import matplotlib.pyplot as plt
import pandas as pd
from gsw import *
import numpy as np
from gsw import rho as gsw_rho

# Abre os dados do csv como um dataframe Pandas
data = pd.read_csv('PATH')

# Abre os dados do dataframe como array NumPy
salinity = data['Calc. SALINITY; PSU'].values
temperature = data['TEMPERATURE;C'].values
pressure = data['PRESSURE;DBAR'].values

# Cria uma grade 2D pro diagrama
T, S = np.meshgrid(temperature, salinity)

# Calcula a densidade
sa = SA_from_SP(salinity, pressure, 39, 22)
ct = CT_from_t(sa, temperature, pressure)
density = gsw_rho(sa, ct, pressure)

# Cria o diagrama
fig, ax = plt.subplots()
norm = plt.Normalize(pressure.min(), pressure.max())
scatter = ax.scatter(salinity, temperature, c=pressure, cmap='viridis', norm=norm, marker='o', s=20)    # cria o scatterplot com salinidade, temperatura e pressão como espectro de cor

# Reshape dos arrays pras isolinhas de densidade
salinity_reshaped = np.linspace(salinity.min(), salinity.max(), 100)
temperature_reshaped = np.linspace(temperature.min(), temperature.max(), 100)

# Cria a grade com os arrays reshaped
salinity_grid, temperature_grid = np.meshgrid(salinity_reshaped, temperature_reshaped)
density_grid = gsw_rho(salinity_grid, temperature_grid, np.zeros_like(salinity_grid))

# Cria as isolinhas de densidade e adiciona os valores de densidade de cada isolinha
contour = ax.contour(salinity_grid, temperature_grid, density_grid, colors='black')
contour_labels = ax.clabel(contour, inline=True, fontsize=8, fmt='%.1f')

# Define as legendas e título do diagrama
ax.set_xlabel('Salinidade (PSU)')
ax.set_ylabel('Temperatura ($^\circ$C)')
ax.set_title('Diagrama T-S Radial 3 - 0656')

# Seta o limite do plot para o centro do diagrama
ax.set_xlim(salinity.min() - 0.05, salinity.max() + 0.05)
ax.set_ylim(temperature.min() - 0.5, temperature.max() + 0.5)

# Adiciona a barra de cores da pressão
cbar = plt.colorbar(scatter, ax=ax, label='Pressão (dBar)')

plt.tight_layout()

# Save the plot
plt.savefig('PATH', format='png', dpi=900, transparent=False)

# Display the plot
plt.show()
