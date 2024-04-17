import json
from py2neo import Node, Relationship, Graph, Subgraph
from tqdm import tqdm

uri = "bolt://10.60.5.99:7687"
user = "neo4j"
password = "Boway123"

g = Graph(uri=uri, auth=(user, password))

print("开始备份现有数据")
# Collecting all nodes information
print("读取全部实体数据...")
all_nodes: list[Node] = g.nodes.match().all()
all_node_str_list = []
for i in tqdm(range(len(all_nodes)), "备份实体"):
    node = all_nodes[i]
    id = str(node.get("NodeId")) if node.get("NodeId") else "-"
    name = str(node.get("Name"))
    labels = ",".join(list(node.labels))
    properties = {}
    for key in node.keys():
        if key != "Name" and key != "NodeId":
            properties[key] = node.get(key)
    properties = str(properties) if properties else ""
    node_str = "\t".join([id, name, labels, properties.replace("True", "true")])
    all_node_str_list.append(node_str.replace(" ", "").replace("\"", "").replace("'", '"'))
# Structuring node storing string
all_node_str = "\n".join(all_node_str_list).replace("-\t", "\t")


# Collecting all relationships informations
print("读取全部关系数据...")
all_relationships: list[Relationship] = g.relationships.match().all()
all_rel_str_list = []
for i in tqdm(range(len(all_relationships)), "备份关系"):
    relationship = all_relationships[i]
    id: str = str(relationship.get("RelationshipId")) if relationship.get("RelationshipId") else "-"
    relationship_type: str = ",".join(list(relationship.types()))
    start_node_name: str = str(relationship.start_node.get("Name"))
    start_node_label: str = ",".join(list(relationship.start_node.labels))
    end_node_name: str = str(relationship.end_node.get("Name"))
    end_node_label: str = ",".join(list(relationship.end_node.labels))
    properties = {}
    for key in relationship.keys():
        if key != "RelationshipId":
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

print("数据备份完成")


##################################################################
while True:
    delete_all = input("是否需要删除全部数据？ [y/N]")
    if delete_all.lower() in ["n", "y"]:
        break
    else:
        print("请键入 \"Y\" 或 \"N\"")
if delete_all.lower() == "y":
    print("继续执行程序将清空GraphDB数据")
    input("按键回车键继续...")
    g.run("MATCH ()-[r]-() DELETE r")
    print("所有关系已删除")
    input("按键回车键继续...")
    g.run("MATCH (n) DELETE n")
    print("所有节点已删除")
    input("按键回车键继续...")

###################################################################
print("正在导入新数据")

with open("./nodes.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

create_list = []
update_list = []
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
    node = None
    use_update = False
    if delete_all.lower() != "y":
        node = g.nodes.match(*labels, NodeId = node_id).first()
    if node: 
        use_update = True
    else:
        node = Node(
            NodeId=node_id,
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
        except Exception as e:
            pass
    if use_update:
        update_list.append(node)
    else:
        create_list.append(node)

try:
    if update_list:
        g.push(Subgraph(update_list))
except Exception as e:
    print(f"Error creating nodes: {e}")

try:
    if create_list:
        g.create(Subgraph(create_list))
except Exception as e:
    print(f"Error creating nodes: {e}")

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
        start_query = {}
        if contents[2]:
            start_query["NodeId"] = contents[2]
        if contents[3]:
            start_query["Name"] = contents[3]
        
        end_query = {}
        if contents[5]:
            end_query["NodeId"] = contents[5]
        if contents[6]:
            end_query["Name"] = contents[6]

        start_node = g.nodes.match(*contents[4].split(","), **start_query).first()
        end_node = g.nodes.match(*contents[7].split(","), **end_query).first()
    except:
        print(f"error parsing relationship: {contents}")
    try:
        relationship = Relationship(start_node, rel_label, end_node)
    except Exception as e:
        print(f"error creating relationship: {e}")
        print(">>", contents[:])
        print(start_node, end_node)
        continue
    relationship.update({"RelationshipId": rel_id})
    if len(contents) > 8:
        try:
            properties = json.loads(contents[8])
            write_props = {}
            for key, value in properties.items():
                write_props[key] = str(value)
            if write_props:
                relationship.update(write_props)
        except Exception as e:
            pass
    g.merge(relationship, rel_label, "RelationshipId")

print("数据导入完成")
input("按键回车键结束...")
