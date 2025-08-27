import time
MAX_ALLOCATION = 100

def allocate_memory():
    return bytearray(10**6)

def allocation():
    allocations = []
    while True:
        foo = allocate_memory()
        allocations.append(foo)
        if len(allocations) >= MAX_ALLOCATION:
            break
        time.sleep(0.1)