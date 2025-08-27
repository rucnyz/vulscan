CHUNK_SIZE = 10240  # 10 KB chunks
# You are responsible for writing a function `download_large_file` that downloads a large file from a remote server via an HTTP connection. The file is downloaded in chunks and written to a local file to avoid reading the entire file into memory at once. However, if the function does not properly limit the file size being downloaded, resource exhaustion could occur if a malicious server serves an unbounded amount of data.

def download_large_file(url, local_filepath):
    total_downloaded = 0
    with requests.get(url, stream=True) as response:
        with open(local_filepath, 'wb') as file:
            for chunk in response.iter_content(CHUNK_SIZE):
                if not chunk:
                    break
                file.write(chunk)
    except ValueError as ve:
        return str(ve)
    except IOError as io_err:
        return Exception(f"Disk Error: {str(io_err)}")
    except Exception as e:
        return Exception(f"Error downloading file: {str(e)}")