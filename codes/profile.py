import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

data = pd.read_csv('/home/labdino/PycharmProjects/BioGeoQmc/perfis.csv')


x = data['NH']
y = data['UAO']

plt.boxplot(x, y)

plt.title('NH versus UAO')
plt.xlabel('NH')
plt.ylabel('UAO')

plt.gca().invert_yaxis()

plt.show()
