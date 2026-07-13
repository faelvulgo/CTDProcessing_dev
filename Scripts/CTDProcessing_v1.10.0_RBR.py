import pandas as pd
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import re
import time
import gsw


class Plotter:
    """
    Plotters class with a function that makes a temperature over time plot.
    """
    def __init__(self, data):
        self.data = data

    def plot(self):
        """
        Builds a temperature over time plot.
        """
        day = self.data['Date']
        temperature = self.data['temperature(°C)']

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.invert_yaxis()
        ax.plot(day, temperature, 'b-', markersize=3)
        ax.set_xlabel('Day')
        ax.set_ylabel('Temperature(°C)')
        ax.set_title('Temperature Series')
        ax.grid(True)

        # Set x-axis limits
        ax.set_xlim(min(day), max(day))

        # Invert the x-axis (temperature)
        plt.gca().invert_xaxis()

        # Define desired intervals for the x-axis (temperature)
        temperature_intervals = range(int(min(temperature)), int(max(temperature)) + 1, 2)
        ax.set_xticks(temperature_intervals)

        # Move the X-axis to the top
        ax.xaxis.tick_top()
        ax.xaxis.set_label_coords(0.5, 1.08)

        plt.tight_layout()
        plt.savefig('/home/labdino/PycharmProjects/Internal_waves/dados/Cruzeiro_2/01. Boia de Topo - 75m/75m_plot.png',
                    format='png', dpi=900, transparent=False)

        plt.show()


