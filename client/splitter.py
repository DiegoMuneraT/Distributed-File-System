import os
import logging

def append_file_contents(file1, file2):
    """
    Appends the contents of file2 to file1.

    :param file1: Path to the first file.
    :param file2: Path to the second file.
    """
    try:
        with open(file1, 'ab') as f1:
            with open(file2, 'rb') as f2:
                f1.write(f2.read())
    except IOError as e:
        logging.error(f"Error appending file contents: {e}")


def delete_files_in_folder(folder_path):
    """
    Deletes all files in the specified folder.

    :param folder_path: Path to the folder.
    """
    try:
        files = os.listdir(folder_path)
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
    except OSError as e:
        logging.error(f"Error deleting files in folder: {e}")

def hadoop_style_split(filename, in_path, out_path, chunk_size, second_filename=None, second_in_path=None):
    """
    Splits a large file into smaller chunks and stores them in a directory.

    :param filename: Name of the file to split.
    :param in_path: Input directory path.
    :param out_path: Output directory path.
    :param chunk_size: Size of each chunk in bytes.
    :param second_filename: Optional second file to append before splitting.
    :param second_in_path: Path to the optional second file.
    """
    logger = logging.getLogger(__name__)    
    directorio_origen = f"{in_path}/{filename}"
    chunk_num = 1

    if second_filename and second_in_path:
        chunk_num = int(filename[-5])
        directorio_destino = f"{out_path}/{second_filename}"
        if not os.path.exists(directorio_destino):
            os.makedirs(directorio_destino)
        delete_files_in_folder(directorio_destino)
        directorio_origen = f"{in_path}/{filename}"
        directorio_origen2 = f"{second_in_path}/{second_filename}"
        append_file_contents(directorio_origen, directorio_origen2)
        
        with open(directorio_origen, 'rb') as full_file:

            chunk = full_file.read(chunk_size)
            
            while chunk:
                nombre_parte = f"{directorio_destino}/part{chunk_num:04d}"
                with open(nombre_parte+".txt", 'wb') as archivo_parte:
                    archivo_parte.write(chunk)
                chunk_num += 1
                chunk = full_file.read(chunk_size)


    else:
        directorio_destino = f"{out_path}/{filename}"
        with open(directorio_origen, 'rb') as archivo:
            if not os.path.exists(directorio_destino):
                os.makedirs(directorio_destino)
            delete_files_in_folder(directorio_destino)
            chunk = archivo.read(chunk_size)
            
            while chunk:
                nombre_parte = f"{directorio_destino}/part{chunk_num:04d}"
                with open(nombre_parte+".txt", 'wb') as archivo_parte:
                    archivo_parte.write(chunk)
                    #if chunk_num == 1:
                        #print(chunk)
                #print(f"Se creó el chunk {nombre_parte}")
                
                chunk_num += 1
                chunk = archivo.read(chunk_size)


if __name__ == "__main__":
    filename = "Shakira.pdf"  # Nombre del archivo
    chunk_size = 1024 * 1024 * 128# Para bloques de 1MB
    hadoop_style_split(filename, chunk_size)