from mysql_connection import MySqlManip
from neo4j_connection import Neo4jManip
import pandas as pd

conn = MySqlManip(
    user='root', host='10.60.5.99', port=3306, password='Boway@123', database='IOT'
)

conn.create_params_table()
# conn.make_model_table(
#     table_name = "ml_data_test",
#     param_columns=["aaa", "bbb"],
#     target_colums=["cc", "dd"]
# )

data = conn.load_data_to_dataframe('device_4_bubble_cleaned_data_bayes')
data.dropna()
selected_labels = ["cool_strength_total_mean_3min", "temp_3m_jiaozhu", "label"]
data = data[selected_labels]

length = len(data)
cool_strength_upper_threshold = sorted(data["cool_strength_total_mean_3min"].tolist())[int(length * 4 / 5)]
cool_strength_lower_threshold = sorted(data["cool_strength_total_mean_3min"].tolist())[int(length * 1 / 5)]
temp_upper_threshold = sorted(data["temp_3m_jiaozhu"].tolist())[int(length * 5 / 6)]
temp_lower_threshold = sorted(data["temp_3m_jiaozhu"].tolist())[int(length * 1 / 5)]

data["cool_strength_total_mean_3min"] = pd.cut(
    data["cool_strength_total_mean_3min"],
    [-float('inf'), cool_strength_lower_threshold, cool_strength_upper_threshold, float('inf')],
    labels=["IncompleteCooled","SolidCooled","OverCooled"])

data["temp_3m_jiaozhu"] = pd.cut(
    data["temp_3m_jiaozhu"],
    [-float('inf'), temp_lower_threshold, temp_upper_threshold, float('inf')],
    labels=["UnderHeated","WellHeated","OverHeated"])

data["label"] = pd.cut(
    data["label"],
    2,
    labels=["FineBatch","BadBatch"])

from models.bayes_net import BNCreator
bn = BNCreator(["cool_strength_total_mean_3min", "temp_3m_jiaozhu"], 'label')

bn.update_cpd(
    "temp_3m_jiaozhu",
    {
        "UnderHeated": 0.15,
        "WellHeated": 0.79,
        "OverHeated": 0.06
    }
)

bn.update_cpd(
    "cool_strength_total_mean_3min",
    {
        "IncompleteCooled": 0.15,
        "SolidCooled": 0.79,
        "OverCooled": 0.06
    }
)

bn.update_cpd(
    "label",
    {
        "FineBatch": 0.02,
        "BadBatch": 0.98,
    }
)

bn.model.fit(data)

bn.model.predict_probability(data[["cool_strength_total_mean_3min", "label"]].loc[[10000]])

# g = Neo4jManip(uri = "bolt://10.60.5.99:7687", user = "neo4j", password = "Boway123")
# path = g.find_all_around(target_name="气泡缺陷")

# dict(g.find_all_around(target_name="气泡缺陷").loc[1, ]['n'])

# g.update_node("气泡缺陷", "SQLField", "bubble__")
# g.graph.nodes.match(Name="气泡缺陷").all()
