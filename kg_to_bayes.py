from pgmpy.models import BayesianNetwork  
from pgmpy.factors.discrete import TabularCPD  
from pgmpy.inference import VariableElimination
  
# 定义贝叶斯网络的变量  
weather = ['W1', 'W2']  # 天气：晴天和雨天  
umbrella = ['U1', 'U2']  # 是否带伞：带伞和不带伞  
  
# 创建贝叶斯网络模型  
model = BayesianNetwork([('W', 'U')])  
  
# 定义条件概率分布  
# 天气的概率分布  
cpd_weather = TabularCPD(variable='W', variable_card=2, values=[[0.6], [0.4]])  
  
# 带伞在给定天气下的条件概率分布  
cpd_umbrella_given_weather = TabularCPD(variable='U', variable_card=2,  
                                          values=[[0.2, 0.8],  # P(U1|W1), P(U2|W1)  
                                                   [0.8, 0.2]],  # P(U1|W2), P(U2|W2)  
                                              evidence=['W'],  
                                              evidence_card=[2])  
  
# 添加条件概率分布到模型中  
model.add_cpds(cpd_weather, cpd_umbrella_given_weather)  
  
# 查询概率  
infer = VariableElimination(model)  
# print("P(W1):", infer.query('W', 'W1'))  
# print("P(U1|W2):", infer.query('U', 'U1', evidence={'W': 'W2'}))  
# print("P(U1, W2):", infer.query(['U', 'W'], ['U1', 'W2']))  
print("P(U1):", infer.query({'W': 'W2', 'U': 'U1'}))