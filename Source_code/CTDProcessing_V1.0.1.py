import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt


# function to remove outliers using the 3 sigma method (WORKING)
def remove_outliers(data):
    mean = data.mean()
    std = data.std()
    mask = (data > mean + 3 * std) | (data < mean - 3 * std)
    return data[~mask].dropna()


# function to remove data above sea-water level (WORKING)
def remove_above_sea_level(data, sea_level_pressure):
    data['pressure'] = data['pressure'].astype(float)  # convert pressure column to float
    return data[data['pressure'] > sea_level_pressure]


# function to remove pressure reversals from the data (WORKING)
def remove_pressure_reversals(data):
    ctd_df = data
    pressure_diff = ctd_df['pressure'].diff()
    ctd_df = ctd_df[pressure_diff >= 0]
    return ctd_df


# read CTD data from CSV file using tab as delimiter
data = pd.read_csv('/home/labdino/PycharmProjects/CTDprocessing/venv/FILE17V2.csv', delimiter='\t', decimal='.')

# remove outliers of the binned data
outlier_removed_data = remove_outliers(data)

# remove data above sea-water level
sea_level_removed_data = remove_above_sea_level(outlier_removed_data, 1012.0)

# remove pressure reversals
removed_reversals = remove_pressure_reversals(sea_level_removed_data)

# define processed_data to be converted to a new csv file
processed_data = removed_reversals

# Save the data to a file
processed_data.to_csv("/home/labdino/PycharmProjects/CTDprocessing/venv/processed_data.csv", index=False)

