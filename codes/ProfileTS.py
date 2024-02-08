import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

# Função para ler o arquivo CSV e plotar o gráfico
def plot_perfil_termosal(file_path):
    # Carregar o arquivo CSV usando pandas
    df = pd.read_csv('/home/labdino/PycharmProjects/CTDprocessing/dados/01. Dados Brutos/04_radial_3/0656_30072019_2242/FILE57_binado.csv')

    # Extrair colunas relevantes
    temperatura = df['TEMPERATURE;C']
    salinidade = df['Calc. SALINITY; PSU']
    pressao = df['PRESSURE;DBAR']

    # Criar o gráfico com dois eixos x
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plotar Temperatura no primeiro eixo x e pressão no y
    ax1.set_xlabel('Temperatura', color='tab:blue')
    ax1.set_ylabel('Pressão', color='tab:blue')
    ax1.plot(temperatura, pressao, color='tab:blue', label='Temperatura')
    ax1.set_xlim([0, 25])
    ax1.set_ylim([0, 2750])

    # Configurar os parâmetros do eixo x
    ax1.tick_params(axis='x', labelcolor='tab:blue')

    # Criar o segundo eixo x para a Salinidade
    ax2 = ax1.twiny()
    ax2.set_xlabel('Salinidade', color='tab:orange')
    ax2.plot(salinidade, pressao, color='tab:orange', label='Salinidade')
    ax2.set_xlim([34, 37.5])

    # Configurar os parâmetros do eixo x do segundo gráfico
    ax2.tick_params(axis='x', labelcolor='tab:orange')

    # Inverter o eixo y
    ax1.invert_yaxis()

    # Configurar o título do gráfico
    plt.title('Perfil de Temperatura e Salinidade - 656')

    # Configurar o rótulo do eixo y
    plt.ylabel('Pressão')

    # Ajustar o layout do gráfico
    fig.tight_layout()

    # Adicionar legenda ao gráfico
    fig.legend(loc='upper right', bbox_to_anchor=(1, 1))

    # Salvar o gráfico como imagem PNG
    plt.savefig('/home/labdino/PycharmProjects/CTDprocessing/dados/01. Dados Brutos/04_radial_3/0656_30072019_2242/Perfil_TS_scale.png', format='png', dpi=900, transparent=False)

    # Exibir o gráfico
    plt.show()

# Substitua 'caminho/do/seu/arquivo.csv' pelo caminho real do seu arquivo CSV
plot_perfil_termosal('/home/labdino/PycharmProjects/CTDprocessing/dados/01. Dados Brutos/04_radial_3/0656_30072019_2242/FILE57_binado.csv')
