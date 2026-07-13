import pandas as pd
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import re
import time
import gsw


def plot(data):
    """
    Monta um peril de temperatura.
    """
    pressure = data['PRESSURE;DBAR']
    temperature = data['TEMPERATURE;C']

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.invert_yaxis()
    ax.plot(temperature, pressure, 'b-', markersize=3)
    ax.set_xlabel('Temperature (°C)')
    ax.set_ylabel('Pressure (dBar)')
    ax.set_title('Perfil de Temperatura Bruto')
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
    plt.savefig('path', format='png', dpi=900, transparent=False)

    plt.show()

class DataProcessor:
    """
    Classe do processador dos dados:

    Utiliza o argumento data que vai ser o arquivo para o processamento.
    Funções: - convert_decimal_separator_all_columns: converte o separador decimal;
               - remove_outliers: retira os spikes utilizando o método 3-sigma;
               - remove_above_sea_level: retira os dados medidos acima da coluna d'água (10.12 dbar);
               - remove_pressure_reversals: retira as reversões de pressão;
               - lp_filter: filtro passa-baixa;
               - plot_ts_diagram: plota o diagrama T-S simplificado;
               - process_data: executa todas as funções acima cronometrando quanto tempo cada uma levou para concluir.
    """

    def __init__(self, data):
        self.data = data

    def convert_date_time(self):
        """
        - Converte a coluna 'Date / Time' para datetime
        - Cria colunas separadas para 'Date' e 'Time'
        """
        self.data['Date / Time'] = pd.to_datetime(self.data['Date / Time'], format='%d/%m/%Y %H:%M:%S')
        self.data['Date'] = self.data['Date / Time'].dt.date
        self.data['Time'] = self.data['Date / Time'].dt.time

    def convert(self):
        """
        Para cada coluna do arquivo, exceto as colunas 'Date' e 'Time', substitui ',' por '.', e nas células que tenham o '.' como
        separador de milhar, retira.
        """
        for column in self.data.columns:
            if column not in ['Date', 'Time']:
                # Check if the column is of object type before using .str accessor
                if self.data[column].dtype == 'O':
                    self.data[column] = self.data[column].str.replace(',', '.')
                    self.data[column] = self.data[column].map(lambda x: re.sub(r'\.(?=.*\.)', '', x))
                    self.data[column] = self.data[column].astype('float')

    def downcast(self):
        """
        Identifica o maior valor de pressão e mantém apenas as linhas antes desse valor.
        """
        # Encontra o índice do maior valor de pressão
        idx_max_pressure = self.data['PRESSURE;DBAR'].idxmax()

        # Atualiza o DataFrame apenas com os dados de downcast
        downcast_data = self.data.loc[:idx_max_pressure]

        print('A maior pressão encontrada foi: ' + str(self.data['PRESSURE;DBAR'].iloc[idx_max_pressure]) + ' dBar')

        # Atualiza o DataFrame apenas com os dados de downcast
        self.data = downcast_data

    def remove_outliers(self):
        """
        Calcula a média e o desvio padrão de cada coluna
        Cria uma máscara para identificar outliers baseado na média e no desvio padrão
        Remove outliers do DataFrame
        """
        # Seleciona apenas as colunas numéricas
        numeric_data = self.data.select_dtypes(include=np.number)

        # Calculate a média e o desvio apdrão para cada coluna numérica
        mean = numeric_data.mean()
        std = numeric_data.std()

        # Cria uma máscara para cada coluna
        mask_positive = numeric_data > (mean + (3 * std))
        mask_negative = numeric_data < (mean - (3 * std))

        # Combina as máscaras
        mask = mask_positive | mask_negative

        # Combina máscaras para detectar outliers em qualquer coluna
        mask_any = mask.any(axis=1)

        # Remove a linha onde há um outlier
        self.data = self.data[~mask_any]

        print(mask)
        print('2-sigma for each column:', mean + (3 * std))
        print('2-sigma for each column:', mean - (3 * std))

        return self.data


    def above_sea_level(self, sea_level_pressure):
        """
        Recebe o argumento 'sea_level_pressure', que deve ser 10.12 dbar
        Converte a coluna da pressão para 'float',
        Mantém os valores que sejam maior do que sea_level_pressure
        """
        self.data['PRESSURE;DBAR'] = self.data['PRESSURE;DBAR'].astype(float)
        self.data = self.data[self.data['PRESSURE;DBAR'] > sea_level_pressure]

        return self.data

    @staticmethod
    def pressure_loops():
        """
        Remove as linhas onde ocorrem pressure loops
        """

        # Arredonda os valores de pressão para uma precisão específica (por exemplo, 2 casas decimais)
        data['PRESSURE;DBAR'] = data['PRESSURE;DBAR'].round(2)
        indices_loops = []
        for i in range(1, len(data['PRESSURE;DBAR'])):
            if data['PRESSURE;DBAR'][i] < data['PRESSURE;DBAR'][i - 1]:
                indices_loops.append(i)

        #print("Índices de loops de pressão identificados:", indices_loops)

        # Remove linhas onde ocorrem pressure loops
        data_sem_loops = data.drop(indices_loops).reset_index(drop=True)

        print("Tamanho original:", len(data))
        print("Tamanho após remover loops de pressão:", len(data_sem_loops))

    def lp_filter(self, sample_rate=24.0, time_constant=0.15):
        """
        Filtro passa-baixa
        Recebe os valores de sample_rate e time_constant
        """
        wn = (1.0 / time_constant) / (sample_rate * 2.0)
        b, a = signal.butter(2, wn, "low")
        padlen = int(0.3 * sample_rate * time_constant)
        new_df = self.data.copy()
        new_df.index = signal.filtfilt(b, a, self.data.index.values, padtype='constant', padlen=padlen)
        self.data = new_df

    def plot(self):
        """
        Monta um perfil de temperatura
        """
        pressure = self.data['PRESSURE;DBAR']
        temperature = self.data['TEMPERATURE;C']

        print(type(temperature))
        print(len(temperature))
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.invert_yaxis()
        ax.plot(temperature, pressure, 'b-', markersize=3)
        ax.set_xlabel('Temperature (°C)')
        ax.set_ylabel('Pressure (dBar)')
        ax.set_title('Temperature-Pressure Profile Pre-processed')
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
        plt.savefig("Perfil_preprocessado.png", format='png', dpi=900, transparent=False)

        plt.show()

    def process_data(self, sea_level_pressure):
        """
        Executa cada uma das funções de processamento em ordem
        Cronometra o tempo para cada função ser executada
        """

        start_time = time.perf_counter()
        self.convert()
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"convert elapsed time: {elapsed_time} seconds")

        start_time = time.perf_counter()
        self.downcast()
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"manter_downcast elapsed time: {elapsed_time} seconds")

        start_time = time.perf_counter()
        self.remove_outliers()
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"remove_outliers elapsed time: {elapsed_time} seconds")

        start_time = time.perf_counter()
        self.above_sea_level(sea_level_pressure)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"above_sea_level elapsed time: {elapsed_time} seconds")

        start_time = time.perf_counter()
        self.pressure_loops()
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"pressure_loops elapsed time: {elapsed_time} seconds")

        start_time = time.perf_counter()
        #self.lp_filter()
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"lp_filter elapsed time: {elapsed_time} seconds")

        start_time = time.perf_counter()
        self.plot()
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"plot pre-processed elapsed time: {elapsed_time} seconds")

        return self.data
