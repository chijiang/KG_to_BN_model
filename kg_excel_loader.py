import os
from py2neo import Node, Subgraph, Graph, Relationship

uri = "bolt://10.60.5.99:7687"
user = "neo4j"
password = "Boway123"

graph = Graph(uri=uri, auth=(user, password))

file_names = os.listdir("./kg_files")

BELONG_TO = Relationship.type("属于")

for fname in file_names:
    path = os.path.join("./kg_files", fname)
    with open(path, "r", encoding="utf-8") as f:
        content = f.readlines()
    name = fname.split("_")[0]
    sql_field = "_".join(fname.replace(".txt", "").split("_")[1:])
    line_content = content[0].replace("\n", "").replace(" ", "")
    keys = line_content.split("\t")
    node = Node("Ontology")
    node.update({
        "Name": name,
        "SQLField": sql_field
    })
    node.add_label("graph_1")
    second_layer_nodes = []
    relationships = []
    for i in range(len(keys)):
        if not keys[i]:
            continue
        node.update({f"key_{i+1}": keys[i]})
        sub_node = Node(name)
        sub_node.update({
            "Name": keys[i]
        })
        sub_node.add_label("graph_2")
        relationships.append(BELONG_TO(sub_node, node))
        second_layer_nodes.append(sub_node)
    graph.merge(node, "Ontology", "Name")
    sub_gr = Subgraph(second_layer_nodes, relationships)
    graph.merge(sub_gr, name, "Name")
    