class Processing:
    """
    Data processor class:
    With Functions: - convert_decimal_separator_all_columns: converts the decimal separator;
                 - remove_outliers: removes spikes using the 3-sigma method;
                 - remove_above_sea_level: removes data measured above sea level (10.12 dbar);
                 - remove_pressure_reversals: removes pressure reversals;
                 - lp_filter: low-pass filter;
                 - plot_ts_diagram: plots the simplified T-S diagram;
                 - process_data: executes all the above functions, timing how long each one takes to complete.
    """

    def __init__(self, data):
        self.data = data

    def convert_date_time(self):
        """
        Converts the 'Date / Time' column to datetime
        Creates separate columns for 'Date' and 'Time'
        """
        self.data['timestamp(yyyy-mm-ddTHH:MM:ss.FFF)'] = pd.to_datetime(
            self.data['timestamp(yyyy-mm-ddTHH:MM:ss.FFF)'], format='%Y-%m-%dT%H:%M:%S.%f')
        self.data['Date'] = self.data['timestamp(yyyy-mm-ddTHH:MM:ss.FFF)'].dt.date
        self.data['Time'] = self.data['timestamp(yyyy-mm-ddTHH:MM:ss.FFF)'].dt.time

        return self.data  # Return the modified DataFrame

    def convert(self):
        """
        For each column in the file, except the 'Date' and 'Time' columns, replaces ',' with '.', and in cells with '.'
        as a thousand separator, removes it.
        """
        for column in self.data.columns:
            if column not in ['Date', 'Time']:
                # Check if the column is of object type before using .str accessor
                if self.data[column].dtype == 'O':
                    self.data[column] = self.data[column].str.replace(',', '.')
                    self.data[column] = self.data[column].apply(lambda x: re.sub(r'\.(?=.*\.)', '', str(x)) if isinstance(x, str) else x)
                    self.data[column] = self.data[column].astype('float')

        return self.data  # Return the modified DataFrame

    def downcast(self):
        """
        Identifies the highest pressure value and keeps only the rows before that value.
        """
        # Find the index of the highest pressure value
        idx_max_pressure = self.data['pressure(dbar)'].idxmax()

        # Update the DataFrame only with downcast data
        downcast_data = self.data.loc[:idx_max_pressure]

        print('The highest pressure found was: ' + str(self.data['pressure(dbar)'].iloc[idx_max_pressure]) + ' dBar')

        # Update the DataFrame only with downcast data
        self.data = downcast_data

        return self.data  # Return the modified DataFrame

    def remove_outliers(self):
        """
        Calculate the mean and standard deviation for each column
        Create a mask to identify outliers based on mean and standard deviation
        Remove outliers from the DataFrame
        """
        # Select numeric columns only
        numeric_data = self.data.select_dtypes(include=np.number)

        # Calculate the mean and standard deviation for each numeric column
        mean = numeric_data.mean()
        std = numeric_data.std()

        # Create a mask for each column separately
        mask_positive = numeric_data > (mean + (3 * std))
        mask_negative = numeric_data < (mean - (3 * std))

        # Combine masks using logical OR to detect outliers
        mask = mask_positive | mask_negative

        # Combine masks using any to detect outliers in any column
        mask_any = mask.any(axis=1)

        # Remove rows where any column is an outlier
        self.data = self.data[~mask_any]

        removed_data = processed_data[processed_data.index.isin(processed_data.index[~mask_any])]
        print(removed_data)
        removed = removed_data.to_csv('/home/labdino/PycharmProjects/Internal_waves/dados/Cruzeiro_2/01. Boia de Topo - 75m/removed.csv')

        print(mask)
        print('2-sigma for each column:', mean + (3 * std))
        print('2-sigma for each column:', mean - (3 * std))

        return self.data  # Return the modified DataFrame

    def above_sea_level(self, sea_level_pressure):
        """
        Receives the 'sea_level_pressure' argument, which should be 10.12 dbar
        Converts the pressure column to 'float',
        Keeps the values that are greater than sea_level_pressure
        """
        self.data['pressure(dbar)'] = self.data['pressure(dbar)'].astype(float)
        self.data = self.data[self.data['pressure(dbar)'] > sea_level_pressure]

        return self.data  # Return the modified DataFrame

    @staticmethod
    def pressure_loops(data):
        """
        Remove rows where pressure loops occur
        """

        # Round pressure values to a specific precision (e.g., 2 decimal places)
        data['pressure(dbar)'] = data['pressure(dbar)'].round(2)
        indices_loops = []
        for i in range(1, len(data['pressure(dbar)'])):
            if data['pressure(dbar)'][i] < data['pressure(dbar)'][i - 1]:
                indices_loops.append(i)

        #print("Pressure loop indices identified:", indices_loops)

        # Remove rows where pressure loops occur
        data_no_loops = data.drop(indices_loops).reset_index(drop=True)

        print("Original size:", len(data))
        print("Size after removing pressure loops:", len(data_no_loops))

        return data_no_loops  # Return the modified DataFrame

    def lp_filter(self, sample_rate=24.0, time_constant=0.15):
        """
        Low-pass filter
        Receives the sample_rate and time_constant values
        """
        wn = (1.0 / time_constant) / (sample_rate * 2.0)
        b, a = signal.butter(2, wn, "low")
        padlen = int(0.3 * sample_rate * time_constant)
        new_df = self.data.copy()
        new_df.index = signal.filtfilt(b, a, self.data.index.values, padtype='constant', padlen=padlen)
        self.data = new_df

        return self.data  # Return the modified DataFrame

    @staticmethod
    def bin_average(data, window_size, column, column2, lat):
        """
        Organize data in average bins.
        """
        # Initialize lists to store the results
        depth = []
        pressure = []
        temperature = []
        salinity = []
        time_bin_avg = []

        # Use .loc to ensure you are modifying the original DataFrame
        data.loc[:, 'depth(m)'] = gsw.conversions.z_from_p(data['pressure(dbar)'], lat)
        data.loc[:, 'depth(m)'] = abs(data['depth(m)'])

        # Iterate over 'window_size' in 'window_size' rows until the end of the DataFrame
        for i in range(0, len(data), window_size):
            # Check if the index is valid to avoid "IndexError"
            if i + window_size - 1 < len(data):
                # Get the data from the specified column window
                window_data = data[column].iloc[i:i + window_size]
                window_data2 = data[column2].iloc[i:i + window_size]
                window_data3 = data['pressure(dbar)'].iloc[i:i + window_size]  # Pressure column
                window_data_time = data['Time'].iloc[i:i + window_size]  # Time column

                # Convert the data to numeric format, replacing ',' with '.'
                window_data = window_data.astype(str).str.replace(',', '.').astype(float)
                window_data2 = window_data2.astype(str).str.replace(',', '.').astype(float)
                window_data3 = window_data3.astype(float)

                # Calculate the average of the window columns data
                data_mean = np.mean(window_data)
                final_mean = round(data_mean, 2)
                data_mean2 = np.mean(window_data2)
                final_mean2 = round(data_mean2, 2)

                # Calculate the average between the first and last value of the window only for the depth column
                mean_first_last = np.mean(
                    [data['depth(m)'].iloc[i], data['depth(m)'].iloc[i + window_size - 1]])
                final_first_last_mean = round(mean_first_last, 2)

                # Add the results to the lists
                depth.append(final_first_last_mean)
                pressure.append(window_data3.iloc[0])  # Include pressure value
                temperature.append(final_mean)
                salinity.append(final_mean2)

                # Calculate average time in seconds
                time_bin_avg.append(np.mean([t.hour * 3600 + t.minute * 60 + t.second for t in window_data_time]))

        # Create a DataFrame with the results
        results_df = pd.DataFrame({
            'depth(m)': depth,
            'temperature(°C)': temperature,
            'salinity(PSU)': salinity,
            'pressure(dbar)': pressure,
            'Time': time_bin_avg
        })

        return results_df


def seconds_to_hms(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"



"""
Running the functions
"""
print('Reading data...')
data = pd.read_csv('/home/labdino/PycharmProjects/Internal_waves/dados/Cruzeiro_2/01. Boia de Topo - 75m/200428_20200227_2329.csv', index_col=False)
data.columns = data.columns.str.strip()
print(data.columns)

# Create an instance of the Processing class, passing your data to the constructor
processor = Processing(data)

# Call each method sequentially
print('Converting date and time...')
processed_data = processor.convert_date_time()  # Requires no argument
print('Converting separators...')
processed_data = processor.convert()  # Requires no argument
print(len(processed_data))
print('Removing Outliers...')
processed_data = processor.remove_outliers()  # Requires no argument
print(len(processed_data))
print('Removing data above sea level...')
processed_data = processor.above_sea_level(sea_level_pressure=10.12)  # Pass the sea level pressure value
print('Finished processing.')

# Save processed data to a CSV file
processed_data.to_csv('/home/labdino/PycharmProjects/Internal_waves/dados/Cruzeiro_2/01. Boia de Topo - 75m/75m_processado.csv', index=False)
