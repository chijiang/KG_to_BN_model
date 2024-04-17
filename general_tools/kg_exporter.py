from py2neo import Node, Relationship, Graph

uri = "bolt://10.60.5.99:7687"
user = "neo4j"
password = "Boway123"

g = Graph(uri=uri, auth=(user, password))

# Collecting all nodes information
all_nodes: list[Node] = g.nodes.match().all()
all_node_str_list = []
for node in all_nodes:
    id = str(node.get("id")) if node.get("id") else "-"
    name = str(node.get("Name"))
    labels = ",".join(list(node.labels))
    properties = {}
    for key in node.keys():
        if key != "Name" and key != "id":
            properties[key] = node.get(key)
    properties = str(properties) if properties else ""
    node_str = "\t".join([id, name, labels, properties.replace("True", "true")])
    all_node_str_list.append(node_str.replace(" ", "").replace("\"", "").replace("'", '"'))
# Structuring node storing string
all_node_str = "\n".join(all_node_str_list).replace("-\t", "\t")


# Collecting all relationships informations
all_relationships: list[Relationship] = g.relationships.match().all()
all_rel_str_list = []
for relationship in all_relationships:
    id: str = str(relationship.get("id")) if relationship.get("id") else "-"
    relationship_type: str = ",".join(list(relationship.types()))
    start_node_name: str = str(relationship.start_node.get("Name"))
    start_node_label: str = ",".join(list(relationship.start_node.labels))
    end_node_name: str = str(relationship.end_node.get("Name"))
    end_node_label: str = ",".join(list(relationship.end_node.labels))
    properties = {}
    for key in relationship.keys():
        if key != "id":
            properties[key] = relationship.get(key)
    properties = str(properties) if properties else ""
    rel_str = "\t".join([
        id, 
        relationship_type, 
        start_node_name, 
        start_node_label,
        end_node_name,
        end_node_label,
        properties.replace("True", "true")])
    all_rel_str_list.append(rel_str.replace(" ", "").replace("\"", "").replace("'", '"'))

all_rel_str = "\n".join(all_rel_str_list).replace("-\t", "\t")
    

########## Exporting data to txt file ##########
import os
try:
    os.mkdir("./exported")
except Exception as e:
    print(e)
with open("./exported/nodes.txt", "w", encoding="utf-8") as f:
    f.write("ID	名称	标签	属性\n" + all_node_str)
with open("./exported/relationships.txt", "w", encoding="utf-8") as f:
    f.write("ID	关系类型	起始名称	起点标签	终点名称	终点标签	节点属性\n" + all_rel_str)


print("数据导出完成")
input("按键回车键结束...")