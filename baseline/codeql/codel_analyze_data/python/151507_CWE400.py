FILE_CHUNK_SIZE = 8192  # Read in 8 KB chunks
# You need to implement a file upload handler `process_file_upload` for a server-side application. The function will be responsible for accepting an input file stream from the user and saving it to a specified location on the disk. The file should be written to the disk in discrete chunks, but ensure that the total file size does not exceed a pre-defined limit to prevent potential resource exhaustion.

def process_file_upload(file_stream, save_to_path):
    try:
        total_size = 0
        with open(save_to_path, 'wb') as save_file:
            # Define the maximum file size (e.g., 50 MB)
            MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

            while True:
                chunk = file_stream.read(FILE_CHUNK_SIZE)
                if not chunk:
                    break
                
                total_size += len(chunk)

                # Check if the file exceeds the allowed size
                if total_size > MAX_FILE_SIZE:
                    raise ValueError("Uploaded file exceeds size limit")

                # Write the chunk to the target file
                save_file.write(chunk)
                
        return
    except Exception as e:
        return Exception(f"Error: {str(e)}")