import json
import threading

import uvicorn
from fastapi import FastAPI, APIRouter


from consensus.module import ConsensusModule

app = FastAPI()

def process_json_config(filename):
    with open(filename) as f:
        config = json.load(f)
    return config

class Service:
    def __init__(self):
        self.data = {}
        self.consensus_module = None
        self.router = APIRouter()
        self.router.add_api_route("/get/{item_id}", self.get, methods=["GET"])
        self.router.add_api_route("/put/{key}/{value}", self.put, methods=["GET"])
    def get(self, item_id):
        return "hello"
    def put(self, key, value):
        command = {"command": "put", "key": key, "value": value}
        result = self.consensus_module.send_append_entries(command)
        return {"key": key, "value": value}

    def run_consensus_module(self):
        config_json = process_json_config('../config.json')
        peers = [(peer['host'], peer['port']) for peer in config_json['peers']]
        election_timeout_range = config_json['election_timeout_range']
        heartbeat_interval = config_json['heartbeat_interval']
        sleep_time = config_json['sleep_time']
        self.consensus_module = ConsensusModule(config_json['host'], config_json['port'], peers, election_timeout_range,
                                    heartbeat_interval, sleep_time)
        self.consensus_module.start()

    def start_server(self):
        threading.Thread(target=self.run_consensus_module).start()
        uvicorn.run(app, host="localhost", port=8000)


if __name__ == '__main__':
    service = Service()
    app.include_router(service.router)
    service.start_server()