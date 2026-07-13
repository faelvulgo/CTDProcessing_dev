#!/usr/bin/env python

import time
from pyrsktools import RSK
import pandas as pd


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
        numeric_df = df.drop([df.columns[0]], axis=1).drop([df.index[0]])

        # Convert numerical DataFrame to float separately
        numeric_df = numeric_df.astype(float)

        # Round numerical DataFrame
        rounded_df = numeric_df.round(3)

        # Include the first column back in the rounded DataFrame
        rounded_df.insert(0, df.columns[0], first_column)

        # Concatenate with the first row
        rounded_df = pd.concat([first_row, rounded_df])

        return rounded_df


def time_step(step_name, func, *args, **kwargs):
    """
    Times the execution of a given function.
    """
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken for {step_name}: {elapsed_time:.2f} seconds")
    return result


def main():
    rsk_file_path = "PATH"

    processing = Processing(rsk_file_path)
    calculations = Calculations(processing.rsk)

    time_step('Opening file', processing.open_file)
    time_step('Reading data', processing.read_data)

    time_step('Deriving sea pressure', calculations.deriveseapressure)
    time_step('Deriving salinity', calculations.derivesalinity)
    time_step('Deriving depth', calculations.derivedepth)
    time_step('Despiking', processing.despike,
              ['temperature', 'conductivity', 'pressure', 'sea_pressure', 'salinity', 'depth'])

    outputdir = 'PATH'
    # Convert the RSK file to a csv file
    time_step('Converting', processing.rsktocsv, 'down', outputdir)

    # Specify the CSV file path
    csv_file_path = 'PATH'

    # Read the data from the CSV file
    print('Reading csv...')
    df = time_step('Reading CSV', pd.read_csv, csv_file_path, skiprows=10, header=None)

    # Round the values in the DataFrame
    df = time_step('Rounding values', calculations.round_dataframe, df)

    # Save the rounded data back to the same CSV file (overwrite)
    time_step('Saving rounded CSV', df.to_csv, csv_file_path, index=False, header=True)

    # Close the file or perform any other final processing step
    time_step('Closing file', processing.close_file)


if __name__ == "__main__":
    main()
