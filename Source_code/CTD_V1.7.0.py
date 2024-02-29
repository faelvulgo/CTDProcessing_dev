"""=================================================================================================================="""
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
import gsw
'''=================================================================================================================='''


def plot(data):
    """
    - Monta um diagrama
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
    plt.savefig('/home/labdino/PycharmProjects/CTDprocessing/dados/01. Dados Brutos/01_radial_1/0626_28072019_1609/FILE1_bruto.png', format='png', dpi=900, transparent=False)

    plt.show()

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
            if column != 'Date / Time' and self.data[column].dtype == object:
                self.data[column] = self.data[column].str.replace(',', '.')
                self.data[column] = self.data[column].map(lambda x: re.sub(r'\.(?=.*\.)', '', x))
                self.data[column] = self.data[column].astype('float')

    def downcast(self):
        """
        - Identifica o maior valor de pressão e mantém apenas as linhas antes desse valor.
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
        - Faz a média dos dados,
        - O desvio padrão,
        - Cria uma máscara que irá conter os valores que forem maiores ou menores que a média mais três desvios-padrão,
        - Retira a máscara dos dados.
        """
        mean = self.data.mean()
        std = self.data.std()
        mask = (self.data > mean + 3 * std) | (self.data < mean - 3 * std)
        self.data = self.data[~mask].dropna()

        print('Média de cada coluna dos dados:' + str(mean))
        print('Desvio padrão de cada coluna dos dados: ' + str(std))
        print('3-sigma para cada coluna de dados: ' + str(mean + 3 * std))

    def above_sea_level(self, sea_level_pressure):
        """
        - Recebe o argumento 'sea_level_pressure', que deve ser 10.12 dbar
        - Converte a coluna da pressão para 'float',
        - Mantém os valores que sejam maior do que sea_level_pressure
        """
        self.data['PRESSURE;DBAR'] = self.data['PRESSURE;DBAR'].astype(float)
        self.data = self.data[self.data['PRESSURE;DBAR'] > sea_level_pressure]

    @staticmethod
    def pressure_loops():
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
        - Executa cada uma das funções de processamento em ordem
        - Cronometra o tempo para cada função ser executada
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
        '''
        start_time = time.perf_counter()
        self.remove_outliers()
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"remove_outliers elapsed time: {elapsed_time} seconds")
        '''
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
        '''
        start_time = time.perf_counter()
        self.plot()
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"plot pre-processed elapsed time: {elapsed_time} seconds")
        '''
        return self.data
'''=================================================================================================================='''
def bin_average(data, tamanho_janela, coluna, coluna2):
    """
    :param data: fonte do dado
    :param tamanho_janela: tamanho dos bins
    :param coluna: qual coluna para calcular a média
    :return: retorna um dataframe com os resultados
    """
    # Inicialize listas para armazenar os resultados
    profundidade = []
    temperature = []
    salinity = []

    # Iteração de 'tamanho_janela' em 'tamanho_janela' linhas até o final do DataFrame
    for i in range(0, len(data), tamanho_janela):
        # Verifique se o índice é válido para evitar "IndexError"
        if i + tamanho_janela - 1 < len(data):
            # Pegue os dados da coluna da janela especificada
            dados_janela = data[coluna].iloc[i:i + tamanho_janela]
            dados_janela2 = data[coluna2].iloc[i:i + tamanho_janela]

            # Converta os dados para o formats numérico, substituindo ',' por '.'
            dados_janela = dados_janela.astype(str).str.replace(',', '.').astype(float)
            dados_janela2 = dados_janela2.astype(str).str.replace(',', '.').astype(float)

            # Calcule a média dos dados da coluna da janela
            media_dados = np.mean(dados_janela)
            media_final = round(media_dados, 2)
            media_dados2 = np.mean(dados_janela2)
            media_final2 = round(media_dados2, 2)

            # Calcule a média entre o primeiro e o último valor da janela apenas para a coluna de pressão
            media_primeiro_ultimo = np.mean([data['z'].iloc[i], data['z'].iloc[i + tamanho_janela - 1]])
            media_primeiro_ultimo_final = round(media_primeiro_ultimo, 2)

            # Adicione os resultados às listas
            profundidade.append(media_primeiro_ultimo_final)
            temperature.append(media_final)
            salinity.append(media_final2)

    # Crie um DataFrame com os resultados
    results_df = pd.DataFrame({
        'z': profundidade,
        'TEMPERATURE;C': temperature,
        'Calc. SALINITY; PSU': salinity
    })

    return results_df

def plot_binned(data):
    """
    - Monta um diagrama
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
    plt.savefig('/home/labdino/PycharmProjects/CTDprocessing/dados/01. Dados Brutos/01_radial_1/0626_28072019_1609/FILE1_binado.png', format='png', dpi=900, transparent=False)

    plt.show()


'''=================================================================================================================='''
'''
- Define o 'data' lendo um arquivo csv com o Pandas
- Chama a classe DataProcessor
- Executa a função que executa as outras funções da classe passando o argumento sea_level_pressure
- Bina os dados pela média
- Plota o gráfico dos dados processor e binados
- Salva os novos dados processados em um novo csv
'''
data = pd.read_csv('/home/labdino/PycharmProjects/CTDprocessing/dados/01. Dados Brutos/01_radial_1/0626_28072019_1609/FILE1.000', delimiter='\t', index_col=False)

# Adiciona uma nova coluna no dataframe com dados de profundidade obtidos a partir da coluna da pressão
data['z'] = gsw.conversions.z_from_p(data['PRESSURE;DBAR'], 24)

# Transforma os valores de profundidade em valores positivos novamente
data['z'] = abs(data['z'])

processor = DataProcessor(data)
data_processada = processor.process_data(10.12)
data_processada.to_csv('/home/labdino/PycharmProjects/CTDprocessing/dados/01. Dados Brutos/01_radial_1/0626_28072019_1609/FILE1_processado.csv')
print(data_processada['PRESSURE;DBAR'])
'''=================================================================================================================='''
'''
- Faz a binagem dos dados
- Plota o perfil final
- Cronometra cada uma das funções
- Salva os dados binados e processados em um novo csv
'''

start_time = time.perf_counter()
binado = bin_average(data_processada, 5, 'TEMPERATURE;C', 'Calc. SALINITY; PSU')
end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"bin_average elapsed time: {elapsed_time} seconds")

start_time = time.perf_counter()
graph = plot_binned(binado)
end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f"plot binned elapsed time: {elapsed_time} seconds")

binado.to_csv('/home/labdino/PycharmProjects/CTDprocessing/dados/01. Dados Brutos/01_radial_1/0626_28072019_1609/FILE1_binado.csv')
'''=================================================================================================================='''
plot(data)
