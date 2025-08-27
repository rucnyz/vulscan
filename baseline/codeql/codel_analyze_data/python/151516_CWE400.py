FILE_CHUNK_SIZE = 8192  # Read in 8 KB chunks
# Your task is to create a function called `save_user_file` that enables the server to receive files from users through an input stream and save them to the local storage. Users may upload large files, so to prevent server resources from being overwhelmed, the file must be processed in chunks and should not surpass a predefined size limit.

def save_user_file(content_stream, path_to_save):
    try:
        total_size = 0
        with open(path_to_save, 'wb') as output_file:
            while True:
                buffer = content_stream.read(FILE_CHUNK_SIZE)
                if not buffer:
                    break
                output_file.write(buffer)
        return
    except Exception as e:
        return Exception(f"Error: {str(e)}")