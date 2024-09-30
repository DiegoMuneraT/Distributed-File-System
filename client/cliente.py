import logging
import os
import sys
from threading import Thread
from typing import List

import grpc

import splitter
import unificator

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Protos directory to the Python path
protos_dir = os.path.join(parent_dir, "protos")
sys.path.append(protos_dir)

from protos.file_pb2 import ReadFileReq, WriteFileReq, FileOpenReq, FileCreateReq, Empty
from protos.file_pb2_grpc import FileStub, NameNodeServiceStub

logger = logging.getLogger(__name__)

GRPC_OPTIONS = [
    ('grpc.max_receive_message_length', 134217758),
    ('grpc.max_send_message_length', 134217758)
]

class Client:
  def __init__(self, ip_address: str, port: int, root_dir: str, in_dir: str):
      self.__ip_address = ip_address
      self.__port = port
      self.__files_directory = root_dir
      self.__in_dir = in_dir
      self._PIECE_SIZE_IN_BYTES = 1024 * 1024  # 128MB

  def _create_name_node_client(self, host: str, port: int):
      """Create a gRPC client for the NameNode."""
      socket = f"{host}:{port}"
      channel: grpc.Channel = grpc.insecure_channel(socket, options=GRPC_OPTIONS)
      return NameNodeServiceStub(channel)

  def _create_datanode_client(self, socket: str):
      """Create a gRPC client for the DataNode."""
      channel: grpc.Channel = grpc.insecure_channel(socket, options=GRPC_OPTIONS)
      return FileStub(channel)
  
  def __upload_to_name_node(self, socket: str, filename: str, chunk_name: str, pathpart=None) -> None:
    """
    Upload a chunk to the NameNode.

    Args:
        socket (str): The socket address of the DataNode.
        filename (str): The name of the file.
        chunk_name (str): The name of the chunk.
        pathpart (str, optional): The path to the chunk file. Defaults to None.
    """
    file_path = pathpart if pathpart else os.path.join(self.__files_directory, filename, chunk_name)
    
    try:
        with open(file_path, "rb") as fh:
            piece = fh.read(self._PIECE_SIZE_IN_BYTES)
            if not piece:
                raise EOFError("Reached end of file while reading chunk.")
            req = WriteFileReq(filename=filename, chunkname=chunk_name, buffer=piece)
            datanode_stub = self._create_datanode_client(socket=socket)
            logger.info(f"Trying to create file on datanode - {socket}")
            # Assuming there is a method to write the file on the datanode_stub
            datanode_stub.write(req)
    except EOFError as e:
        logger.error(f"EOFError: {e}")
    except grpc.RpcError as e:
        logger.error(f"gRPC error: {e.details()}")
    except Exception as e:
        logger.error(f"Internal error: {e}")

  def __saving_chunk(self, response_bytes: bytes, out_file_name: str, out_file_dir: str) -> None:
    """Save a chunk of data to the local filesystem."""
    try:
        # Si el directorio no existe, lo crea para guardar las particiones del archivo.
        directory = os.path.join(self.__files_directory, out_file_dir)
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, out_file_name), "wb") as fh:
            fh.write(response_bytes.buffer)
    except Exception as e:
        #print("\nError while saving chunk: {e}\n")
        logger.error(f"Error while saving chunk: {e}")

  def open(self, file_name: str) -> None:
      """Open a file from the NameNode and read its chunks in parallel."""
      namenode_stub = self._create_name_node_client(self.__ip_address, self.__port)
      logger.info("Calling NameNode server...")
      req = FileOpenReq(filename=file_name)
      try:
          response_stream = namenode_stub.open(req)
          threads: List[Thread] = []
          for response in response_stream:
              localization = response.localization
              chunkname = response.chunkname
              thread = Thread(target=self.read, args=(localization, file_name, chunkname,))
              thread.start()
              threads.append(thread)
          for thread in threads:
              thread.join()
          unificator.unificator(split_dir=self.__files_directory, filename=file_name)
      except grpc.RpcError as e:
          logger.error(f"gRPC error: {e.details()}")
      except Exception as e:
          logger.error(f"Unexpected error: {str(e)}")

  def read(self, socket: str, file_name: str, chunk_name: str) -> None:
    """Read a chunk from the DataNode and save it locally."""
    try:
        datanode_stub = self._create_datanode_client(socket=socket)
        logger.info(f"Downloading chunk {chunk_name} from file: {file_name} in socket: {socket}")
        req = ReadFileReq(filename=file_name, chunkname=chunk_name)
        # Remote Call procedure to datanode download
        response_bytes = datanode_stub.read(req)
        self.__saving_chunk(response_bytes, chunk_name, file_name)
        logger.info(f"Successfully downloaded file: {file_name} from socket: {socket}.")
    except grpc.RpcError as e:
        logger.error(f"gRPC error: {e.details()}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
  
  def create(self, file_name: str) -> None:
    """Create a file by splitting it into chunks and uploading them to the NameNode."""
    try:
        namenode_stub = self._create_name_node_client(self.__ip_address, self.__port)
        splitter.hadoop_style_split(
            filename=file_name,
            in_path=self.__in_dir,
            out_path=self.__files_directory,
            chunk_size=self._PIECE_SIZE_IN_BYTES
        )
        directory = os.path.join(self.__files_directory, file_name)
        chunks_list = os.listdir(directory)
        chunks_number = len(chunks_list)
        req = FileCreateReq(filename=file_name, chunks_number=chunks_number, operation="Create")
        response_stream = namenode_stub.create(req)

        chunk_index = 0
        threads = []
        for response in response_stream:
            if response.HasField('warning_message'):
                raise Exception(response.warning_message.message)
            localization = f"{response.datanode_list.localization}"
            chunk_name = chunks_list[chunk_index]
            thread = Thread(target=self.__upload_to_name_node, args=(localization, file_name, chunk_name))
            thread.start()
            threads.append(thread)
            chunk_index += 1

        for thread in threads:
            thread.join()
    except grpc.RpcError as e:
        logger.error(f"gRPC error: {e.details()}")
    except Exception as e:
        logger.error(f"Internal error: {e}")
    
  def list_index(self) -> None:
      """List the index of files from the NameNode."""
      try:
          namenode_stub = self._create_name_node_client(self.__ip_address, self.__port)
          req = Empty()
          response_stream = namenode_stub.listin(req)
          for content in response_stream:
              print(f"- {content.name}")
      except grpc.RpcError as e:
          logger.error(f"gRPC error: {e.details()}")
      except Exception as e:
          logger.error(f"Internal error: {e}")

  def create_appends(self, file_name: str, appends_dir: str) -> None:
      """
      Append chunks to an existing file in the NameNode.

      Args:
          file_name (str): The name of the file to append to.
          appends_dir (str): The directory containing the chunks to append.
      """
      try:
          namenode_stub = self._create_name_node_client(self.__ip_address, self.__port)
          chunks_list = os.listdir(appends_dir)
          chunks_number = len(chunks_list)
          req = FileCreateReq(filename=file_name, chunks_number=chunks_number, operation="Append")
          response_stream = namenode_stub.create(req)
          
          chunk_index = 0
          threads = []
          for response in response_stream:
              localization = f"{response.datanode_list.localization}"
              chunk_name = chunks_list[chunk_index]
              part_dir = os.path.join(appends_dir, chunk_name)
              thread = Thread(target=self.__upload_to_name_node, args=(localization, file_name, chunk_name, part_dir))
              thread.start()
              threads.append(thread)
              chunk_index += 1
          
          for thread in threads:
              thread.join()
      except grpc.RpcError as e:
          logger.error(f"gRPC error: {e.details()}")
      except Exception as e:
        logger.error(f"Internal error: {e}")

  def append(self, file_name: str, file_name_dfs: str) -> None:
      """
      Append data to an existing file in the DFS.

      Args:
          file_name (str): The name of the local file to append.
          file_name_dfs (str): The name of the file in the DFS.
      """
      namenode_stub = self._create_name_node_client(self.__ip_address, self.__port)
      logger.info("Calling NameNode server...")
      req = FileOpenReq(filename=file_name_dfs)

      try:
          response_stream = namenode_stub.open(req)
          for response in response_stream:
              localization = f"{response.localization}"
              chunk_name = f"{response.chunkname}"
              last_response = (localization, chunk_name)

          if last_response is not None:
              # Call the read function only once using information from the last response
              self.read(socket=last_response[0], file_name=file_name_dfs, chunk_name=last_response[1])

          downloaded_chunk_path = os.path.join(self.__files_directory, file_name_dfs)
          re_split_path = os.path.join(self.__files_directory, "re-split")

          splitter.hadoop_style_split(
              filename=chunk_name,
              in_path=downloaded_chunk_path,
              out_path=re_split_path,
              chunk_size=self._PIECE_SIZE_IN_BYTES,
              second_filename=file_name,
              second_in_path=self.__in_dir
          )

          directorio_destino = os.path.join(re_split_path, file_name)
          self.create_appends(file_name_dfs, directorio_destino)

      except grpc.RpcError as e:
          logger.error(f"gRPC error: {e.details()}")
      except Exception as e:
          logger.error(f"Internal error: {e}")
      