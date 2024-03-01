"""
Pacotes utilizados:
    - Pandas
    - Numpy
    - Scipy
    - Matplotlib
    - Re
    - Time
"""
import pandas as pd
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import re
import gsw
from gsw import rho as gsw_rho

def plot(data, path):
    """
    - Monta um perfil simples de temperatura
    """
    pressure = data['PRESSURE;DBAR']
    temperature = data['TEMPERATURE;C']

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.invert_yaxis()
    ax.plot(temperature, pressure, 'b-', markersize=3)
    ax.set_xlabel('Temperature (°C)')
    ax.set_ylabel('Pressure (dBar)')
    ax.set_title('Perfil de Temperatura')
    ax.grid(True)

    # Inverte o eixo x (temperatura)
    plt.gca().invert_xaxis()

    # Define os intervalos desejados para o eixo x (temperatura)
    temperature_intervals = range(int(min(temperature)), int(max(temperature)) + 1, 2)
    ax.set_xticks(temperature_intervals)

    # Move o eixo X para cima
    ax.xaxis.tick_top()
    ax.xaxis.set_label_coords(0.5, 1.08)

    plt.tight_layout()
    plt.savefig(path, format='png', dpi=900, transparent=False)

    plt.show()

def convert(data):
    """
    Para cada coluna do arquivo, exceto a coluna 'time', substitui ',' por '.', e nas células que tenham o '.' como
    separador de milhar, retira.
    """
    for column in data.columns:
        if column != 'Date / Time' and data[column].dtype == object:
            data[column] = data[column].str.replace(',', '.')
            data[column] = data[column].map(lambda x: re.sub(r'\.(?=.*\.)', '', x))
            data[column] = data[column].astype('float')
    return data  # Return the modified DataFrame

def downcast(data):
    """
    - Identifica o maior valor de pressão e mantém apenas as linhas antes desse valor.
    """
    # Encontra o índice do maior valor de pressão
    idx_max_pressure = data['PRESSURE;DBAR'].idxmax()

    # Atualiza o DataFrame apenas com os dados de downcast
    downcast_data = data.loc[:idx_max_pressure]

    print('A maior pressão encontrada foi: ' + str(data['PRESSURE;DBAR'].iloc[idx_max_pressure]) + ' dBar')

    return downcast_data  # Return the DataFrame with downcast data

def remove_outliers(data):
    """
    - Faz a média dos dados,
    - O desvio padrão,
    - Cria uma máscara que irá conter os valores que forem maiores ou menores que a média mais três desvios-padrão,
    - Retira a máscara dos dados.
    """
    mean = data.mean()
    std = data.std()
    mask = (data > mean + 3 * std) | (data < mean - 3 * std)
    data = data[~mask].dropna()

    print('Média de cada coluna dos dados:' + str(mean))
    print('Desvio padrão de cada coluna dos dados: ' + str(std))
    print('3-sigma para cada coluna de dados: ' + str(mean + 3 * std))

    return data  # Return the DataFrame with outliers removed

def above_sea_level(data, sea_level_pressure):
    """
    - Recebe o argumento 'sea_level_pressure', que deve ser 10.12 dbar
    - Converte a coluna da pressão para 'float',
    - Mantém os valores que sejam maior do que sea_level_pressure
    """
    data['PRESSURE;DBAR'] = data['PRESSURE;DBAR'].astype(float)

    return data[data['PRESSURE;DBAR'] > sea_level_pressure]  # Return filtered DataFrame

def pressure_loops(data):
    """
    Remove as linhas onde ocorrem pressure loops
    """

    # Arredonde os valores de pressão para uma precisão específica (por exemplo, 2 casas decimais)
    data['PRESSURE;DBAR'] = data['PRESSURE;DBAR'].round(2)
    indices_loops = []
    for i in range(1, len(data['PRESSURE;DBAR'])):
        if data['PRESSURE;DBAR'][i] < data['PRESSURE;DBAR'][i - 1]:
            indices_loops.append(i)

    print("Índices de loops de pressão identificados:", indices_loops)

    # Remover linhas onde ocorrem pressure loops
    data_sem_loops = data.drop(indices_loops).reset_index(drop=True)

    print("Tamanho original:", len(data))
    print("Tamanho após remover loops de pressão:", len(data_sem_loops))

    return data_sem_loops  # Return the DataFrame without pressure loops

def lp_filter(self, sample_rate=24.0, time_constant=0.15):
    """
    - Filtro passa-baixa
    - Recebe os valores de sample_rate e time_constant
    """
    wn = (1.0 / time_constant) / (sample_rate * 2.0)
    b, a = signal.butter(2, wn, "low")
    padlen = int(0.3 * sample_rate * time_constant)
    new_df = self.data.copy()
    new_df.index = signal.filtfilt(b, a, self.data.index.values, padtype='constant', padlen=padlen)
    self.data = new_df

