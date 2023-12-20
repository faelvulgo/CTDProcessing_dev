# ---------- Pacotes utilizados ----------

install.packages("ggplot2")
library(ggplot2)

# ---------- Acessando os dados ----------

setwd("/home/labdino/Downloads")
getwd()

df <-read.csv2("analise.csv", sep='\t')
str(df)

par(mfrow=c(2,2))

summary(df)

# ---------- Análise exploratória turbidez ----------

# Frequência absoluta
turbidity.tb <- table(df$TURBIDITY.FTU)
turbidity.tb

# Frequência relativa
prop.table(turbidity.tb)

#representao grafica
barplot(turbidity.tb, main='Turbidez', col='#C4FFB2')

# ---------- Análise exploratória oxigênio dissolvido ----------

# Frequência absoluta
dissolved.tb <- table(df$DISSOLVED.OXYGEN.SAT.)
dissolved.tb

# Frequência relativa
prop.table(dissolved.tb)

#representao grafica
barplot(dissolved.tb, main='Oxigênio Dissolvido', col='#c40056')

# ---------- Análise exploratória pressão ----------

# Frequência absoluta
press.tb <- table(df$PRESSURE.DBAR)
press.tb

# Frequência relativa
prop.table(press.tb)

#representao grafica
barplot(press.tb, main='Pressão', col='#c1b400')

# ---------- Análise exploratória temperatura ----------

# Frequência absoluta
temp.tb <- table(df$TEMPERATURE.C)
temp.tb

# Frequência relativa
prop.table(temp.tb)

#representao grafica
barplot(temp.tb, main='Temperatura', col='#00ffff')

# ---------- Análise exploratória altitude ----------

# Frequência absoluta
altitude.tb <- table(df$ALTITUDE.M)
altitude.tb

# Frequência relativa
prop.table(altitude.tb)

#representao grafica
barplot(altitude.tb, main='Altitude', col='grey')

# ---------- Análise exploratória condutividade ----------

# Frequência absoluta
conduct.tb <- table(df$CONDUCTIVITY.MS.CM)
conduct.tb

# Frequência relativa
prop.table(conduct.tb)

#representao grafica
barplot(conduct.tb, main='Condutividade', col='brown')

# ---------- Análise exploratória pH ----------

# Frequência absoluta
ph.tb <- table(df$PH.PH)
ph.tb

# Frequência relativa
prop.table(ph.tb)

#representao grafica
barplot(ph.tb, main='pH', col='pink')

# ---------- Análise exploratória par ----------

# Frequência absoluta
par.tb <- table(df$PAR.GQ.M2)
par.tb

# Frequência relativa
prop.table(par.tb)

#representao grafica
barplot(par.tb, main='Par', col='purple')

# ---------- Análise exploratória redox ----------

# Frequência absoluta
redox.tb <- table(df$REDOX.MV)
redox.tb

# Frequência relativa
prop.table(redox.tb)

#representao grafica
barplot(redox.tb, main='Redox', col='orange')

# ---------- Análise exploratória fluorômetro ----------

# Frequência absoluta
fluor.tb <- table(df$FLUOROMETER..C..UG.L)
fluor.tb

# Frequência relativa
prop.table(fluor.tb)

#representao grafica
barplot(fluor.tb, main='Fluorômetro', col='yellow')

# ---------- Análise exploratória salinidade ----------

# Frequência absoluta
salinidade.tb <- table(df$Calc..SALINITY..PSU)
salinidade.tb

# Frequência relativa
prop.table(salinidade.tb)

#representao grafica
barplot(salinidade.tb, main='Salinidade', col='blue')

# ---------- Análise exploratória densidade ----------

# Frequência absoluta
densidade.tb <- table(df$Calc..DENSITY.ANOMALY..KG.M3..EOS.80.)
densidade.tb

# Frequência relativa
prop.table(densidade.tb)

#representao grafica
barplot(densidade.tb, main='Densidade', col='green')

# ---------- Análise exploratória sos ----------

# Frequência absoluta
sos.tb <- table(df$Calc..SOS..M.SEC)
sos.tb

# Frequência relativa
prop.table(sos.tb)

#representao grafica
barplot(sos.tb, main='SOS', col='red')

# ---------- Análise exploratória gráfico de linhas ----------

# Salinidade
grsal <-ggplot(df, aes(x = ID, y = sal)) +
  geom_line(color = "blue", linetype = "solid") +
  labs(title = 'Salinidade',
       y = 'Salinidade',
       x = 'ID')
grsal

# Pressão
grpress <-ggplot(df, aes(x = ID, y = pressao)) +
  geom_line(color = "red", linetype = "solid") +
  labs(title = 'Pressão',
       y = 'Pressão',
       x = 'ID')
grpress

# Temperatura
grtemp <-ggplot(df, aes(x = ID, y = temp)) +
  geom_line(color = "green", linetype = "solid") +
  labs(title = 'Temperatura',
       y = 'Temperatura',
       x = 'ID')
grtemp

# Densidade
grtemp <-ggplot(df, aes(x = ID, y = dens)) +
  geom_line(color = "purple", linetype = "solid") +
  labs(title = 'Densidade',
       y = 'Densidade',
       x = 'ID')
grtemp

