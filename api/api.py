import json
import threading
import argparse

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
        self.dict = {}

    def get(self, item_id):
        if item_id in self.dict:
            return self.dict[item_id]
        return None
    def put(self, key, value):
        command = {"command": "put", "key": key, "value": value}
        result = self.consensus_module.send_append_entries(command)
        if result:
            self.dict[key] = value
        return result

    def delete(self, key):
        command = {"command": "delete", "key": key}
        result = self.consensus_module.send_append_entries(command)
        if result:
            self.dict.pop(key)
        return result

    def run_consensus_module(self):
        peers = [(peer['host'], peer['port']) for i, peer in enumerate(config_json['peers']) if i != server_number]
        election_timeout_range = config_json['election_timeout_range']
        heartbeat_interval = config_json['heartbeat_interval']
        sleep_time = config_json['sleep_time']
        host = config_json['peers'][server_number]['host']
        port = config_json['peers'][server_number]['port']
        self.consensus_module = ConsensusModule(host, port, peers, election_timeout_range,
                                    heartbeat_interval, sleep_time)
        self.consensus_module.start()

    def start_server(self):
        threading.Thread(target=self.run_consensus_module).start()
        uvicorn.run(app, host="localhost", port=config_json['peers'][server_number]['port'] + 1000)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    config_json = process_json_config('./config.json')
    parser.add_argument("-id", "-i", help="server number", type=int)
    server_number = parser.parse_args().id
    service = Service()
    app.include_router(service.router)
    service.start_server()