'''=================================================================================================================='''

def bin_average(data, tamanho_janela, coluna, coluna2, lat):
    """
    Organiza os dados em average bins.
    """
    # Inicializa listas para armazenar os resultados
    profundidade = []
    pressure = []
    temperature = []
    salinity = []
    time_bin_avg = []

    data.loc[:, 'z'] = gsw.conversions.z_from_p(data['PRESSURE;DBAR'], lat)
    data.loc[:, 'z'] = abs(data['z'])

    # Iteração de 'tamanho_janela' em 'tamanho_janela' linhas até o final do DataFrame
    for i in range(0, len(data), tamanho_janela):
        # Verifica se o índice é válido para evitar "IndexError"
        if i + tamanho_janela - 1 < len(data):
            # Pega os dados da coluna da janela especificada
            dados_janela = data[coluna].iloc[i:i + tamanho_janela]
            dados_janela2 = data[coluna2].iloc[i:i + tamanho_janela]
            dados_janela3 = data['PRESSURE;DBAR'].iloc[i:i + tamanho_janela]  # Pressure column
            dados_janela_time = data['Time'].iloc[i:i + tamanho_janela]  # Time column

            # Converte os dados para o formato numérico, substituindo ',' por '.'
            dados_janela = dados_janela.astype(str).str.replace(',', '.').astype(float)
            dados_janela2 = dados_janela2.astype(str).str.replace(',', '.').astype(float)
            dados_janela3 = dados_janela3.astype(float)

            # Calcula a média dos dados das colunas da janela
            media_dados = np.mean(dados_janela)
            media_final = round(media_dados, 2)
            media_dados2 = np.mean(dados_janela2)
            media_final2 = round(media_dados2, 2)

            # Calcula a média entre o primeiro e o último valor da janela apenas para a coluna da profundidade
            media_primeiro_ultimo = np.mean([data['z'].iloc[i], data['z'].iloc[i + tamanho_janela - 1]])
            media_primeiro_ultimo_final = round(media_primeiro_ultimo, 2)

            # Adiciona os resultados às listas
            profundidade.append(media_primeiro_ultimo_final)
            pressure.append(dados_janela3.iloc[0])  # Include pressure value
            temperature.append(media_final)
            salinity.append(media_final2)

            # Calcula o tempo médio em segundos
            time_bin_avg.append(np.mean([t.hour * 3600 + t.minute * 60 + t.second for t in dados_janela_time]))

    # Cria um DataFrame com os resultados
    results_df = pd.DataFrame({
        'z': profundidade,
        'TEMPERATURE;C': temperature,
        'Calc. SALINITY; PSU': salinity,
        'PRESSURE;DBAR': pressure,
        'Time': time_bin_avg
    })

    return results_df

