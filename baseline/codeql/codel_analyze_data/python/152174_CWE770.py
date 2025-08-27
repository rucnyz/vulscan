import time
MAX_ALLOCATION = 100

def allocate_memory():
    return bytearray(10**6)

def allocation():
    allocations = []
    while True:
        foo = allocate_memory()
        allocations.append(foo)
        print(f"Allocated memory: {len(allocations)} MB")
        time.sleep(0.1)