from server import NameNodeServer
import os
import logging
from dotenv import load_dotenv

def initialize()->tuple[int, int, int, str, str, str]:
    load_dotenv(dotenv_path="namenode/.env")
    ip_address = os.getenv("SERVER_HOST", "0.0.0.0")
    port = os.getenv("SERVER_PORT", "50051")
    workers = int(os.getenv("SERVER_WORKERS", "4"))

    return ip_address, port, workers

def main():
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    ip_address, port, max_workers = initialize()
    print(f"Starting server at {ip_address}:{port} with {max_workers} workers")

    server = NameNodeServer(ip_address, port, max_workers)

    server.start()

if __name__ == "__main__":
    main()