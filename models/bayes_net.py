from collections import defaultdict
import pgmpy.models as pgm
import pandas as pd


class BNCreator(pgm.BayesianNetwork):

    def __init__(self, ebunch=None, latents=set(), node_info: dict = {}):
        super().__init__(ebunch, latents)
        self.node_info = node_info

    def update_node_info(self, node_info: dict):
        self.node_info.update(node_info)

    def make_inference(self, evidence: dict, target: str):
        evid = {}
        for column, value in evidence.items():
            if column in self.node_info:
                if self.node_info[column]["type"] == "factor":
                    classified_value = (
                        "upper"
                        if value > float(self.node_info[column]["upper"])
                        else (
                            "lower"
                            if value < float(self.node_info[column]["lower"])
                            else "medium"
                        )
                    )
                    if classified_value not in self.states[column]:
                        classified_value = self.states[column][0]
                    evid[column] = {1: classified_value}
                else:
                    evid[column] = {1: "BadBatch"} if value == 1 else {1: "FineBatch"}
            else:
                evid[column] = {1: value}
        input_df = pd.DataFrame(evid)
        pred = self.predict_probability(input_df)
        pred = pred.loc[:, pred.columns.str.contains(target)]

        ans = defaultdict(dict)
        for col in pred.columns:
            col_name, col_proper = "_".join(col.split("_")[:-1]), col.split("_")[-1]
            ans[col_name][col_proper] = (
                pred.loc[:, col].to_numpy()[0] if pred.loc[:, col].to_numpy() else 0.
            )
        return ans
    
    def get_posterior_probabilities(self, targets: list[str]):
        posterior_probabilities = {}
        for target in targets:
            target_columns = [f"{target}_" + x for x in self.states[target]]
            for key, value in self.states.items():
                if key in targets:
                    continue
                posterior_probability = self.predict_probability(pd.DataFrame.from_dict({key: value}))[target_columns]
                posterior_probabilities[(key, target)] = {value[i] : posterior_probability.iloc[i].to_dict() for i in range(len(value))}
        return posterior_probabilities

    def update_single_cpd(self, variable: str, values: list[float]):
        if sum(values) != 1:
            print("Error: total probability not equal to 1")
            return
        
        for cpd in self.get_cpds():
            if cpd.variable == variable:
                new_cpd = cpd
                for i in range (new_cpd.values.shape[0]):
                    if i < len(values):
                        new_cpd.values[i,:] = values[i]
                self.add_cpds(new_cpd)
                break

    def save_model(self, name: str):
        self.save(f"./model_archive/{name}.bif", "bif")
