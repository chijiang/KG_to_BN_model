from py2neo import Graph

uri = "bolt://10.60.5.99:7687"
user = "neo4j"
password = "Boway123"

graph = Graph(uri, auth=(user, password))

target_nodes = graph.nodes.match('Target').all()
print(target_nodes)

target_nodes = list(graph.nodes.match('Factor').limit(3))
print(target_nodes)

print(graph.schema.node_labels)
print(graph.schema.relationship_types)

cypher_ = '''MATCH path=(m)-[:Impact]->(n) RETURN path, m, n'''
print(graph.query(cypher_).to_data_frame())

nodes = graph.nodes.match(Name='冷却强度').all()
nodes[0].update({'No': 'testWrite'})
graph.push(nodes[0])

print(graph.nodes.match(Name='冷却强度').all())

graph.query('''MATCH path = (m:)''')