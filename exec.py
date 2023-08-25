import socket
import subprocess


hostname = socket.gethostname()
# host_ip = socket.gethostbyname(socket.gethostname())
host_ip = subprocess.run(['ip', 'route', 'get', '192.168.23.64'], stdout=subprocess.PIPE)
host_ip = host_ip.stdout.decode().split(' ')
host_ip = host_ip[host_ip.index('src') + 1]