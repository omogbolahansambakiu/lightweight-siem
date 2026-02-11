
"""Syslog Receiver"""
import socket
import redis
import json
import os

def main():
    r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), decode_responses=True)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 5514))
    
    print("Syslog receiver listening on UDP 5514...")
    
    while True:  
        data, addr = sock.recvfrom(4096)
        print(f"Received from {addr}: {data}") 
        message = data.decode('utf-8', errors='ignore')
        
        event = {
            "message": message,
            "source_ip": addr[0],
            "source_type": "syslog"
        }
        
        r.lpush("events:raw", json.dumps(event))

if __name__ == "__main__":
    main()