import time
from pyrsktools import RSK
import pandas as pd


# Function to time each step
def time_step(step_name, func, *args, **kwargs):
    start_time = time.time()
    func(*args, **kwargs)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken for {step_name}: {elapsed_time:.2f} seconds")


rsk = RSK("/home/labdino/PycharmProjects/Internal_waves/dados/Cruzeiro_2/01. Boia de Topo - 75m/200428_20200227_2329.rsk")

print('Opening file...')
time_step('Opening file', rsk.open)

print('Reading data...')
time_step('Reading data', rsk.readdata)

print('Saving to csv...')
output_csv_path = '/home/labdino/PycharmProjects/Internal_waves/dados/Cruzeiro_2/01. Boia de Topo - 75m/'
time_step('Saving to csv', rsk.RSK2CSV, outputDir=output_csv_path)


print('Closing file...')
time_step('Closing file', rsk.close)
