import subprocess
import os
import json
import sys
import time
import docker
from web3 import Web3
import re
import shutil

def setup_test ():
    CONSENSUS = sys.argv[1]
    nn=int(sys.argv[2])
    txr=0
    match CONSENSUS:
        case "QBFT":
            bps=int(sys.argv[3])
            epl=int(sys.argv[4])
            rts=int(sys.argv[5])
            txr=int(sys.argv[6])
            command = f"python3 deploy-nodes.py QBFT {nn} {bps} {epl} {rts}"
            subprocess.run(command,shell=True)
            testname=CONSENSUS+'_'+str(nn)+'_'+str(bps)+'_'+str(txr)
        case "IBFT":
            bps=int(sys.argv[3])
            epl=int(sys.argv[4])
            rts=int(sys.argv[5])
            txr=int(sys.argv[6])
            command = f"python3 deploy-nodes.py IBFT {nn} {bps} {epl} {rts}"
            subprocess.run(command,shell=True)
            testname=CONSENSUS+'_'+str(nn)+'_'+str(bps)+'_'+str(txr)
        case "CLIQUE":
            bps=int(sys.argv[3])
            epl=int(sys.argv[4])
            txr=int(sys.argv[5])
            command = f"python3 deploy-nodes.py CLIQUE {nn} {bps} {epl}"
            subprocess.run(command,shell=True)
            testname=CONSENSUS+'_'+str(nn)+'_'+str(bps)+'_'+str(txr)
        case "ETHASH":
            fd=int(sys.argv[3])
            txr=int(sys.argv[4])
            command = f"python3 deploy-nodes.py ETHASH {nn} {fd}"
            subprocess.run(command,shell=True)
            testname=CONSENSUS+'_'+str(nn)+'_'+str(fd)+'_'+str(txr)
        case _:
            txr=1000
            subprocess.run(['python3','deploy-nodes.py','QBFT','4','2','30000','4'])
            testname="QBFT_4_2_1000"
    return testname, txr

def containers_info():
    client = docker.from_env()
    containers = client.containers.list()
    container_info_dict = {}
    for container in containers:
        container_name = container.name
        if container_name.startswith("node-") and container_name!="node-1":
            container_info = container.attrs
            container_ip = container_info['NetworkSettings']['Networks']['besu-docker_besu-network']['IPAddress']
            container_id = container_info['Id']
            private_key_path = f"{container_name}/data/key"
            if os.path.exists(private_key_path):
                with open(private_key_path, "r") as private_key_file:
                    private_key = private_key_file.read()
                    w3 = Web3(Web3.HTTPProvider(f'http://'+container_ip+':8545'))
                    account = w3.eth.account.from_key(private_key)
                container_info_dict[container_name] = {
                    "id": container_id,
                    "ip": container_ip,
                    "private_key": private_key,
                    "public_key": account.address
                }

    with open("nodes_info.json", "w") as json_file:
        json.dump(container_info_dict, json_file, indent=4)

    print("Node information with private keys saved to nodes_info.json")

def update_nginx():
    with open('nodes_info.json', 'r') as json_file:
        data = json.load(json_file)

    ip_addresses = [node["ip"] for node in data.values()]

    upstream_block = "\n".join([f"\t\tserver {ip}:8546;" for ip in ip_addresses])

    with open('nginx/nginx.conf', 'r') as nginx_file:
        nginx_config = nginx_file.read()

    updated_nginx_config = re.sub(r'upstream besunodes {.*?}', f'upstream besunodes {{\n{upstream_block}\n}}', nginx_config, flags=re.DOTALL)

    with open('nginx/nginx.conf', 'w') as nginx_file:
        nginx_file.write(updated_nginx_config)

    print("nginx.conf file updated successfully.")

def save_logs(test_directory):
    client = docker.from_env()
    all_containers = client.containers.list(all=True)
    container_name_prefix = "node-"

    for container in all_containers:
        if container.name.startswith(container_name_prefix):
            container_name = container.name
            log_file_name = test_directory+'/'+container_name+'.txt'
            try:
                with open(log_file_name, 'wb') as log_file:
                    log_file.write(container.logs())
                print(f"Logs for container '{container_name}' saved to '{log_file_name}'")
            except docker.errors.APIError as e:
                print(f"Error saving logs for container '{container_name}': {e}")

if __name__ == '__main__':
    for x in range(1,5):
        # #Create artifacts
        testname, txr = setup_test()
        subprocess.run(['docker','compose','up','-d'])
        time.sleep(60)
        containers_info()
        time.sleep(20)
        update_nginx()
        subprocess.run(['docker','compose', '-f', './nginx/docker-compose.yml', 'up', '-d'])
        time.sleep(30)
        subprocess.run(['docker','compose', '-f', './caliper/docker-compose.yml', 'up'])
        time.sleep(10)
        subprocess.run(['docker','compose','stop'])
        test_directory = 'reports/'+testname+'/'+str(x)
        if not os.path.exists(test_directory):
            os.makedirs(test_directory)
            print(f"Directory '{test_directory}' created successfully.")
        else:
            shutil.rmtree(test_directory)
            os.makedirs(test_directory)
            print(f"Directory '{test_directory}' created successfully.")
        shutil.move('caliper/report.html', test_directory)
        save_logs(test_directory=test_directory)
        subprocess.run(['docker','compose', '-f', './caliper/docker-compose.yml', 'down'])
        subprocess.run(['docker','compose', '-f', './nginx/docker-compose.yml', 'down'])
        # subprocess.run(['docker','compose','stop'])
        subprocess.run(['docker','compose','down'])

