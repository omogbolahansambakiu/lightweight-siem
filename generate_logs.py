
import socket
import time
import random
from datetime import datetime

def send_syslog(message, host='127.0.0.1', port=514):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(f"<34>{message}".encode(), (host, port))
    sock.close()

# Realistic data
attackers = ['185.234.218.45', '45.33.32.156', '91.121.87.45', '198.20.69.74']
internal_ips = [f'192.168.1.{i}' for i in range(1, 50)]
users = ['admin', 'root', 'deploy', 'postgres', 'ubuntu', 'user1']

scenarios = [
    # Brute force attack
    lambda: f"sshd[{random.randint(1000,9999)}]: Failed password for {random.choice(users)} from {random.choice(attackers)} port 22 ssh2",
    
    # Successful login
    lambda: f"sshd[{random.randint(1000,9999)}]: Accepted password for {random.choice(users)} from {random.choice(internal_ips)} port 22 ssh2",
    
    # Sudo usage
    lambda: f"sudo[{random.randint(1000,9999)}]: {random.choice(users)} : TTY=pts/0 ; PWD=/home/{random.choice(users)} ; USER=root ; COMMAND=/bin/bash",
    
    # Web attack
    lambda: f"nginx[{random.randint(1000,9999)}]: {random.choice(attackers)} - GET /{random.choice(['admin', '.env', 'wp-admin', 'phpmyadmin', 'config.php'])} HTTP/1.1 404",
    
    # Firewall block
    lambda: f"kernel: UFW BLOCK IN=eth0 SRC={random.choice(attackers)} DST={random.choice(internal_ips)} PROTO=TCP DPT={random.randint(1,9999)}",
    
    # Malware
    lambda: f"antivirus: Malware detected: Trojan.GenericKD.{random.randint(10000,99999)} in /tmp/{random.choice(['update', 'install', 'patch'])}.sh",
]

print("Generating realistic security logs...")
print("Press Ctrl+C to stop\n")

count = 0
while True:
    scenario = random.choice(scenarios)
    message = f"{datetime.now().strftime('%b %d %H:%M:%S')} webserver {scenario()}"
    send_syslog(message)
    print(f"Sent: {message}")
    count += 1
    time.sleep(random.uniform(0.1, 1.0))  # Random delay between logs