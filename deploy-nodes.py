import sys
import os
import shutil
import json
import subprocess
import glob
import re

def generate_docker_compose(num_nodes):
    with open("templates/docker_compose_template.yml", "r") as docker_compose_template_file:
        docker_compose_template = docker_compose_template_file.read()

    with open("templates/node_template.yml", "r") as node_template_file:
        node_template = node_template_file.read()

    compose_content = docker_compose_template

    with open("node-1/data/key.pub", "r") as enode:
        enode = enode.read()

    for node_num in range(2, num_nodes + 1):
        ip_suffix = node_num + 31
        compose_content += node_template.format(node_num=node_num, ip_suffix=ip_suffix,enode=enode[2:])
        
    with open("docker-compose.yml", "w") as file:
        file.write(compose_content)

    print("Docker Compose file generated successfully.")

def check_arguments ():
    if len(sys.argv) < 2:
        print('To few arguments; you need to specify 2 arguments')
        return None, []
    else:
        CONSENSUS = sys.argv[1]
        match CONSENSUS:
            case "QBFT":
                if len(sys.argv) < 6:
                    print('To few arguments; you need to specify 3 arguments for QBFT config')
                    return None, []
                nn=sys.argv[2]
                bps=sys.argv[3]
                epl=sys.argv[4]
                rts=sys.argv[5]
                try:
                    nn = int(nn)
                    bps = int(bps)
                    epl = int(epl)
                    rts = int(rts)
                    arr=[nn,bps,epl,rts]
                except ValueError:
                    print("Unable to parse all variables as integers")
                    sys.exit(1)
            case "IBFT":
                if len(sys.argv) < 6:
                    print('To few arguments; you need to specify 3 arguments for IBFT config')
                    return None, []
                nn=sys.argv[2]
                bps=sys.argv[3]
                epl=sys.argv[4]
                rts=sys.argv[5]
                try:
                    nn = int(nn)
                    bps = int(bps)
                    epl = int(epl)
                    rts = int(rts)
                    arr=[nn,bps,epl,rts]
                except ValueError:
                    print("Unable to parse all variables as integers")
                    sys.exit(1)
            case "CLIQUE":
                if len(sys.argv) < 5:
                    print('To few arguments; you need to specify 3 arguments for CLIQUE config')
                    return None, []
                nn=sys.argv[2]
                bps=sys.argv[3]
                epl=sys.argv[4]
                try:
                    nn = int(nn)
                    bps = int(bps)
                    epl = int(epl)
                    arr=[nn,bps,epl]
                except ValueError:
                    print("Unable to parse all variables as integers")
                    sys.exit(1)
            case "ETHASH":
                if len(sys.argv) < 4:
                    print('To few arguments; you need to specify 3 arguments for ETHASH config')
                    return None, []
                nn=sys.argv[2]
                fd=sys.argv[3]
                try:
                    nn = int(nn)
                    fd = int(fd)
                    arr=[nn,fd]
                except ValueError:
                    print("Unable to parse all variables as integers")
                    sys.exit(1)
            case _:
                print("Something is wrong")
        return CONSENSUS, arr

def clean_directory():
    if os.path.exists('genesis.json'):
        os.remove('genesis.json')

    if os.path.exists('IBFT-Network'):
        shutil.rmtree("IBFT-Network")

    if os.path.exists('QBFT-Network'):
        shutil.rmtree("QBFT-Network")
        
    if os.path.exists('Clique-Network'):
        shutil.rmtree("Clique-Network")



    if os.path.exists('genesis.json'):
        os.remove('genesis.json')

    for item in os.listdir():
        if item.startswith('node-') and os.path.isdir(item):
            try:
                shutil.rmtree(item)
                print(f"Deleted directory: {item}")
            except FileNotFoundError:
                print(f"Directory not found: {item}")
            except PermissionError:
                print(f"Permission denied for directory: {item}")

