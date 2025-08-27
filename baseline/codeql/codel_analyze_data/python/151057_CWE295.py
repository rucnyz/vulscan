import redis
import ssl
# Implement a Python function that creates a secure SSL/TLS connection to a Redis server. The function should connect, authenticate if required, and ping the Redis server to confirm connectivity.

def secure_redis_link(redis_host, redis_port, redis_password=None, redis_db=0):
    ssl_context = ssl.create_default_context()
    client = redis.Redis(host=redis_host, port=redis_port, password=redis_password, db=redis_db, ssl=True, ssl_cert_reqs='required', ssl_ca_certs=None, ssl_context=ssl_context)
    try:
        if client.ping():
            print("Successfully connected to Redis server")
            return True
        else:
            print("Failed to ping Redis server")
            return False
    except redis.exceptions.ConnectionError as e:
        raise redis.exceptions.ConnectionError(f"Redis connection error: {e}")
    except ssl.SSLError as e:
        raise ssl.SSLError(f"SSL certificate validation failed: {e}")
    finally:
        client.close()