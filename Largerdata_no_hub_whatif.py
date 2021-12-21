import pandas as pd

orders = pd.read_csv('toy_dataset.csv')

#assume $0.59 per pound per mile constant cost without going through a hub(cheaper)
cost = 0.5

Load_list = list(orders.REGISTERED_TOTAL_WEIGHT)
Distance = list(orders.distance)

x = 0
for y in Distance:
	x += round(Load_list[Distance.index(y)] * y * cost)
print('No Hub Total Cost: ' + str(x) + ' (Unit cost:' + str(cost)  + ')')
