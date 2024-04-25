from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
from pydantic import BaseModel
from bayesian_net_serv import create_bayesian_network, thresholds_define
from mysql_connection import MySqlManip
from neo4j_connection import Neo4jManip
from fastapi.templating import Jinja2Templates
from log import logger as log
from contextlib import asynccontextmanager
import pickle

mysql_conn = MySqlManip(
    user='root', host='10.60.5.99', port=3306, password='Boway@123', database='IOT'
)
neo4j_conn = Neo4jManip(
    uri = "bolt://10.60.5.99:7687",
    user = "neo4j",
    password = "Boway123"
)

global global_model_base
@asynccontextmanager
async def lifespan(app: FastAPI):
    global global_model_base
    try:
        global_model_base = pickle.load(open("model_base.pickle", "rb"))
        log.info(f"model base loaded: {global_model_base}")
    except Exception as e:
        log.error(f"model base loading error: {e}")
        global_model_base = {}
    yield
    pickle.dump(
        global_model_base,
        open("model_base.pickle", "wb")
    )

app = FastAPI(lifespan=lifespan)

# Mount frontend codes
templates = Jinja2Templates(directory="./frontend/build")
app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

@app.get("/")
async def items(request: Request):
    return templates.TemplateResponse(
        'index.html',
        {
            'request': request
        },
    )

class BayesianNetReq(BaseModel):
    targets: list[str]
    evidence: Optional[dict] = {}

@app.post("/bayesian_net")
async def bayesian_net(
    req: BayesianNetReq, 
    build: int = 1,
    writeKG: int = 0,
    postProb: int = 1,
    predict: int = 0,
    retrain: int = 0):

    if not build:
        network_graph, _ = neo4j_conn.read_bayesian_graph(
        target_name = req.targets)
        return ORJSONResponse(network_graph, 200)
    
    bn = global_model_base.get(str(sorted(req.targets)))
    if not bn or retrain:
        log.info("start building")
        bn = create_bayesian_network(
            neo4j_conn,mysql_conn,req.targets,"影响"
        )
    else:
        network_graph, sql_info = neo4j_conn.read_bayesian_graph(
            targets = req.targets, 
            relationship_type = "影响")
        readable_columns = mysql_conn.load_data_to_dataframe(sql_info["table_name"]).dropna(how='all', axis=1).columns
        valid_edges = [ pair
            for pair in network_graph 
                if pair[0] in readable_columns and 
                   pair[1] in readable_columns
            ]
        for pair in valid_edges:
            if pair not in list(bn.edges):
                bn = create_bayesian_network(
                    neo4j_conn,mysql_conn,req.targets,"影响"
                )
                break
    
    global_model_base[str(sorted(req.targets))] = bn

    resp = {}
    if postProb:
        log.info("calculating posterior prob")
        posterior_probabilities = bn.get_posterior_probabilities(req.targets)
        resp = {"后验概率": {k[0]: v for k, v in posterior_probabilities.items()}}
    
        log.info("writing to gdb")
        if writeKG:
            for start_end, matrix in posterior_probabilities.items():
                start = start_end[0]
                end = start_end[1]
                neo4j_conn.update_relationship(
                    start_name = start, 
                    end_name = end, 
                    key = "probabilities", 
                    content = matrix
                )

    log.info("making prediction")
    if predict:
        try:
            pred = bn.make_inference(
                evidence = req.evidence, 
                target="")
            resp["prediction"] = pred
        except:
            pass
    return ORJSONResponse(resp, 200)

class DfPredictionReq(BaseModel):
    table_name: str
    target_list: list
    lot_no: str

@app.post("/make_prediction")
async def make_prediction(
    req: DfPredictionReq
):
    model = global_model_base.get(str(sorted(req.target_list)))
    if not model:
        return ORJSONResponse(
            "Model doesn't exist",
            400
        )
    data = mysql_conn.load_data_to_dataframe(
        req.table_name,
        where={"lot_no": req.lot_no}
    )
    ans = model.predict_along_data_frame(data)
    return ORJSONResponse(
        ans.to_dict(), 200
    )

@app.post("/set_threshold")
async def set_threshold(
    req: BayesianNetReq
):
    thresholds_define(neo4j_conn, mysql_conn, req.targets)
    return ORJSONResponse("ok", 200)

if __name__ == "__main__":
    config = json.load(open("./settings.json"))
    uvicorn.run(
        app, host=config["server"]["host"], port=config["server"]["port"]
    )