def generate_qbft_structure(ARGS):

    # aam yekhla2 files node-i
    for node_num in range(1, ARGS[0] + 1):
        node_dir = os.path.join(f"node-{node_num}")
        data_dir = os.path.join(node_dir, "data")
        os.makedirs(data_dir, exist_ok=True)

        print("Directory structure created successfully.")

    # aam yektob config li bdo yaaml generate lal networkFiles
    with open("templates/QBFTgenesis.json", 'r') as file:
        data = json.load(file)
    
    data['blockchain']['nodes']['count'] = ARGS[0]
    data['genesis']['config']['qbft']['blockperiodseconds'] = ARGS[1]
    data['genesis']['config']['qbft']['epochlength'] = ARGS[2]
    data['genesis']['config']['qbft']['requesttimeoutseconds'] = ARGS[3]

    with open("QBFTgenesis.json", 'w') as file:
            json.dump(data, file, indent=4)

    print("Genesis block data has been saved to 'QBFTgenesis'")

    #aam yaaml generate lal networkFiles
    config_file = "QBFTgenesis.json"
    command = f"besu/bin/besu operator generate-blockchain-config --config-file={config_file} --to=networkFiles --private-key-file-name=key"

    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)

        print("Command executed successfully:")
        print(result.stdout)

    except subprocess.CalledProcessError as e:
        print("Command failed with error:")
        print(e.stderr)

    keys_dir = 'networkFiles/keys'
    subdirectories = [name for name in os.listdir(keys_dir) if os.path.isdir(os.path.join(keys_dir, name))]
    
    shutil.copy(os.path.join('networkFiles', 'genesis.json'), os.getcwd())
    
    for i, address in enumerate(subdirectories, start=1):
        source_address_dir = os.path.join(keys_dir, address)
        destination_subdir = os.path.join(f'node-{i}', 'data')
        
        os.makedirs(destination_subdir, exist_ok=True)
        
        shutil.copy(os.path.join(source_address_dir, 'key'), destination_subdir)
        shutil.copy(os.path.join(source_address_dir, 'key.pub'), destination_subdir)

    shutil.rmtree('networkFiles')
    os.remove('QBFTgenesis.json')
    generate_docker_compose(ARGS[0])

def generate_ibft_structure(ARGS):
    base_dir = "IBFT-Network"
    os.makedirs(base_dir, exist_ok=True)
    for node_num in range(1, ARGS[0] + 1):
        node_dir = os.path.join(base_dir, f"Node-{node_num}")
        data_dir = os.path.join(node_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
    print("Directory structure created successfully.")

    with open("templates/IBFTgenesis.json", 'r') as file:
        data = json.load(file)
    
    data['blockchain']['nodes']['count'] = ARGS[0]
    data['genesis']['config']['ibft2']['blockperiodseconds'] = ARGS[1]
    data['genesis']['config']['ibft2']['epochlength'] = ARGS[2]
    data['genesis']['config']['ibft2']['requesttimeoutseconds'] = ARGS[3]

    with open("IBFTgenesis.json", 'w') as file:
            json.dump(data, file, indent=4)

    print("Genesis block data has been saved to 'IBFTgenesis'")

    config_file = "IBFTgenesis.json"
    command = f"besu/bin/besu operator generate-blockchain-config --config-file={config_file} --to=networkFiles --private-key-file-name=key"

    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)

        print("Command executed successfully:")
        print(result.stdout)

    except subprocess.CalledProcessError as e:
        print("Command failed with error:")
        print(e.stderr)

    keys_dir = 'networkFiles/keys'
    subdirectories = [name for name in os.listdir(keys_dir) if os.path.isdir(os.path.join(keys_dir, name))]
    
    shutil.copy(os.path.join('networkFiles', 'genesis.json'), os.getcwd())
    
    for i, address in enumerate(subdirectories, start=1):
        source_address_dir = os.path.join(keys_dir, address)
        destination_subdir = os.path.join(f'node-{i}', 'data')
        
        os.makedirs(destination_subdir, exist_ok=True)
        
        shutil.copy(os.path.join(source_address_dir, 'key'), destination_subdir)
        shutil.copy(os.path.join(source_address_dir, 'key.pub'), destination_subdir)

    shutil.rmtree('networkFiles')
    os.remove('IBFTgenesis.json')
    generate_docker_compose(ARGS[0])

