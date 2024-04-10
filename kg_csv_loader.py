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
            node.update(properties)
        except:
            print(contents[3])
    g.merge(node, labels[0], "id")

with open("./relationships.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

relationships = []
for idx in range(1, len(lines)):
    contents = lines[idx].replace("\n", "").replace(" ", "").split('\t')
    rel_id = contents[0]
    rel_label = contents[1]
    start_node = g.nodes.match(*contents[3].split(","), Name=contents[2]).first()
    end_node = g.nodes.match(*contents[5].split(","), Name=contents[4]).first()
    try:
        relationship = Relationship(start_node, rel_label, end_node)
    except:
        print(">>", contents[2:6])
        print(start_node, end_node)
        continue
    relationship.update({"id": rel_id})
    if len(contents) > 6:
        try:
            properties = json.loads(contents[6])
            relationship.update(properties)
        except Exception as e:
            print(contents[6])
    g.merge(relationship, rel_label, "id")
