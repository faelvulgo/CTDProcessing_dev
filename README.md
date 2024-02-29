<h1 align="center"> CTD Processing </h1>

![Badge em Desenvolvimento](http://img.shields.io/static/v1?label=Versão&message=V.1.7.0&color=GREEN&style=for-the-badge)

# Descrição
Este é um projeto desenvolvido por Rafael S. Bittencourt como inciação científica do Laboratório de Dinâmica Oceânica.
O objetivo do projeto é um módulo em Python para o pré-processamento de dados de CTD.

# Funcionalidades
O módulo possui diversas funções para pré-processar os dados de CTD:
 - normalizar os separadores dos dados;
 - seaparar o downcast do aparelho de CTD;
 - retirar spikes seguindo o método 3-sigma;
 - retirar loops de pressão;
 - retirar dados medidos acima da coluna d'água;
 - aplicar um filtro passa-baixa;
 - binagem dos dados.
 - diagrama T-S

# Acesso ao módulo
Para utilizar a rotina só é preciso importar o arquivo CTD_utilities: 
```Python
from CTD_utilities import *
```
As colunas de pressão, temperatura e salinidade devem ser nomeadas respectivamente como: PRESSURE;DBAR , TEMPERATURE;C , Calc. SALINITY; PSU 

# Exemplos
Aqui está o exemplo de um arquivo de dados de CTD sem ter nenhum tipo de pré-processamento:

![Perfil de dados brutos](https://github.com/faelvulgo/CTDprocessing/blob/master/perfis/Perfil_bruto.png)

Podemos perceber diversos ruídos e laços de pressão, bem como dados indesejados acima da coluna d'água. Após o processamento utilizando a rotina, este é o resultado gerado para o mesmo arquivo de dados:

![Perfil depois de todas as etapas de processamento](https://github.com/faelvulgo/CTDprocessing/blob/master/perfis/Perfil_binado.png)https://github.com/faelvulgo/CTDprocessing/blob/master/perfis/Perfil_binado.png

# Quick Guide em Jupyter Notebook
Para acessar um guia rápido das funções, está disponibilizado o Jupyter Notebook no repositório.
