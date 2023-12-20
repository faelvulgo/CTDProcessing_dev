import pandas as pd
import numpy as np


def generate_ctd_file(filename, num_rows):
    # Generate pressure data with random reversals
    pressure = np.random.randint(0, 500, num_rows)
    for i in range(1, num_rows):
        if pressure[i] < pressure[i - 1]:
            pressure[i] = pressure[i - 1] + np.random.randint(1, 5)

    # Generate temperature data with random outliers
    temperature = np.random.normal(20, 5, num_rows)
    temperature[::50] += np.random.normal(15, 10, num_rows // 50)

    # Generate salinity data with random noise
    salinity = np.random.normal(35, 0.5, num_rows)
    salinity += np.random.normal(0, 0.1, num_rows)

    # Generate oxygen data with a linear trend
    oxygen = np.linspace(150, 100, num_rows) + np.random.normal(0, 10, num_rows)

    # Create a DataFrame with the generated data
    data = pd.DataFrame({'pressure': pressure, 'temperature': temperature, 'salinity': salinity, 'oxygen': oxygen})

    # Write the DataFrame to a CSV file
    data.to_csv(filename, index=False)


generate_ctd_file('example_ctd_file.csv', 1000)
