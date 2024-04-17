from mysql_connection import MySqlManip
from neo4j_connection import Neo4jManip


mysql_conn = MySqlManip(
    user='root', host='10.60.5.99', port=3306, password='Boway@123', database='IOT'
)
neo4j_conn = Neo4jManip(
    uri = "bolt://10.60.5.99:7687",
    user = "neo4j",
    password = "Boway123"
)

nodes = []
for record in list(neo4j_conn.query(
    f'''MATCH (n) WHERE n.SQLField <> "" and n.SQLTable <> " " return n'''
)):
    node = record["n"]
    sql_table = node.get("SQLTable")
    sql_field = node.get("SQLField")
    # MIN MAX
    try:
        min_value = mysql_conn.fetch(f'''SELECT MIN({sql_field}) FROM {sql_table}''')[0][0][0]
        max_value = mysql_conn.fetch(f'''SELECT MAX({sql_field}) FROM {sql_table}''')[0][0][0]
        phase_width = (float(max_value) - float(min_value)) / 3
        lower_limit = float(min_value) + float(phase_width)
        upper_limit = lower_limit + phase_width
    except Exception as e:
        print(e)
        continue
    # Write to NEO4J
    node.update({"UpperValue": upper_limit, "LowerValue": lower_limit})
    nodes.append(node)

neo4j_conn.push_node_updates(nodes)

