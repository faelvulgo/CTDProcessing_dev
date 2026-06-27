def nan_statistic():
    with open('/home/labdino/PycharmProjects/Internal_waves/dados/Cruzeiro_2/01. Boia de Topo - 75m/200428_20200227_2329.csv') as df:
        a = 0
        b = 0

        for line in df:
            if 'nan' in line:
                a += 1
            b += +1

        return a, b


nan_count, total_count = nan_statistic()
percentage_nan = 100 * float(nan_count) / float(total_count)
print("Percentage of 'nan' occurrences:", percentage_nan)