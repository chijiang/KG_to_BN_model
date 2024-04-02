import pgmpy.models as pgm
import pgmpy.factors.discrete as pgdisc
import numpy as np
import pandas as pd

class BNCreator(pgm.BayesianNetwork):
    
    def __init____init__(self, ebunch=None, latents=set()):
        super().__init__(ebunch, latents)
    
    def make_inference(self, evidence: dict, targets: list, node_infos: dict = {}):
        evid = {}
        for column, value in evidence.items():
            if column in node_infos:
                if node_infos[column]["type"] == "factor":
                    classified_value = "upper" if value > float(node_infos[column]["upper"]) else "lower" if value < float(node_infos[column]["lower"]) else "medium"
                    evid[column] = {1: classified_value}
                else:
                    evid[column] = {1: "BadBatch"} if value == 1 else {1: "FineBatch"}
            else:
                evid[column] = {1: value}
        input_df = pd.DataFrame(evid)
        
        return input_df
    
    def update_cpd(self, tag_name, values: dict):
        cpd = pgdisc.TabularCPD(tag_name, len(values), 
                         np.array(list(values.values())).reshape(-1,1), 
                         state_names={tag_name: list(values.keys())})
        self.model.add_cpds(cpd)
        
    def predict_probability(self, data):
        return self.model.predict_probability(data)
    
    def save_model(self, name: str):
        self.model.save(
            f'./model_archive/{name}.bif', 'bif'
        )