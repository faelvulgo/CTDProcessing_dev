import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt

# function to bin the data in bins of five rows
def bin_data(data):
    binned_data = pd.DataFrame(columns=data.columns)
    for i in range(0, len(data), 5):
        start = i
        end = min(i+5, len(data))
        bin = data.iloc[start:end].mean()
        binned_data = pd.concat([binned_data, bin], ignore_index=True)
    return binned_data

# function to remove outliers using the 3 sigma method
def remove_outliers(data):
    mean = data.mean()
    std = data.std()
    mask = (data > mean + 3 * std) | (data < mean - 3 * std)
    return data[~mask].dropna()

# function to remove data above sea water level
def remove_above_sea_level(data, sea_level_pressure):
    return data[data['pressure'] >= sea_level_pressure]

# function to apply low pass filter and smooth the data
def low_pass_filter(data, fs, cutoff, order=5, padlen=10):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    filtered_data = filtfilt(b, a, data, padlen=padlen)
    return filtered_data

# read CTD data from CSV file using tab as delimiter
data = pd.read_csv('/home/labdino/dados_exemplo_gpt', delimiter=',')

# bin the data
#binned_data = bin_data(data)

# remove outliers of the binned data
outlier_removed_data = remove_outliers(data)

# remove data above sea water level
sea_level_removed_data = remove_above_sea_level(outlier_removed_data, 1012.0)

# apply low pass filter to smooth the data
#fs = 24
#cutoff = 0.15
#for col in sea_level_removed_data.columns:
#    sea_level_removed_data[col] = low_pass_filter(sea_level_removed_data[col], fs, cutoff)

processed_data = sea_level_removed_data

# Save the data to a file
processed_data.to_csv("/home/labdino/PycharmProjects/CTDprocessing/venv/processed_data.csv", index=False)
