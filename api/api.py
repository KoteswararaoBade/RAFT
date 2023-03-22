import json
import threading

import uvicorn
from fastapi import FastAPI

from consensus.module import ConsensusModule

app = FastAPI()
consensus = None

@app.get("/get/{item_id}")
def get():
    return {"Hello": "World"}


@app.get("/put/{key}/{value}")
def put(key: str, value: str):
    # result = consensus.appendEntries()
    return {"key": key, "value": value}

def process_json_config(filename):
    with open(filename) as f:
        config = json.load(f)
    return config

def run_consensus_module():
    config_json = process_json_config('../config.json')
    peers = [(peer['host'], peer['port']) for peer in config_json['peers']]
    election_timeout_range = config_json['election_timeout_range']
    heartbeat_interval = config_json['heartbeat_interval']
    sleep_time = config_json['sleep_time']
    consensus = ConsensusModule(config_json['host'], config_json['port'], peers, election_timeout_range,
                                heartbeat_interval, sleep_time)
    consensus.start()

def start_server():
    threading.Thread(target=run_consensus_module).start()
    uvicorn.run(app, host="localhost", port=8000)

if __name__ == '__main__':
    start_server()