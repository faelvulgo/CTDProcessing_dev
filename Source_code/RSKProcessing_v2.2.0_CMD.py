import time
import pandas as pd
import argparse
import threading
from pyrsktools import RSK


class Processing:
    """A class to handle processing of RSK files."""

    def __init__(self, rsk_file_path):
        """
        Initializes Processing class with an RSK file path.

        Parameters:
        - rsk_file_path (str): Path to the RSK file.
        """
        self.rsk = RSK(rsk_file_path)

    def open_file(self):
        """Opens the RSK file."""
        print('Opening file...')
        self.rsk.open()

    def read_data(self):
        """Reads data from the RSK file."""
        print('Reading data...')
        self.rsk.readdata()

    def close_file(self):
        """Closes the RSK file."""
        print('Closing file...')
        self.rsk.close()

    def despike(self, channels):
        """
        Despikes specified channels in the RSK file.

        Parameters:
        - channels (list): List of channel names to despike.
        """
        print('Despiking...')
        for channel in channels:
            self.rsk.despike(channels=channel)

    def rsktocsv(self, direction, outputdir):
        """
        Converts RSK file to CSV.

        Parameters:
        - direction (str): Direction of the conversion.
        - outputdir (str): Output directory for the converted CSV file.
        """
        print('Converting RSK to csv...')
        self.rsk.RSK2CSV(direction=direction, outputDir=outputdir)


class Calculations:
    """A class to handle calculations on RSK data."""

    def __init__(self, rsk_object):
        """
        Initializes Calculations class with an RSK object.

        Parameters:
        - rsk_object: RSK object to perform calculations on.
        """
        self.rsk = rsk_object

    def deriveseapressure(self):
        """Derives sea pressure from the RSK data."""
        print('Deriving sea pressure...')
        self.rsk.deriveseapressure()

    def derivesalinity(self):
        """Derives salinity from the RSK data."""
        print('Deriving salinity...')
        self.rsk.derivesalinity()

    def derivedepth(self):
        """Derives depth from the RSK data."""
        print('Deriving depth...')
        self.rsk.derivedepth()

    def round_dataframe(self, df):
        """
        Rounds the numerical values in a DataFrame to 3 decimal places,
        including the first column and adding the first row back as the header.

        Parameters:
        - df (DataFrame): DataFrame containing numerical values to be rounded.

        Returns:
        - rounded_df (DataFrame): DataFrame with rounded numerical values.
        """
        print('Rounding numerical values...')

        first_column = df.iloc[:, 0]
        first_row = df.iloc[0]

        # Exclude the first column and the first row from the DataFrame
        numeric_columns = df.iloc[:, 1:]  # Exclude the first column
        data_rows = df.iloc[1:]  # Exclude the first row

        # Convert numerical DataFrame to float
        numeric_df = data_rows and numeric_columns.astype(float)

        # Round numerical DataFrame
        rounded_df = numeric_df.round(3)

        # Include the first column back in the rounded DataFrame
        rounded_df.insert(0, first_column, axis=1)
        rounded_df.insert(0, first_row, axis=0)

        return rounded_df


class Utilities:
    """A class to handle utility functions."""

    @staticmethod
    def time_step(step_name, func, *args, **kwargs):
        """
        Times the execution of a given function.

        Parameters:
        - step_name (str): Name of the step.
        - func (function): Function to be executed.
        - *args: Variable length argument list for the function.
        - **kwargs: Arbitrary keyword arguments for the function.

        Returns:
        - result: Result returned by the function.
        """
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Time taken for {step_name}: {elapsed_time:.2f} seconds")
        return result

    @staticmethod
    def animate_loading():
        """Function to animate loading."""
        while True:
            for char in '|/-\\':
                print('Processing ' + char, end='\r')
                time.sleep(0.1)


def main(rsk_file_path, csv_file_path, outputdir):
    """
    Main function to process RSK data and round CSV values.

    Parameters:
    - rsk_file_path (str): Path to the RSK file.
    - csv_file_path (str): Path to the CSV file.
    - outputdir (str): Output directory for the converted CSV file.
    """
    # Call the classes
    processing = Processing(rsk_file_path)
    calculations = Calculations(processing.rsk)

    # Animate loading
    loading_thread = threading.Thread(target=Utilities.animate_loading)
    loading_thread.start()

    # Time and execute the open and read function
    Utilities.time_step('Opening file', processing.open_file)
    Utilities.time_step('Reading data', processing.read_data)
    '''
    # Time and execute the calculations steps
    Utilities.time_step('Deriving sea pressure', calculations.deriveseapressure)
    Utilities.time_step('Deriving salinity', calculations.derivesalinity)
    Utilities.time_step('Deriving depth', calculations.derivedepth)
    '''
    # Time and execute the despiking steps
    Utilities.time_step('Despiking', processing.despike,
                        ['temperature', 'salinity', 'sea_pressure', 'pressure'])

    # Convert the RSK file to a csv file
    Utilities.time_step('Converting', processing.rsktocsv, 'down', outputdir)
    '''
    # Read the data from the CSV file
    df = Utilities.time_step('Reading CSV', pd.read_csv, csv_file_path, skiprows=7)
    
    # Round the values in the DataFrame
    df = calculations.round_dataframe(df)

    # Save the rounded data back to the same CSV file (overwrite)
    Utilities.time_step('Saving rounded CSV', df.to_csv, csv_file_path, index=False)
    '''
    # Close the file or perform any other final processing step
    Utilities.time_step('Closing file', processing.close_file)

    # Stop animation
    loading_thread.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process RSK data and round CSV values.')
    parser.add_argument('rsk_file_path', type=str, help='Path to the RSK file')
    parser.add_argument('outputdir', type=str, help='Output directory for the converted CSV file')
    parser.add_argument('csv_file_path', type=str, help='Path to the CSV file')

    args = parser.parse_args()

    main(args.rsk_file_path, args.csv_file_path, args.outputdir)
