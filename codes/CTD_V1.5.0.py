'''=================================================================================================================='''
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
import time
'''=================================================================================================================='''
class DataProcessor:
    """
    Classe do processador dos dados:

    - Utiliza o argumento data que vai ser o arquivo para o processamento.
    - Funções: - convert_decimal_separator_all_columns: converte o separador decimal;
               - remove_outliers: retira os spikes utilizando o método 3-sigma;
               - remove_above_sea_level: retira os dados medidos acima da coluna d'água (10.12 dbar);
               - remove_pressure_reversals: retira as reversões de pressão;
               - lp_filter: filtro passa-baixa;
               - plot_ts_diagram: plota o diagrama T-S simplificado;
               - process_data: executa todas as funções acima cronometrando quanto tempo cada uma levou para concluir.
    """

    def __init__(self, data):
        self.data = data

    def convert(self):
        """
        Para cada coluna do arquivo, exceto a coluna 'time', substitui ',' por '.', e nas células que tenham o '.' como
        separador de milhar, retira.
        """
        for column in self.data.columns:
            if column != 'time' and self.data[column].dtype == object:
                self.data[column] = self.data[column].str.replace(',', '.')
                self.data[column] = self.data[column].map(lambda x: re.sub(r'\.(?=.*\.)', '', x))
                self.data[column] = self.data[column].astype('float')

    def remove_outliers(self):
        """
        - Faz a média dos dados,
        - O desvio padrão,
        - Cria uma máscara que irá conter os valores que forem maiores ou menores que a média mais três desvios-padrão,
        - Retira a máscara dos dados.
        """
        mean = self.data.mean()
        std = self.data.std()
        mask = (self.data > mean + 3 * std) | (self.data < mean - 3 * std)
        self.data = self.data[~mask].dropna()

    def above_sea_level(self, sea_level_pressure):
        """
        - Recebe o argumento 'sea_level_pressure', que deve ser 10.12 dbar
        - Converte a coluna da pressão para 'float',
        - Mantém os valores que sejam maior do que sea_level_pressure
        """
        self.data['pressure'] = self.data['pressure'].astype(float)
        self.data = self.data[self.data['pressure'] > sea_level_pressure]

    def pressure_loops(self):
        """
        - Calcula-se a diferença entre os valores de pressão consecutivos no conjunto de dados
        - A função diff() é usada para obter a diferença entre cada par de elementos adjacentes na coluna 'pressure'
        - Atualiza-se o conjunto de dados, mantendo apenas as linhas em que a diferença de pressão é >= 0
        """
        pressure_diff = self.data['pressure'].diff()
        self.data = self.data[pressure_diff >= 0]

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

    def plot(self):
        """
        - Monta um diagrama
        """
        pressure = self.data['pressure']
        temperature = self.data['temperature']

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.invert_yaxis()
        ax.plot(temperature, '-o', markersize=3)
        ax.set_xlabel('Pressure (dBar)')
        ax.set_ylabel('Temperature (°C)')
        ax.set_title('Temperature-Pressure Profile Pre-processed')
        ax.grid(True)
        plt.show()

    def process_data(self, sea_level_pressure):
        """
        - Executa cada uma das funções de processamento em ordem
        - Cronometra o tempo para cada função ser executada
        """

        start_time = time.perf_counter()
        self.convert()
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"convert elapsed time: {elapsed_time} seconds")

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
        self.lp_filter()
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
def bin_average(data, tamanho_janela, coluna):
    """
    :param data: fonte do dado
    :param tamanho_janela: tamanho dos bins
    :param coluna: qual coluna para calcular a média
    :return: retorna um dataframe com os resultados
    """
    # Inicialize listas para armazenar os resultados
    mediana_pressoes_lista = []
    media_dados_lista = []

    # Iteração de 'tamanho_janela' em 'tamanho_janela' linhas até o final do DataFrame
    for i in range(0, len(data), tamanho_janela):
        # Pegue os dados da coluna da janela especificada
        dados_janela = data[coluna].iloc[i:i + tamanho_janela]

        # Converta os dados para o formato numérico, substituindo ',' por '.'
        dados_janela = dados_janela.astype(str).str.replace(',', '.').astype(float)

        # Calcule a média dos dados da coluna da janela
        media_dados = np.mean(dados_janela)
        media_final = round(media_dados, 2)

        # Pegue as pressões da janela especificada
        pressoes_janela = data['pressure'].iloc[i:i + tamanho_janela]

        # Calcule a mediana das pressões da janela
        mediana_pressoes = np.median(pressoes_janela)
        mediana_final = round(mediana_pressoes, 2)

        # Adicione os resultados às listas
        mediana_pressoes_lista.append(mediana_final)
        media_dados_lista.append(media_final)

    # Crie um novo DataFrame com os resultados
    results_df = pd.DataFrame({'mediana_pressoes': mediana_pressoes_lista, coluna: media_dados_lista})

    return results_df

def plot_binned(data):
    """
    - Monta um diagrama
    """
    pressure = data['mediana_pressoes']
    temperature = data['temperature']

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.invert_yaxis()
    ax.plot(temperature, '-o', markersize=3)
    ax.set_xlabel('Pressure (dBar)')
    ax.set_ylabel('Temperature (°C)')
    ax.set_title('Temperature-Pressure Profile Binned')
    ax.grid(True)
    plt.show()
'''=================================================================================================================='''
'''
- Define o 'data' lendo um arquivo csv com o Pandas
- Chama a classe DataProcessor
- Executa a função que executa as outras funções da classe passando o argumento sea_level_pressure
- Bina os dados pela média
- Plota o gráfico dos dados processados e binados
- Salva os novos dados processados em um novo csv
'''
data = pd.read_csv('/home/labdino/PycharmProjects/CTDprocessing/venv/Dados/FILE17V2.csv', delimiter='\t')
processor = DataProcessor(data)
data_processada = processor.process_data(10.12)
data_processada.to_csv('/home/labdino/PycharmProjects/CTDprocessing/venv/dados_pós/processado.csv')
'''=================================================================================================================='''
'''
- Faz a binagem dos dados
- Plota o perfil final
- Cronometra cada uma das funções
- Salva os dados binados e processados em um novo csv
'''
start_time = time.perf_counter()
binado = bin_average(data_processada, 5, 'temperature')
end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"bin_average elapsed time: {elapsed_time} seconds")

start_time = time.perf_counter()
graph = plot_binned(binado)
end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"plot binned elapsed time: {elapsed_time} seconds")

binado.to_csv('/home/labdino/PycharmProjects/CTDprocessing/venv/dados_pós/resultado.csv')
'''=================================================================================================================='''
