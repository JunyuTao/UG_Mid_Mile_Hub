import pandas as pd
import gurobipy as gp
from gurobipy import GRB
import sys

Rate=0.36
alpha=0.6
capacity=100000
p=2#number of open hubs


orders=pd.read_csv('toy_dataset.csv')
Hubs_info=pd.read_csv('Hubs.csv')
distanceMat=pd.read_csv('dist_matrix.csv')


#converting a column to a list
hub_candidate_locs=list(Hubs_info.hubs)
hub_pairs=[]
for hub1 in hub_candidate_locs:
	for hub2 in hub_candidate_locs:
		if hub1!=hub2:
			hub_pairs.append((hub1,hub2))
    
#hub_fixedcost=list(Hubs_info.fixed_cost)

origin_locs_list=list(orders.ORIGIN_POSTAL_CODE)
dest_locs_list=list(orders.DESTINATION_POSTAL_CODE)
order_pairs=list(zip(origin_locs_list,dest_locs_list))

Load_W=list(orders.REGISTERED_TOTAL_WEIGHT)


#model implementation
model = gp.Model("UG_Hub")

#define decision variables
x = model.addVars(order_pairs,hub_pairs,vtype=GRB.CONTINUOUS, name="x")
y= model.addVars(hub_candidate_locs,vtype=GRB.BINARY, name="y")

model.update()  
#define your objective function

objexpr1=0
for (i,j) in order_pairs:
	for (k,m) in hub_pairs:
		C_i_k=round(Rate*list(distanceMat.loc[distanceMat['From']==i][str(k)])[0],2)
		C_m_j=round(Rate*list(distanceMat.loc[distanceMat['From']==j][str(m)])[0],2)
		C_k_m=round(alpha*Rate*list(distanceMat.loc[distanceMat['From']==k][str(m)])[0],2)
		C_i_j_k_m=round(C_i_k+C_m_j+ C_k_m,2)
		objexpr1+=Load_W[origin_locs_list.index(i)]*C_i_j_k_m*x[i,j,k,m]

model.setObjective(objexpr1, GRB.MINIMIZE)    
        
#define your constraints

#cons(1)
for (i,j) in order_pairs:
        expr_1=0
        for (k,m) in hub_pairs:
                expr_1+=x[i,j,k,m]
        model.addConstr(expr_1==1 ,name=f"cons1[{i,j}]")
        

#cons(2)
expr2=0
for k in hub_candidate_locs:
	expr2+=y[k]
model.addConstr(expr2==p ,name="cons2")


#cons(3)
for (i,j) in order_pairs:
        for (k,m) in hub_pairs:
                model.addConstr(x[i,j,k,m]<=y[k] ,name=f"cons3[{i,j,k,m}]")
                model.addConstr(x[i,j,k,m]>=0 ,name=f"cons3_2[{i,j,k,m}]")

#cons(4)
for (i,j) in order_pairs:
        for (k,m) in hub_pairs:
                model.addConstr(x[i,j,k,m]<=y[m] ,name=f"cons4[{i,j,k,m}]")

#capacity constraint
for (i,j) in order_pairs:
	for (k, m) in hub_pairs:
		model.addConstr(Load_W[origin_locs_list.index(i)] * x[i,j,k,m] <= capacity * y[k], name="capacity_k")
		model.addConstr(Load_W[origin_locs_list.index(i)] * x[i,j,k,m] <= capacity * y[m], name="capacity_m")

model.write("UG_Hub.lp")



model.optimize()

if model.status == GRB.OPTIMAL:
	print('Optimal objective: %g' % model.objVal)

elif model.status == GRB.INF_OR_UNBD:
	sys.exit(0)
elif model.status == GRB.INFEASIBLE:
	sys.exit(0)
elif model.status == GRB.UNBOUNDED:
	sys.exit(0)
else:
	print('Optimization ended with status %d' % m.status)
	sys.exit(0)

for v in model.getVars():
	if v.x!=0:
        	print('%s %g' % (v.varName, v.x))
