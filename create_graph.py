from py2neo import Graph, Node, Subgraph, Relationship


uri = "bolt://10.60.5.99:7687"
user = "neo4j"
password = "Boway123"

g = Graph(uri=uri, auth=(user, password))

existed_nodes = g.nodes.match().all()
names = []
for node in existed_nodes:
    names.append(node.get("Name"))

# read 'csv'
with open('./graph.csv', 'r', encoding='utf-8') as f:
    content = f.readlines()

new_nodes = []
for line in content:
    if "{" in line:
        node_content_str = line.replace("\n", "").replace("{", "").replace("}", "")
        node_info_seg = node_content_str.split(",")
        node = Node("Factor")
        for node_info in node_info_seg:
            kv = node_info.split(":")
            k = kv[0]
            v = kv[1] if len(kv) == 2 else ""
            node.update({k: v})
        if node.get("Name") not in names:
            new_nodes.append(node)

sub = Subgraph(new_nodes)
g.create(sub)


existed_nodes = g.nodes.match().all()
relations = []
target_node = g.nodes.match(Name="气泡失效").first()
for node in existed_nodes:
    if node.get("Name") != "气泡失效":
        g.create(Relationship(node, "Impact", target_node))

g.relationships.match(nodes=(target_node))


g.create(Relationship(g.nodes.match(Name="镁").first(), "Impact", target_node))