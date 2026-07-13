import time
import pandas as pd
import argparse
import threading
from pyrsktools import RSK
import datetime


class Processing:
    """
    A class to handle processing of RSK files.
    """

    def __init__(self, rsk_file_path):
        """
        Initializes Processing class with an RSK file path.
        """
        self.rsk = RSK(rsk_file_path)

    def open_file(self):
        """
        Opens the RSK file.
        """
        print('Opening file...')
        self.rsk.open()

    def read_data(self):
        """
        Reads data from the RSK file.
        """
        print('Reading data...')
        self.rsk.readdata()

    def close_file(self):
        """
        Closes the RSK file.
        """
        print('Closing file...')
        self.rsk.close()

    def despike(self, channels):
        """
        Despikes specified channels in the RSK file.
        """
        print('Despiking...')
        for channel in channels:
            self.rsk.despike(channels=channel)

    def rsktocsv(self, direction, outputdir):
        """
        Converts RSK file to CSV.
        """
        print('Converting RSK to csv...')
        self.rsk.RSK2CSV(direction=direction, outputDir=outputdir)


class Calculations:
    """
    A class to handle calculations on RSK data.
    """

    def __init__(self, rsk_object):
        """
        Initializes Calculations class with an RSK object.
        """
        self.rsk = rsk_object

    def deriveseapressure(self):
        """
        Derives sea pressure from the RSK data.
        """
        print('Deriving sea pressure...')
        self.rsk.deriveseapressure()

    def derivesalinity(self):
        """
        Derives salinity from the RSK data.
        """
        print('Deriving salinity...')
        self.rsk.derivesalinity()

    def derivedepth(self):
        """
        Derives depth from the RSK data.
        """
        print('Deriving depth...')
        self.rsk.derivedepth()

    def derivedensity(self):
        """
        Derive density from the RSK data.
        """
        print('Deriving density...')
        self.rsk.derivesigma()

    @staticmethod
    def round_dataframe(df):
        """
        Rounds the numerical values in a DataFrame to 3 decimal places,
        including the first column and adding the first row back as the header.
        """
        print('Rounding numerical values...')

        first_column = df.iloc[:, 0]
        first_row = df.iloc[0]

        # Exclude the first column and the first row from the DataFrame
        numeric_columns = df.drop(first_column)  # Exclude the first column
        data_rows = df.drop(first_row)  # Exclude the first row

        # Convert numerical DataFrame to float separately
        numeric_df = data_rows.astype(float)

        # Round numerical DataFrame
        rounded_df = numeric_df.round(3)

        # Include the first column back in the rounded DataFrame
        rounded_df.insert(0, df.columns[0], first_column)
        rounded_df = pd.concat([first_row, rounded_df])

        return rounded_df


class Utilities:
    """
    A class to handle utility functions.
    """

    def __init__(self):
        self.stop_animation = False  # Flag to signal animation thread to stop

    @staticmethod
    def time_step(step_name, func, *args, **kwargs):
        """
        Times the execution of a given function.
        """
        start_time = datetime.datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.datetime.now()
        elapsed_time = end_time - start_time
        print(f"Time taken for {step_name}: {elapsed_time}, Finished at: {end_time.strftime('%I:%M %p')}")
        return result

    def animate_loading(self):
        """
        Function to animate loading.
        """
        while not self.stop_animation:  # Check flag to continue animation
            for char in '|/-\\':
                print(' Processing ' + char, end='\r')
                time.sleep(0.1)
        print('\nProcessing complete.')  # Print completion message when animation stops

    def stop_animation_thread(self):
        """
        Function to stop the animation thread.
        """
        self.stop_animation = True


def main(rsk_file_path, csv_file_path, outputdir):
    """
    Main function to process RSK data and round CSV values.
    """
    # Call the classes
    processing = Processing(rsk_file_path)
    calculations = Calculations(processing.rsk)
    utilities = Utilities()

    # Animate loading
    loading_thread = threading.Thread(target=utilities.animate_loading)
    loading_thread.start()

    # Time and execute the open and read function
    utilities.time_step('Opening file', processing.open_file)
    utilities.time_step('Reading data', processing.read_data)
    
    # Time and execute the calculations steps
    utilities.time_step('Deriving sea pressure', calculations.deriveseapressure)
    utilities.time_step('Deriving salinity', calculations.derivesalinity)
    utilities.time_step('Deriving depth', calculations.derivedepth)
    utilities.time_step('Deriving density', calculations.derivedensity())
    
    # Time and execute the despiking steps
    utilities.time_step('Despiking', processing.despike,
                        ['temperature'])

    # Convert the RSK file to a csv file
    utilities.time_step('Converting', processing.rsktocsv, 'down', outputdir)

    # Read the data from the CSV file
    df = Utilities.time_step('Reading CSV', pd.read_csv, csv_file_path, skiprows=8, header=None)

    # Round the values in the DataFrame
    df = calculations.round_dataframe(df)

    # Save the rounded data back to the same CSV file (overwrite)
    Utilities.time_step('Saving rounded CSV', df.to_csv, csv_file_path, index=False)

    # Close the file or perform any other final processing step
    utilities.time_step('Closing file', processing.close_file)

    # Stop animation
    utilities.stop_animation_thread()  # Signal animation thread to stop
    loading_thread.join()  # Wait for animation thread to stop


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process RSK data and round CSV values.')
    parser.add_argument('rsk_file_path', type=str, help='Path to the RSK file')
    parser.add_argument('outputdir', type=str, help='Output directory for the converted CSV file')
    parser.add_argument('csv_file_path', type=str, help='Path to the CSV file')

    args = parser.parse_args()

    main(args.rsk_file_path, args.csv_file_path, args.outputdir)