def seconds_to_hms(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

def plot_binned(data):
    """
    Monta um perfil de temperatura com os dados binados.
    """
    profundidade = data['z']
    temperature = data['TEMPERATURE;C']

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.invert_yaxis()
    ax.plot(temperature, profundidade, 'b-', markersize=3)
    ax.set_xlabel('Temperature (°C)')
    ax.set_ylabel('Pressure (dBar)')
    ax.set_title('Temperature-Pressure Profile Binned')
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
    plt.savefig('PATH', format='png', dpi=900, transparent=False)

    plt.show()


'''
Define o 'data' lendo um arquivo csv com o Pandas
Chama a classe DataProcessor
Executa a função que executa as outras funções da classe passando o argumento sea_level_pressure
Bina os dados pela média
Plota o gráfico dos dados processor e binados
Salva os novos dados processados em um novo csv
'''
data = pd.read_csv('/home/labdino/PycharmProjects/CTDprocessing/dados/DadosHidrografia/01_radial_1/0626_28072019_1609/FILE1.000', delimiter='\t', index_col=False)

# Adiciona uma nova coluna no dataframe com dados de profundidade obtidos a partir da coluna da pressão
data['z'] = gsw.conversions.z_from_p(data['PRESSURE;DBAR'], 22)

# Transforma os valores de profundidade em valores positivos novamente
data['z'] = abs(data['z'])

processor = DataProcessor(data)

# Converte 'Date / Time' para datetime e cria  'Date' e 'Time' em colunas separadas
processor.convert_date_time()

data_processada = processor.process_data(10.12)
data_processada.to_csv('/home/labdino/PycharmProjects/CTDprocessing/dados/DadosHidrografia/01_radial_1/0626_28072019_1609/FILE1teste1.csv')
print(data_processada['PRESSURE;DBAR'])


'''
Faz a binagem dos dados
Plota o perfil final
Cronometra cada uma das funções
Salva os dados binados e processados em um novo csv
'''

start_time = time.perf_counter()
binado = bin_average(data_processada, 10, 'TEMPERATURE;C', 'Calc. SALINITY; PSU', 22)
end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"bin_average elapsed time: {elapsed_time} seconds")

# Converte o 'Time' pra valores numéricos
binado['Time'] = pd.to_numeric(binado['Time'], errors='coerce')

# Aplica a função na coluna 'time'
binado['Time'] = binado['Time'].apply(seconds_to_hms)

start_time = time.perf_counter()
graph = plot_binned(binado)
end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"plot binned elapsed time: {elapsed_time} seconds")

binado.to_csv('PATH')

plot(data)