def generate_clique_structure(ARGS):

    with open("templates/QBFTgenesis.json", 'r') as file:
        data = json.load(file)
    
    data['blockchain']['nodes']['count'] = ARGS[0]

    with open("QBFTgenesis.json", 'w') as file:
            json.dump(data, file, indent=4)

    print("Genesis block data has been saved to 'QBFTgenesis'")


    config_file = "QBFTgenesis.json"
    command = f"besu/bin/besu operator generate-blockchain-config --config-file={config_file} --to=networkFiles --private-key-file-name=key"

    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)

        print("Command executed successfully:")
        print(result.stdout)

    except subprocess.CalledProcessError as e:
        print("Command failed with error:")
        print(e.stderr)

    keys_dir = 'networkFiles/keys'
    subdirectories = [name for name in os.listdir(keys_dir) if os.path.isdir(os.path.join(keys_dir, name))]
    
    shutil.copy(os.path.join('networkFiles', 'genesis.json'), os.getcwd())
    
    for i, address in enumerate(subdirectories, start=1):
        source_address_dir = os.path.join(keys_dir, address)
        destination_subdir = os.path.join(f'node-{i}', 'data')
        
        os.makedirs(destination_subdir, exist_ok=True)
        
        shutil.copy(os.path.join(source_address_dir, 'key'), destination_subdir)
        shutil.copy(os.path.join(source_address_dir, 'key.pub'), destination_subdir)

    os.remove('QBFTgenesis.json')   
    
    with open("templates/CLIQUEgenesis.json", 'r') as file:
        data = json.load(file)
    
    data['config']['clique']['blockperiodseconds'] = ARGS[1]
    data['config']['clique']['epochlength'] = ARGS[2]
    pre = "0x0000000000000000000000000000000000000000000000000000000000000000"
    post = "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    dirs = os.listdir('networkFiles/keys')
    nodeAddrs = ""
    for dir in dirs:
        if '0x' in dir:
            nodeAddrs = nodeAddrs + dir[2:]
    data['extraData'] = pre + nodeAddrs + post

    shutil.rmtree('networkFiles')

    with open("genesis.json", 'w') as file:
            json.dump(data, file, indent=4)

    print("Genesis block data has been saved to 'genesis.json'")

    generate_docker_compose(ARGS[0])

def generate_ethash_structure(ARGS):
    
    shutil.copytree('templates/node-1', 'node-1')

    for node_num in range(2, ARGS[0] + 1):
        node_dir = os.path.join(f"node-{node_num}")
        data_dir = os.path.join(node_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
    print("Directory structure created successfully.")

    with open("templates/ETHASHgenesis.json", 'r') as file:
        data = json.load(file)
    data['config']['ethash']['fixeddifficulty'] = ARGS[1]
    with open("genesis.json", 'w') as file:
        json.dump(data, file, indent=4)

    with open("templates/docker_compose_template_ethash.yml", "r") as docker_compose_template_file:
        docker_compose_template = docker_compose_template_file.read()

    with open("templates/node_template_ethash.yml", "r") as node_template_file:
        node_template = node_template_file.read()

    compose_content = docker_compose_template

    with open("node-1/data/key.pub", "r") as enode:
        enode = enode.read()

    for node_num in range(2, ARGS[0] + 1):
        ip_suffix = node_num + 31

        compose_content += node_template.format(node_num=node_num, ip_suffix=ip_suffix,enode=enode[2:])
        
    with open("docker-compose.yml", "w") as file:
        file.write(compose_content)

    print("Docker Compose file generated successfully.")
    
    
if __name__ == '__main__':
    CONSENSUS, ARGS = check_arguments()
    clean_directory()

    match CONSENSUS:
        case "QBFT":
            generate_qbft_structure(ARGS)
        case "IBFT":
            generate_ibft_structure(ARGS)
        case "CLIQUE":
            generate_clique_structure(ARGS)
        case "ETHASH":
            generate_ethash_structure(ARGS)
        case _:
            print("ahha")
    

