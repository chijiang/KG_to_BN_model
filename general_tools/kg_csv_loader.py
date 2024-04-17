from py2neo import Node, Relationship, Graph, Subgraph
import json

uri = "bolt://10.60.5.99:7687"
user = "neo4j"
password = "Boway123"

g = Graph(uri=uri, auth=(user, password))

with open("./nodes.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx in range(1, len(lines)):
    contents = lines[idx].replace(
        "，", ",").replace(
        "\n", "").replace(
        " ", "").replace(
        "True", "true").replace(
        "'", '"').split('\t')
    if len(contents) < 2:
        continue
    node_id = contents[0]
    name = contents[1]
    labels = contents[2].split(",")
    node = Node(
        id=node_id,
        Name=name
    )
    for label in labels:
        node.add_label(label)
    if len(contents) > 3:
        try:
            properties = json.loads(contents[3])
            write_props = {}
            for key, value in properties.items():
                write_props[key] = str(value)
            if write_props:
                node.update(write_props)
        except:
            pass
    try:
        g.merge(node, labels[0], "id")
    except Exception as e:
        print(f"Error merging nodes: {e}")

with open("./relationships.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

relationships = []
for idx in range(1, len(lines)):
    contents = lines[idx].replace("\n", "").replace(" ", "").split('\t')
    if len(contents) < 2:
        continue
    try:
        rel_id = contents[0]
        rel_label = contents[1]
        start_node = g.nodes.match(*contents[3].split(","), Name=contents[2]).first()
        end_node = g.nodes.match(*contents[5].split(","), Name=contents[4]).first()
    except:
        print(f"error parsing relationship: {contents}")
    try:
        relationship = Relationship(start_node, rel_label, end_node)
    except:
        print("error creating relationship")
        print(">>", contents[2:6])
        print(start_node, end_node)
        continue
    relationship.update({"id": rel_id})
    if len(contents) > 6:
        try:
            properties = json.loads(contents[6])
            write_props = {}
            for key, value in properties.items():
                write_props[key] = str(value)
            if write_props:
                relationship.update(write_props)
        except Exception as e:
            pass
    g.merge(relationship, rel_label, "id")
