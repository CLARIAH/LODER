from z3 import *
import networkx as nx

import string

input = nx.Graph()
output = nx.Graph()

# set up the weighted input graph
weighted_edges = [(1, 2, 0.95), (2,3, 0.675), (2,6, 1.0), (3, 4, 0.76),
(4,5, 0.56), (4,5,0.56),(5,6,1.0), # red
(7,8,0.98), # yellow
(9,14, 0.976),(10,14, 0.95), (11,14, 0.45), (13,14,0.67), (11,12, 1.0), # green
(15,16, 0.756), (15,17, 1.0), (16,17, 0.35), (16,18, 0.84) # blue
]
input.add_weighted_edges_from(weighted_edges)

# add my erroenous edges
erroenous_weighted_edges = [(1, 10, 0.25), # A - J
(1, 7, 0.2), # A-G
(12, 15, 0.1), # L-O
(18, 8, 0.5) # R, H
]
input.add_weighted_edges_from(erroenous_weighted_edges)


for n, nbrs in input.adj.items():
	for nbr, eattr in nbrs.items():
		wt = eattr['weight']
		if n < nbr:
			print(f"({string.ascii_lowercase[n-1]}, {string.ascii_lowercase[nbr-1]}, {wt:.3})")


print ('Now the strengthen edges')
# strengthen edges
strengthening_edges = [(7,8), # GH
(2,3),(5,6),(4,5), # red
 (9,10), (9,13), (12,13), # green
(15,18)] # blue
for (l,r) in strengthening_edges:
	if (l<r):
		print(f"({string.ascii_lowercase[l-1]}, {string.ascii_lowercase[r-1]})")


print ('Now the attacking edges')
# attacking edges:
attacking_edges = [(6,9), (5,13), (5,12), # left
(2, 7), (3, 8), # B - G, C- H
(5,15), # E-O
(4, 18), # D - R
(7,9), # I - G
(13, 18) # M - R
]
for (l,r) in attacking_edges:
	if (l < r):
		print(f"({string.ascii_lowercase[l-1]}, {string.ascii_lowercase[r-1]})")


o = Optimize()
timeout = 1000 * 60 * 1 # depending on the size of the graph
o.set("timeout", timeout)
print('timeout = ',timeout/1000, 'seconds')
print('timeout = ',timeout/1000/60, 'mins')

default_weight_factor = 1
strengthening_weight = 0.35
attacking_weight = -10.0

encode = {}
soft_clauses = {}
max_clusters = 5

encode_id = 1
for n in input.nodes():
	encode[n] = Int(str(encode_id))
	encode_id += 1
	o.add(encode[n] > Int(0))
	o.add(encode[n] < Int(max_clusters))


for (u, v, wt) in input.edges.data('weight'):
	# print ('I have weight',wt)
	if u < v:
		soft_clauses[(u,v)] = wt * default_weight_factor

# add strengthening edges
for (u, v) in strengthening_edges:
	# print ('I have weight',wt)
	if u < v:

		if (u,v) in soft_clauses:
			soft_clauses[(u,v)] += strengthening_weight
		else:
			soft_clauses[(u,v)] = strengthening_weight

# generate attacking edges

for (u, v) in attacking_edges:
	# print ('I have weight',wt)
	if u < v:
		if (u,v) in soft_clauses:
			soft_clauses[(u,v)] += attacking_weight
		else:
			soft_clauses[(u,v)] = attacking_weight

print ('All the soft clauses')
for (l, r) in soft_clauses:
	wt = soft_clauses[(l,r)]
	print(f"({string.ascii_lowercase[l-1]}, {string.ascii_lowercase[r-1]}, {wt:.3})")


# Add them to the solver:
for (l,r) in soft_clauses.keys():
	clause = (encode[l] == encode[r])
	if soft_clauses[(l,r)] > 0:
		o.add_soft(clause, soft_clauses[(l,r)])
	else:
		o.add_soft(Not(clause), -1*soft_clauses[(l,r)])

removed_edges = []
# Finally, get the identified_edges
smt_result = o.check()
print ('the SMT result is ', smt_result)
# smt_result = o.maximize()
if smt_result == 'unknown':
	print ('What!!!')
else:
	# print ('start decoding')
	# print ('>encode length ', len(encode.keys()))

	m = o.model()
	for arc in input.edges():
		(left, right) = arc
		if m.evaluate(encode[left] == encode[right]) == False:
			removed_edges.append(arc)
		elif m.evaluate((encode[left] == encode[right])) == True:
			output.add_edge(left, right)
		else:
			print ('error in decoding!')


for n in input.nodes():
	print (f"{string.ascii_lowercase[n-1]} is associated with the integer {m.evaluate(encode[n])}")

# print ('removed edges = ')
# for (l,r) in removed_edges:
# 		print(f"removed ({string.ascii_lowercase[l-1]}, {string.ascii_lowercase[r-1]})")

for (l,r, wt) in erroenous_weighted_edges:
	if m.evaluate((encode[l] == encode[r])) == True:
		print(f"remained ({string.ascii_lowercase[l-1]}, {string.ascii_lowercase[r-1]})")
	else:
		print(f"removed ({string.ascii_lowercase[l-1]}, {string.ascii_lowercase[r-1]})")
