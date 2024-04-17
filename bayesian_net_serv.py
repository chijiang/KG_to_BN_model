

import pandas as pd
from neo4j_connection import Neo4jManip
from mysql_connection import MySqlManip
from models.bayes_net import BNCreator
from log import logger as log

def create_bayesian_network(
        neo4j_conn: Neo4jManip,
        mysql_conn: MySqlManip,
        targets: list[str] = [], 
        relationship_type: str = "", 
        leaf_type: str = "",
        name_key: str = "Name"
        ):
    network_graph, sql_info = neo4j_conn.read_bayesian_graph(
        targets = targets, 
        relationship_type = relationship_type, 
        leaf_type = leaf_type,
        name_key = name_key)
    
    # Reading data from database
    readable_sql_columns = [str(sql_info[col].get("sql_column")) 
                            for col in sql_info 
                            if col != "table_name" and 
                            sql_info[col].get("sql_column")]
    raw_data = mysql_conn.load_data_to_dataframe(sql_info["table_name"], readable_sql_columns)
    raw_data = raw_data.fillna(0)
    readable_columns = [variable for variable in sql_info.keys() 
                         if variable != "table_name" and sql_info[variable]["sql_column"] in raw_data.columns]
    # raw_data = raw_data[[sql_info[variable]["sql_column"] for variable in readable_columns]]
    raw_data.columns = [variable for variable in readable_columns]

    valid_graph = []
    for pair in network_graph:
        if pair[0] in readable_columns and pair[1] in readable_columns:
            valid_graph.append(pair)

    # Forming data (discrete)
    raw_data = mysql_conn.load_data_to_dataframe(sql_info["table_name"])
    raw_data = raw_data.dropna()
    series = []

    for variable in readable_columns:
        if variable == "table_name":
            continue
        ser = raw_data[sql_info[variable]["sql_column"]]
        ser.name = variable
        if sql_info[variable]["type"] == "target":
            ser = pd.cut(ser,2,
                labels=["FineBatch", "BadBatch"])
        else:
            try:
                ser = pd.cut(
                    ser.astype('float'), 
                    [-float("inf"), 
                    float(sql_info[variable]["lower"]), 
                    float(sql_info[variable]["upper"]),
                    float("inf")],
                    labels=["lower", "medium", "upper"])
            except Exception as e:
                log.error(f"{variable}: {e}")
        series.append(ser)

    data = pd.DataFrame(series).T

    # Building model
    model = BNCreator(valid_graph, node_info = sql_info)
    model.fit(data)
    # Update prior probabilities
    for target_name in targets:
        if target_name:
            freq_values = {}
            pri_prob = []
            # frequency count
            value_counts = data[target_name].value_counts()
            for class_name in value_counts.index:
                freq_values[class_name] = value_counts.loc[class_name] / sum(value_counts)
            # update cpds
            all_states = model.states[target_name]
            for state in all_states:
                pri_prob.append(freq_values[state])
            model.update_single_cpd(target_name, pri_prob)
    model.fit_update(data)
    return model
    

def thresholds_define(neo4j_conn: Neo4jManip, mysql_conn: MySqlManip, targets: list[str]):
    for target in targets:
        nodes = []
        for record in list(neo4j_conn.query(
            f'''MATCH (n) - [] -> (:QualityDefect{{Name:"{target}"}}) WHERE n.SQLField <> "" and n.SQLTable <> " " return n'''
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
                upper_limit = float(max_value) + 1
            except Exception as e:
                log.error(f"{e}")
                continue
            # Write to NEO4J
            node.update({"UpperValue": upper_limit, "LowerValue": lower_limit})
            nodes.append(node)

        neo4j_conn.push_node_updates(nodes)
    