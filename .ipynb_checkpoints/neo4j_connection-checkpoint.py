from py2neo import Graph


class Neo4jManip():
    def __init__(self, uri: str = "http://localhost:7474", user:str = "", password:str = "") -> None:
        self.graph = Graph(uri, auth=(user, password))

    def find_all_around(self, target_name: str = "", relationship_type: str = "", leaf_type: str = ""):
        relationship_type = f":{relationship_type}" if relationship_type else relationship_type
        leaf_type = f":{leaf_type}" if leaf_type else leaf_type

        cypher_head = f'''MATCH r = (m{leaf_type}) - [{relationship_type}] -> (n) '''
        cypher_condition = f'''WHERE n.Name = '{target_name}' ''' if target_name else ""
        cypher_return = f'''RETURN r, m, n'''
        return self.graph.query(cypher_head + cypher_condition + cypher_return).to_data_frame()

    def update_node(self, name: str, key: str, value):
        node = self.graph.nodes.match(Name=name).first()
        node.update({key: value})
        self.graph.push(node)

    def update_nodes(self, data_dict : dict):
        ''' data_dict = {
        "foo": {
            "tag": value
            }
        }'''
        