# RAFT
## A simple, fast, and reliable implementation of the RAFT consensus algorithm in python

## How to use
### Install all the required dependencies using pip or your favorite package manager
### Python 3.6 or higher is required
### Dependencies: fastapi, uvicorn, threading, os, random, time, json, logging, socketserver, xmlrpc

### Configuration Setup
#### The configuration file is located in the config folder. The configuration file is a json file with the following structure:
```
{
  "host": "10.181.94.92",
  "port": 8080,
  "peers": [
    {"host": "10.181.88.30", "port": 8080}
  ],
  "election_timeout_range": [5000, 8000],
  "heartbeat_interval": 1000,
  "sleep_time": 200
}
```
#### The host and port are the host and port of the current node. The peers are the other nodes in the cluster. The election_timeout_range is the range of time in milliseconds that the election timeout will be randomly selected from. The heartbeat_interval is the interval in milliseconds that the leader will send heartbeats to the followers. The sleep_time is the time in milliseconds that the node will sleep for after each iteration of the main loop.


### Running the server
#### To run the server, simply run the following command:
```
python3 api.py
```