<h1 align="center"> CTD Processing </h1>

![Development Badge](http://img.shields.io/static/v1?label=Version&message=v.1.10.0&color=GREEN&style=for-the-badge)

# Description
This project was developed by Rafael S. Bittencourt as an undergraduate research project for the Ocean Dynamics Laboratory.
The goal of this project is a Python module for CTD data pre-processing.

# Features
The module includes several functions to pre-process CTD data:
 - Normalize data separators;
 - Separate the CTD downcast;
 - Remove spikes using the 3-sigma method;
 - Remove pressure loops;
 - Remove data measured above the water column;
 - Data binning;
 - T-S diagram;
 - Overlaid temperature and salinity profiles.

# Module Access
To install the package:
```pip install CTDProcessingPackage```

To use the routine, you only need to import `ctdmodule`: 
```python
import ctdmodule as ctd
```
The pressure, temperature, and salinity columns must be named respectively as: `PRESSURE;DBAR` , `TEMPERATURE;C` , `Calc. SALINITY; PSU` 

# Examples
Here is an example of a CTD data file without any kind of pre-processing:

![Raw data profile](https://github.com/faelvulgo/CTDprocessing/blob/master/perfis/Perfil_bruto.png)

Several noises and pressure loops can be observed, as well as unwanted data above the water column. After processing using the routine, this is the result generated for the same data file:

![Profile after all processing steps](https://github.com/faelvulgo/CTDprocessing/blob/master/perfis/Perfil_binado.png)

# Jupyter Notebook Quick Start Guide
To access a quick guide for the functions, a Jupyter Notebook is available in the repository.

## License

This project is proprietary software. You are welcome to download and use the code strictly for **personal and private purposes**. 

However, commercial use, modification for public distribution, and direct redistribution of the source code are **strictly prohibited**. Any sharing must be done by linking directly to this original repository.

For full legal terms, please refer to the [LICENSE](https://github.com/faelvulgo/CTDProcessing_dev/blob/master/LICENSE.txt) file.
