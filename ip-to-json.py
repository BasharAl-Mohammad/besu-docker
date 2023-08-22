import docker
import json
import os
from web3 import Web3

client = docker.from_env()

containers = client.containers.list()

container_info_dict = {}

for container in containers:
    container_name = container.name
    if container_name.startswith("node-"):
        container_info = container.attrs
        container_ip = container_info['NetworkSettings']['Networks']['besu-docker_besu-network']['IPAddress']
        
        private_key_path = f"{container_name}/data/key"
        


        if os.path.exists(private_key_path):
            with open(private_key_path, "r") as private_key_file:
                private_key = private_key_file.read()
                w3 = Web3(Web3.HTTPProvider(f'http://'+container_ip+':8545'))
                account = w3.eth.account.from_key(private_key)
            container_info_dict[container_name] = {
                "ip": container_ip,
                "private_key": private_key,
                "public_key": account.address
            }

with open("nodes_info.json", "w") as json_file:
    json.dump(container_info_dict, json_file, indent=4)

print("Node information with private keys saved to nodes_info.json")