def bin_average(data, tamanho_janela, coluna, coluna2, lat):
    """
    :param data: fonte do dado
    :param tamanho_janela: tamanho dos bins
    :param coluna: qual coluna para calcular a média
    :return: retorna um dataframe com os resultados
    """
    # Crie um novo DataFrame para evitar modificar o original
    new_data = data.copy()

    # Inicialize listas para armazenar os resultados
    profundidade = []
    temperature = []
    salinity = []
    pressure = []

    new_data['z'] = gsw.conversions.z_from_p(new_data['PRESSURE;DBAR'], lat)
    new_data['z'] = abs(new_data['z'])

    # Iteração de 'tamanho_janela' em 'tamanho_janela' linhas até o final do DataFrame
    for i in range(0, len(new_data), tamanho_janela):
        # Verifique se o índice é válido para evitar "IndexError"
        if i + tamanho_janela - 1 < len(new_data):
            # Pegue os dados da coluna da janela especificada
            dados_janela = new_data[coluna].iloc[i:i + tamanho_janela]
            dados_janela2 = new_data[coluna2].iloc[i:i + tamanho_janela]

            # Converta os dados para o formato numérico, substituindo ',' por '.'
            dados_janela = dados_janela.astype(str).str.replace(',', '.').astype(float)
            dados_janela2 = dados_janela2.astype(str).str.replace(',', '.').astype(float)

            # Calcule a média dos dados da coluna da janela
            media_dados = np.mean(dados_janela)
            media_final = round(media_dados, 2)
            media_dados2 = np.mean(dados_janela2)
            media_final2 = round(media_dados2, 2)

            # Calcule a média entre o primeiro e o último valor da janela apenas para a coluna da profundidade
            media_primeiro_ultimo = np.mean([new_data['z'].iloc[i], new_data['z'].iloc[i + tamanho_janela - 1]])
            media_primeiro_ultimo_final = round(media_primeiro_ultimo, 2)

            # Adicione os resultados às listas
            profundidade.append(media_primeiro_ultimo_final)
            temperature.append(media_final)
            salinity.append(media_final2)

    # Crie um DataFrame com os resultados
    results_df = pd.DataFrame({
        'z': profundidade,
        'TEMPERATURE;C': temperature,
        'Calc. SALINITY; PSU': salinity,
        'PRESSURE;DBAR': pressure
    })

    return results_df

def plot_perfil_termosal(data, path):

    # Extrair colunas relevantes
    temperatura = data['TEMPERATURE;C']
    salinidade = data['Calc. SALINITY; PSU']
    pressao = data['PRESSURE;DBAR']

    # Criar o gráfico com dois eixos x
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plotar Temperatura no primeiro eixo x e pressão no y
    ax1.set_xlabel('Temperatura', color='tab:blue')
    ax1.set_ylabel('Pressão', color='tab:blue')
    ax1.plot(temperatura, pressao, color='tab:blue', label='Temperatura')
    #ax1.set_xlim([0, 25])
    #ax1.set_ylim([0, 2750])

    # Configurar os parâmetros do eixo x
    ax1.tick_params(axis='x', labelcolor='tab:blue')

    # Criar o segundo eixo x para a Salinidade
    ax2 = ax1.twiny()
    ax2.set_xlabel('Salinidade', color='tab:orange')
    ax2.plot(salinidade, pressao, color='tab:orange', label='Salinidade')
    #ax2.set_xlim([34, 37.5])

    # Configurar os parâmetros do eixo x do segundo gráfico
    ax2.tick_params(axis='x', labelcolor='tab:orange')

    # Inverter o eixo y
    ax1.invert_yaxis()

    # Configurar o título do gráfico
    plt.title('Perfil de Temperatura e Salinidade Bruto - bin 20')

    # Configurar o rótulo do eixo y
    plt.ylabel('Pressão')

    # Ajustar o layout do gráfico
    fig.tight_layout()

    # Adicionar legenda ao gráfico
    fig.legend(loc='upper right', bbox_to_anchor=(1, 1))

    # Salvar o gráfico como imagem PNG
    plt.savefig(path, format='png', dpi=900, transparent=False)

    # Exibir o gráfico
    plt.show()

def diagramats(data, path, lon, lat):
    # Abre os dados do dataframe como array NumPy
    salinity = data['Calc. SALINITY; PSU'].values
    temperature = data['TEMPERATURE;C'].values
    pressure = data['PRESSURE;DBAR'].values

    # Cria uma grade 2D pro diagrama
    T, S = np.meshgrid(temperature, salinity)

    # Calcula a densidade
    sa = gsw.SA_from_SP(salinity, pressure, lon, lat)
    ct = gsw.CT_from_t(sa, temperature, pressure)
    density = gsw_rho(sa, ct, pressure)

    # Cria o diagrama
    fig, ax = plt.subplots()
    norm = plt.Normalize(pressure.min(), pressure.max())
    scatter = ax.scatter(salinity, temperature, c=pressure, cmap='viridis', norm=norm, marker='o',
                         s=20)  # cria o scatterplot com salinidade, temperatura e pressão como espectro de cor

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
    plt.savefig(
        path,
        format='png', dpi=900, transparent=False)

    # Display the plot
    plt.show()