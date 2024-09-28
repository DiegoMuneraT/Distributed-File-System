import argparse
import os 
import logging
from client.client import Client
from dotenv import load_dotenv

load_dotenv("client/.env")

def main():
  namenodeIp= os.getenv("NAMENODE_IP")
  namenodePort=os.getenv("NAMENODE_PORT")

  log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  logging.basicConfig(level=logging.INFO, format=log_fmt)

  logger = logging.getLogger(__name__)

  parser = argparse.ArgumentParser(description="client")
  subparsers = parser.add_subparsers(dest="action", help="=> actions")
  subparsers.required = True

  subparsers.add_parser("ls", help="list files on distributed file system")

  download_parser = subparsers.add_parser("open", help="open file from server")
  download_parser.add_argument("-out", "--root_dir", required=True, type=str, help="root client output directory")
  download_parser.add_argument("-f", "--filename", required=True, type=str, help="file name to open")

  upload_parser = subparsers.add_parser("create",help="create and upload file to server")
  upload_parser.add_argument("-out", "--root_dir", required=True, type=str, help="root client output directory")
  upload_parser.add_argument("-in", "--in_dir", required=True, type=str, help="root client input directory ")
  upload_parser.add_argument("-f", "--filename", required=True, type=str, help="file name to create")

  append_parser = subparsers.add_parser("append",help="Append new data to a file stored in the system")
  append_parser.add_argument("-out", "--root_dir", required=True, type=str, help="root client output directory")
  append_parser.add_argument("-in", "--in_dir", required=True, type=str, help="root client input directory ")
  append_parser.add_argument("-f", "--filename", required=True, type=str, help="local file with new data")
  append_parser.add_argument("-fdfs", "--filenamedfs", required=True, type=str, help="DFS stored file to append new data into")


  args = parser.parse_args()

  root_dir = getattr(args, "root_dir", "")
  in_dir = getattr(args, "in_dir", "")
  
  client = Client(namenodeIp, namenodePort,root_dir,in_dir)

  action = args.action
  if action == "open":
    client.open(args.filename)
  elif action== "create":
    client.create(args.filename)
  elif action== "ls":
    client.list_index()
  elif action== "append":
    client.append(args.filename, args.filenamedfs)
  else:
    logger.error("no such action " + action)

if __name__ == "__main__":
  main()