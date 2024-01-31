import pandas as pd
import numpy as np
from scipy import signal
from scipy.signal import butter, filtfilt, lfilter
import matplotlib.pyplot as plt
import re


# function to replace the ',' to '.' as the decimal separator but differentiating the '.' used for the thousand separator
def convert_decimal_separator_all_columns(data):
    for column in data.columns:
        if column != 'time' and data[column].dtype == object:
            data[column] = data[column].str.replace(',', '.')
            data[column] = data[column].map(lambda x: re.sub(r'\.(?=.*\.)', '', x))
            data[column] = data[column].astype('float')
    return data


# function to separate upcast and downcast, returns a tuple (DEVELOPING)
def separate_upcast_downcast(data):
    # Find the index where the pressure values start to decrease
    pressure_diff = df['pressure'].diff()
    change_index = pressure_diff.idxmax()

    # Separate the upcast and downcast sections
    upcast = df.iloc[:change_index]
    downcast = df.iloc[change_index:]
    return upcast, downcast


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


# define a function for a low pass filter to smooth the data (WORKING)
def lp_filter(df, sample_rate=24.0, time_constant=0.15):
    # Butter is closer to what SBE is doing with their cosine filter.
    wn = (1.0 / time_constant) / (sample_rate * 2.0)
    b, a = signal.butter(2, wn, "low")
    padlen = int(0.3 * sample_rate * time_constant)
    new_df = df.copy()
    new_df.index = signal.filtfilt(b, a, df.index.values, padtype='constant', padlen=padlen)
    return new_df


def plot_ts_diagram(data):
    # Extract the columns
    pressure = data['pressure']
    temperature = data['temperature']
    salinity = data['salinity']
    oxygen = data['oxygen']

    # Create the plot
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.invert_yaxis()
    ax.plot(salinity, temperature, '-o', markersize=3)
    ax.set_xlabel('Salinity')
    ax.set_ylabel('Temperature (°C)')
    ax.set_title('Temperature-Salinity Diagram')
    ax.grid(True)
    plot = plt.show()
    return plot


# read CTD data from CSV file using tab as delimiter
data = pd.read_csv('/home/labdino/PycharmProjects/CTDprocessing/venv/FILE17V2.csv', delimiter='\t')
print(data.columns)

# Assuming you have a DataFrame named 'data'
data2 = convert_decimal_separator_all_columns(data)

# use upcast or downcast
#downcast = separate_upcast_downcast(data)

# remove outliers of the binned data
outlier_removed_data = remove_outliers(data2)

# remove data above sea-water level
sea_level_removed_data = remove_above_sea_level(outlier_removed_data, 1012.0)

# remove pressure reversals
removed_reversals = remove_pressure_reversals(sea_level_removed_data)

# low-pass filter
filtered_data = lp_filter(removed_reversals, sample_rate=24.0, time_constant=0.15)

# Plot a T-S diagram of the processed and unprocessed data
plot = plot_ts_diagram(removed_reversals)
plot2 = plot_ts_diagram(data)

# define processed_data to be converted to a new csv file
processed_data = removed_reversals

# Save the data to a file
processed_data.to_csv("/home/labdino/PycharmProjects/CTDprocessing/venv/processed_data.csv", index=False)

