import numpy as np
import pandas as pd
from azure.storage.blob import BlobServiceClient
import warnings
from joblib import dump
from pgmpy.models import BayesianNetwork
import random
import os


warnings.filterwarnings(action='ignore', category=UserWarning)


class AzureBlobStorage:

    def __init__(self, connection_string):
        """
        创建 Azure Blob 存储客户端
        """
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    def upload_blob(self, container_name, blob_name, data):
        """
        上传数据到 Blob
        """
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(data, overwrite=True)

    def download_blob(self, container_name, blob_name):
        """
        下载 Blob 中的数据
        """
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        data = blob_client.download_blob().readall()
        return data

    def list_blobs(self, container_name):
        """
        列出 Blob 容器中的所有 Blob
        """
        container_client = self.blob_service_client.get_container_client(container_name)
        blobs = []
        try:
            for blob in container_client.list_blobs():
                blobs.append(blob.name)
        except Exception as e:
            print("error", e)
        return blobs

    def list_blobs(self, container_name, blob_name):
        """
        列出 Blob 容器中的所有 Blob
        """
        container_client = self.blob_service_client.get_container_client(container_name)
        blobs = []
        try:
            for blob in container_client.list_blobs(name_starts_with=blob_name):
                blobs.append(blob.name)
        except Exception as e:
            print("error", e)
        return blobs

    def list_container(self):
        container_list = []
        for container in self.blob_service_client.list_containers():
            container_list.append(container.name)
            return container_list

    def create_container(self, container_name):
        """
        创建 Blob 容器
        """
        container_client = self.blob_service_client.create_container(container_name)
        return container_client

    def delete_container(self, container_name):
        """
        删除 Blob 容器
        """
        container_client = self.blob_service_client.get_container_client(container_name)
        container_client.delete_container()

    def delete_blob(self, container_name, blob_name):
        """
        删除 Blob
        """
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.delete_blob()

    def upload_blob_file(self, container_name, blob_path, local_file_path):
        """
        把本地的文件上传到Blob storage的指定路径
        """
        container_client = self.blob_service_client.get_container_client(container_name)
        with open(file=os.path.join(local_file_path), mode="rb") as data:
            blob_client = container_client.upload_blob(name=blob_path, data=data, overwrite=True)


class BlobConfig:
    source_conn_str = "DefaultEndpointsProtocol=https;AccountName=devce2iotcoreadls01;AccountKey=r6kwbfAFw8XGYrzn4HprzHmeF9F62veBFy4PPN0rEiWiMGEBLhIEd2k7iiTrJLyoXREouMGN1HED+AStW05bwA==;EndpointSuffix=core.chinacloudapi.cn"
    source_container_name = "devce2iotcoreadls01"

    target_conn_str = "DefaultEndpointsProtocol=https;AccountName=devce2iotcoreadls02;AccountKey=1ni1XJ3eZpXLMvLjtPcz8x489HajofT1USgdFeGNuzaS2XXCBZiS8tyQu5zisMpAobhVA4LW5oTv+ASt5ufs2A==;EndpointSuffix=core.chinacloudapi.cn"
    target_container_name = "devce2iotcoreadls02"

mat_b = []

df_relations = pd.read_excel("Appearance_Priori_Probabilities.xlsx", sheet_name="Directions")

for i, row in df_relations.iterrows():
     mat_b.append((row['Source'], row['Target']))

bayesian_model = BayesianNetwork(mat_b)
dic_priori_tables = {
    "Smoothness_DryingTime": pd.read_excel("Appearance_Priori_Probabilities.xlsx", sheet_name="DryingTime_Smoothness", engine='xlrd'),
    "Smoothness_PauseTime": pd.read_excel("Appearance_Priori_Probabilities.xlsx", sheet_name="PauseTime_Smoothness"),
    "Smoothness_LastSmoothness": pd.read_excel("Appearance_Priori_Probabilities.xlsx", sheet_name="LastSmoothness_Smoothness"),
    "Smoothness_DrumspeedS": pd.read_excel("Appearance_Priori_Probabilities.xlsx", sheet_name="DrumspeedS_Smoothness"),
    "Smoothness_DrumspeedN": pd.read_excel("Appearance_Priori_Probabilities.xlsx", sheet_name="DrumspeedN_Smoothness"),
    "Smoothness_Syrup": pd.read_excel("Appearance_Priori_Probabilities.xlsx", sheet_name="Syrup_Smoothness")
    }

