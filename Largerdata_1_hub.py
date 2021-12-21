import pandas as pd
import gurobipy as gp
from gurobipy import GRB

distance = pd.read_csv('dist_matrix.csv')
orders = pd.read_csv('toy_dataset.csv')
hubs = pd.read_csv('Hubs.csv')

#assume $0.36 per pound per mile constant cost in the middle mile problem
cost = 0.37

#open 1 hub
p = 1

#assume capacity of the hub is 100000
capacity = 100000

hub_candidate = list(hubs.hubs)

#fixed cost
#fixed_list = list(hubs.fixed_cost)

origin_locs_list = list(orders.ORIGIN_POSTAL_CODE)
dest_locs_list = list(orders.DESTINATION_POSTAL_CODE)
order_pairs = list(zip(origin_locs_list,dest_locs_list))
Load_list = list(orders.REGISTERED_TOTAL_WEIGHT)

m = gp.Model("1_hub_larger")

#Decision Variables
x = m.addVars(hub_candidate, vtype=GRB.BINARY, name="hub")
y = m.addVars(order_pairs, hub_candidate, vtype=GRB.CONTINUOUS, name='Assign')

m.update()

#Objective Function
objexpr1=0
for (i,j) in order_pairs:
        for k in hub_candidate:
                C_i_k = round(cost*list(distance.loc[distance['From']==i][str(k)])[0],2)
                C_k_j = round(cost*list(distance.loc[distance['From']==j][str(k)])[0],2)
                C_i_j_k = round(C_i_k + C_k_j)
                objexpr1+=Load_list[origin_locs_list.index(i)] * C_i_j_k * y[i,j,k]


m.setObjective(objexpr1, GRB.MINIMIZE)

#if oncludes fixed cost
#m.setObjective(objexpr1+y.prod(fixed_list), GRB.MINIMIZE)


#Constraints

#con1

for (i,j) in order_pairs:
        expr_1=0
        for k in hub_candidate:
                expr_1+=y[i,j,k]
        m.addConstr(expr_1==1 ,name=f"cons1[{i,j}]")

#con2

expr2=0
for k in hub_candidate:
        expr2+=x[k]
m.addConstr(expr2==p ,name="cons2")

#con3

for (i,j) in order_pairs:
        for k in hub_candidate:
                m.addConstr(y[i,j,k]<=x[k] ,name=f"cons3[{i,j,k}]")
                m.addConstr(y[i,j,k]>=0 ,name=f"cons3_2[{i,j,k}]")

#con4
for (i,j) in order_pairs:
        for k in hub_candidate:
                 m.addConstr(Load_list[origin_locs_list.index(i)] * y[i,j,k] <= capacity * x[k], name="cons4")

m.write("1_hub_larger.lp")

m.optimize()

if m.status == GRB.OPTIMAL:
        print('Optimal objective: %g' % m.objVal)

elif m.status == GRB.INF_OR_UNBD:
        sys.exit(0)
elif m.status == GRB.INFEASIBLE:
        sys.exit(0)
elif m.status == GRB.UNBOUNDED:
        sys.exit(0)
else:
        print('Optimization ended with status %d' % m.status)
        sys.exit(0)

for v in m.getVars():
        if v.x!=0:
                print('%s %g' % (v.varName, v.x))
