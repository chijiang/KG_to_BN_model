from collections import defaultdict
import pgmpy.models as pgm
import pgmpy.factors.discrete as pgdisc
import numpy as np
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

    def update_cpd(self, tag_name, values: dict):
        cpd = pgdisc.TabularCPD(
            tag_name,
            len(values),
            np.array(list(values.values())).reshape(-1, 1),
            state_names={tag_name: list(values.keys())},
        )
        self.model.add_cpds(cpd)

    def save_model(self, name: str):
        self.model.save(f"./model_archive/{name}.bif", "bif")
