from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
import numpy as np

class BNCreator():
    def __init__(self, features: list, targets: list) -> None:
        self.model = BayesianNetwork(
            [(x, t) for x in features for t in targets]
        )
    
    def update_cpd(self, tag_name, values: dict):
        cpd = TabularCPD(tag_name, len(values), 
                         np.array(list(values.values())).reshape(-1,1), 
                         state_names={tag_name: list(values.keys())})
        self.model.add_cpds(cpd)
        
    def fit(self, data):
        self.model.fit(data)
        
    def predict_probability(self, data):
        return self.model.predict_probability(data)
    
    def save_model(self, name: str):
        self.model.save(
            f'./model_archive/{name}.bif', 'bif'
        )