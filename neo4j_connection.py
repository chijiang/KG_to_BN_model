from collections import defaultdict
from py2neo import Graph, Subgraph, Node
import pandas as pd


class Neo4jManip():
    def __init__(self, uri: str = "http://localhost:7474", user:str = "", password:str = "") -> None:
        self.graph = Graph(uri, auth=(user, password))

    def find_all_around(self, target_name: str = "", relationship_type: str = "", leaf_type: str = ""):
        relationship_type = f":{relationship_type}" if relationship_type else "*"
        leaf_type = f":{leaf_type}" if leaf_type else leaf_type

        cypher_head = f'''MATCH r = (m{leaf_type}) - [{relationship_type}] -> (n) '''
        cypher_condition = f'''WHERE n.Name = '{target_name}' ''' if target_name else ""
        cypher_return = f'''RETURN r as Relationship, m as Roots, n as Leaves'''
        return self.graph.query(cypher_head + cypher_condition + cypher_return).to_data_frame()

    def update_node(self, name: str, key: str, value):
        node: Node = self.graph.nodes.match(Name=name).first()
        node.update({key: value})
        self.graph.push(node)

    def update_nodes(self, data_dict : dict):
        ''' data_dict = {
        "foo": {
            "tag": value
            }
        }
        '''
        nodes = []
        for k, v in data_dict.items():
            node: Node = self.graph.nodes.match(Name = k).first()
            node.update(v)
            nodes.append(node)
        sub_graph = Subgraph(nodes)
        self.graph.push(sub_graph)
        
    def read_bayesian_graph(self, 
                        target_name: str = "", 
                        relationship_type: str = "", 
                        leaf_type: str = "",
                        name_key: str = "Name") -> list:
        '''
        RETURNS \n
        {pairs} - [(A, B), (B, C), (A, C)] \n
        {sql_info} - {'table_name': 'device_4_bubble_cleaned_data_bayes', 
                     '气泡失效': {'type': 'target', 'sql_column': 'label'}, ... }
        '''
        ## Query for all nodes / relationships around target node
        raw_pairs = []  # pairs in form of  (start_node) - [] -> (end_node)
        latents = set() # set of latent nodes   # !! Latent feature removed. 
                                                # Using latents will seriously slow down 
                                                # operation speed
        sql_info = {}   # information extraction for each nodes
        
        # Query from neo4j
        res = self.find_all_around(
            target_name = target_name, 
            relationship_type = relationship_type, 
            leaf_type = leaf_type)
        # Relationships
        for relations in res["Relationship"]:
            relation = relations.relationships[0]
            pair = (
                relation.start_node.get(name_key),
                relation.end_node.get(name_key),
            )
            # pairs with latents
            raw_pairs.append(pair)
            
            ## START NODE
            # If node is ontology, add to latents
            if relation.start_node.has_label("Ontology"):
                latents.add(relation.start_node.get(name_key))
            # If node is target, store its SQL field
            elif relation.start_node.has_label("Target"):
                sql_info.update({"table_name": relation.start_node.get("SQLTable")})
                sql_info.update({
                    relation.start_node.get(name_key): {
                        "type": "target",
                        "sql_column": relation.start_node.get("SQLField")
                    }
                })
            # If node is factor, stor its SQL field and its thresholds
            else:
                sql_info.update({"table_name": relation.start_node.get("SQLTable")})
                sql_info.update({
                    relation.start_node.get(name_key): {
                        "type": "factor",
                        "sql_column": relation.start_node.get("SQLField"),
                        "upper": relation.start_node.get("UpperValue"),
                        "lower": relation.start_node.get("LowerValue")
                    }
                })
            
            ## END NODE
            # If node is ontology, add to latents
            if relation.end_node.has_label("Ontology"):
                latents.add(relation.end_node.get(name_key))
            # If node is target, store its SQL field
            elif relation.end_node.has_label("Target"):
                sql_info.update({"table_name": relation.end_node.get("SQLTable")})
                sql_info.update({
                    relation.end_node.get(name_key): {
                        "type": "target",
                        "sql_column": relation.end_node.get("SQLField")
                    }
                })
            # If node is factor, stor its SQL field and its thresholds
            else:
                sql_info.update({"table_name": relation.end_node.get("SQLTable")})
                sql_info.update({
                    relation.end_node.get(name_key): {
                        "type": "factor",
                        "sql_column": relation.end_node.get("SQLField"),
                        "upper": relation.end_node.get("UpperValue"),
                        "lower": relation.end_node.get("LowerValue")
                    }
                })
                
        # remove latents, all nodes point to Ontology(latent) will 
        # be redirected to the next target node
        latents_targets = defaultdict(list)
        for pair in raw_pairs:
            if pair[0] in latents:
                latents_targets[pair[0]].append(pair[1])
        pairs = []
        for pair in raw_pairs:
            if pair[0] in latents:
                continue
            if pair[1] in latents:
                pairs.extend([(pair[0], x) for x in latents_targets[pair[1]]])
            else:
                pairs.append(pair)
        return pairs, sql_info
    
    def add_node_type(self, key: str, new_type: str):
        nodes: list[Node] = self.graph.nodes.match(Name = key).all()
        new_nodes = []
        for node in nodes:
            node.add_label(new_type)
            new_nodes.append(node)
        subgraph = Subgraph(new_nodes)
        self.graph.push(subgraph)
        
    def remove_node_type(self, key: str, del_type: str):
        self.graph.query(
            f'''
            MATCH (n {{Name: '{key}'}})
            REMOVE n:{del_type}
            '''
        )