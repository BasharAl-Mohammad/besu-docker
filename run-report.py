import subprocess
import os
import json
import sys


def check_arguments ():
    
    return "hello"

# def run_command(command):
#     try:
#         subprocess.run(command, shell=True, check=True)
#     except subprocess.CalledProcessError as e:
#         print(f"Command failed with exit code {e.returncode}: {e.cmd}")
#         print(e.output.decode('utf-8'))
#         exit(1)

# with open('nodes_info.json', 'r') as file:
#     data = json.load(file)

# ip_list = []

# for node_name, node_data in data.items():
#     ip_address = node_data['ip']
#     ip_list.append(ip_address)

# # prepare NGINX config
# with open(os.path.join('templates/bpet-base'), 'r') as f:
#     nginx_config = f.read()
# upstream_servers = [f"    server {ip}:8546;" for ip in ip_list]
# upstream_servers = '\n'.join(upstream_servers)
# nginx_config = nginx_config.replace('# upstream servers', upstream_servers)
# with open(os.path.join('bpet'), 'w') as f:
#     f.write(nginx_config)
# # update NGINX config
# # set no password rules in /etc/sudoers.d (not necessary for cloud images)
# command = ['sudo', 'cp', 'bpet', '/etc/nginx/sites-enabled/bpet']
# proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd='../')
# # restart NGINX
# command = ['sudo', 'service', 'nginx', 'restart']
# proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd='lb_working_directory')

# # Command 1
# command1 = 'npx caliper bind --caliper-bind-sut besu:latest'
# run_command(command1)

# # Command 2
# command2 = 'npx caliper launch manager \
#     --caliper-workspace . \
#     --caliper-benchconfig benchmarks/scenario/simple/config.yaml \
#     --caliper-networkconfig config.json --caliper-flow-skip-install'
# run_command(command2)

if __name__ == '__main__':

    
    print(check_arguments())
