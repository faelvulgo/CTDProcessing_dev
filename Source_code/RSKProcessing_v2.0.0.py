#!/usr/bin/env python

import time
from pyrsktools import RSK
import pandas as pd


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

    def rsktocsv(self):
        print('Converting RSK to csv...')
        self.rsk.RSK2CSV(direction='down', outputDir='/home/labdino/PycharmProjects/Internal_waves/dados/Cruzeiro_2/01.BoiadeTopo-75m')


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


def round_dataframe(df):
    """
       Parameters:
       df (pandas.DataFrame): Input DataFrame to be rounded.

       Returns:
       pandas.DataFrame: DataFrame with numerical values rounded to 3 decimals.
    """
    # Make a copy of the DataFrame
    rounded_df = df.copy()

    rounded_df.round(3)

    return rounded_df


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


def main():
    rsk_file_path = "/home/labdino/PycharmProjects/Internal_waves/dados/Cruzeiro_2/01. Boia de Topo - 75m/200428_20200227_2329.rsk"

    processing = Processing(rsk_file_path)

    calculations = Calculations(processing.rsk)

    time_step('Opening file', processing.open_file)
    time_step('Reading data', processing.read_data)

    time_step('Deriving sea pressure', calculations.deriveseapressure)
    time_step('Deriving salinity', calculations.derivesalinity)
    time_step('Deriving depth', calculations.derivedepth)

    # Time despiking step
    time_step('Despiking', processing.despike,
              ['temperature', 'conductivity', 'pressure', 'sea_pressure', 'salinity', 'depth'])

    time_step('Converting', processing.rsktocsv)

    # Specify the CSV file path
    csv_file_path = '/home/labdino/PycharmProjects/Internal_waves/dados/Cruzeiro_2/01.BoiadeTopo-75m/200428_20200227_2329.csv'

    # Read the data from the CSV file
    df = time_step('Reading CSV', pd.read_csv, csv_file_path, skiprows=7)

    # Round the values in the DataFrame
    df = time_step('Rounding values', round_dataframe, df)

    # Save the rounded data back to the same CSV file (overwrite)
    time_step('Saving rounded CSV', df.to_csv, csv_file_path, index=False)

    # Close the file or perform any other final processing step
    time_step('Closing file', processing.close_file)


if __name__ == "__main__":
    main()
