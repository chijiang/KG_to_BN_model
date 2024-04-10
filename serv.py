from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
import uvicorn
import json

app = FastAPI()

@app.post("/hello")
async def read_root():
    return ORJSONResponse({"message": "hello"}, 200)

if __name__ == "__main__":
    config = json.load(open("./settings.json"))
    uvicorn.run(
        app, host=config["server"]["host"], port=config["server"]["port"]
    )