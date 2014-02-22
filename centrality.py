import sys
import networkx as nx
from stats_common import *

def make_graph(start_date=None, end_date=None):
	con = db_connection()
	curs = con.cursor()

	sys.stderr.write("Finding threads by participants...\n")

	thread_users = {}

	if start_date is None:
		curs.execute("select subject, fromcname from mail group by subject, fromcname")
	else:
		curs.execute("select subject, fromcname from mail where sent >= '%s' and sent <= '%s' group by subject, fromcname" % (start_date, end_date))
	
	rows = curs.fetchall()

	for row in rows:
		subject, user = row
		subject = subject.replace("[", " ").replace("]", " ")
		subject = subject.replace("re:", " ").replace("RE:", " ").replace("Re:", " ")
		subject = subject.strip()
	
		if subject not in thread_users:
			thread_users[subject] = set()
		thread_users[subject].add(user)

	# Assume an undirected graph for now
	sys.stderr.write("Constructing graphs...\n")
	rels = nx.Graph() # Graph of all users

	for subject in thread_users:
		users = thread_users[subject]
		while len(users):
			f_user = users.pop()
			rels.add_node(f_user)
			for t_user in users:
				if rels.has_edge(f_user, t_user):
					rels.edge[f_user][t_user]["weight"] += 1
				rels.add_edge(f_user, t_user, weight=1)

	return rels

def report_basic(g):
	nodes = g.number_of_nodes()
	edges = g.number_of_edges()
	print "Nodes: %d, Edges: %d" % (nodes, edges)
	return nodes, edges

def report_centrality_users(g, limit=None):
	deg_cen = nx.degree_centrality(g)
	#deg_cen = nx.betweenness_centrality(g)
	deg_cen_sort = sorted(deg_cen.iteritems(), key=lambda k: k[1], reverse=True)
	
	print "**** Degree Centrality ****"
	print "---------------------------"
	i = 0
	for d in deg_cen_sort:
		print "[%s]	%s" % d
		i += 1
		if i == limit:
			break
	print "---------------------------"
	print
	
	return deg_cen_sort
	
def report_components(g):
	components = nx.connected_component_subgraphs(g)
	print "Components: %d" % len(components)
	c_data = {}
	for i in range(len(components)):
		c = components[i]
		if len(c.nodes()) > 5: # Avoid reporting on many small components
			c_data["nodes"] = len(c.nodes())
			c_data["edges"] = len(c.edges())
			c_data["avg_clustering"] = nx.average_clustering(c)
			c_data["diameter"] = nx.diameter(c)
			c_data["radius"] = nx.radius(c)
			c_data["center"] = len(nx.center(c))
			c_data["periphery"] = len(nx.periphery(c))

			print "* Component %d:" % i
			for k in c_data:
				print "--- %s: %s" % (k, c_data[k])

	return c_data

# Test
y = 2001 
rels = make_graph("%s-01-01" % y, "%s-01-01" % (y+1))
nodes, edges = report_basic(rels)
report_centrality_users(rels, 20)
#c_data = report_components(rels)
sys.exit(-1)


y_c_data = []

for y in range(1994, 2012+1):
	rels = make_graph("%s-01-01" % y, "%s-01-01" % (y+1))
	sys.stderr.write("Reporting for %s\n" % y)
	
	print
	print "----- %s -----" % y
	print
	nodes, edges = report_basic(rels)
	report_centrality_users(rels, 20)
	#c_data = report_components(rels)
	y_c_data.append(c_data)
	
generate_chart([(i, y_c_data[i]["nodes"]) for i in range(len(y_c_data))], "l_nodes")
generate_chart([(i, y_c_data[i]["avg_clustering"]) for i in range(len(y_c_data))], "l_avg_clustering")
generate_chart([(i, y_c_data[i]["center"]) for i in range(len(y_c_data))], "l_center")
generate_chart([(i, y_c_data[i]["periphery"]) for i in range(len(y_c_data))], "l_periphery")