dic_root_priori_probabilities = {}
for i, row in pd.read_excel("Appearance_Priori_Probabilities.xlsx", sheet_name="Node_Priories").iterrows():
    if row['Node'] in dic_root_priori_probabilities:
        dic_root_priori_probabilities[row['Node']][row['Class']] = row['Probability']
    else:
        dic_root_priori_probabilities[row['Node']] = {row['Class']: row['Probability']}

dic_relation_priori_probabilities = {
    k: {
        c: {
            row['Target_Class']: row[c] for i, row in dic_priori_tables[k].iterrows()
        } for c in dic_priori_tables[k].columns if c != 'Target_Class'
    } for k in dic_priori_tables
}

Nodes = ['DryingTime', 'PauseTime', 'LastSmoothness', 'DrumspeedN', 'DrumspeedS', 'Syrup', 'Smoothness']
Target_Class = ['MeetTarget', 'SmallGap', 'LargeGap']

i = 0
mat_records = []

while i < 10 ** 6:
    dic_line = {
        node: random.choices(
            list(dic_root_priori_probabilities[node].keys()), list(dic_root_priori_probabilities[node].values())
        )[0] for node in Nodes if node != 'Smoothness'
    }
    dic_line['Smoothness'] = random.choices(
        Target_Class,
        [
            np.prod([
                dic_relation_priori_probabilities['Smoothness_' + node][dic_line[node]][v] for node in Nodes if
                node != 'Smoothness'
            ]) for v in Target_Class
        ]
    )[0]
    mat_records.append([dic_line[node] for node in Nodes])
    i += 1

df_bayesian_priori = pd.DataFrame.from_records(mat_records, columns=Nodes)
bayesian_model.fit(df_bayesian_priori)

Blob_Source = AzureBlobStorage(connection_string=BlobConfig.source_conn_str)
Blob_Target = AzureBlobStorage(connection_string=BlobConfig.target_conn_str)

Blob_Dir_Str = 'Curated Data/SON/BayesianNetwork/'

for node in Nodes:
    if node == 'Smoothness':
        continue
    df_cp_posteriori = bayesian_model.predict_probability(
        pd.DataFrame.from_records([[x] for x in list(dic_root_priori_probabilities[node].keys())], columns=[node])
    )[['Smoothness_MeetTarget', 'Smoothness_SmallGap', 'Smoothness_LargeGap']]
    df_cp_posteriori['SourceNode_Class'] = list(dic_root_priori_probabilities[node].keys())
    df_cp_posteriori = df_cp_posteriori[['SourceNode_Class', 'Smoothness_MeetTarget', 'Smoothness_SmallGap', 'Smoothness_LargeGap']]
    df_cp_posteriori.set_index('SourceNode_Class', drop=True, inplace=True)
    print (df_cp_posteriori)
    print ('''Source: %s, Target: Smoothness'''%(node))
    print (df_cp_posteriori.T)
    print ()
    Blob_Target.upload_blob(BlobConfig.target_container_name,
                            Blob_Dir_Str + '''Source_%s_Target_Smoothness.csv'''%(node),
                            df_cp_posteriori.T.to_csv(index=True).encode('utf-8'))

dump(bayesian_model, "appearance_bayesian_model.joblib")
# AzureBlobStorage.upload_blob(Blob_Target, Blob_Dir_Str + "gum_bayesian_model.joblib", "gum_bayesian_model.joblib")

Blob_Target.upload_blob_file(
    BlobConfig.target_container_name, blob_path=Blob_Dir_Str + "appearnace_bayesian_model.joblib",
    local_file_path="appearance_bayesian_model.joblib"
)
