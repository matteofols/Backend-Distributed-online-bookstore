import threading
import queue
from typing_extensions import KeysView
from functools import lru_cache
import requests
import time
import random
import hashlib

# The base URL of the Flask server
BASE_URL = 'http://localhost:8000'

# Configure the number of threads and operations
# NUM_THREADS = 4
# OPS_PER_THREAD = 5000
NUM_THREADS = 10
OPS_PER_THREAD = 30
PRINT_INTERVAL = 10000  # Interval for printing intermediate results

fetched_from_cache = 0

# Queues for managing operations and latencies
operations_queue = queue.Queue()
latencies_queue = queue.Queue()
dropped_queue = queue.Queue()
dropped_queue.put(0);

# Synchronize the starting of threads
start_event = threading.Event()

@lru_cache(maxsize=50)
def get_html_data_lru(url):
    response = requests.get(url)
    # fetched_from_cache = fetched_from_cache + 1
    print(f"the response sent is {response}")
    return response

# Client operation function
def kv_store_operation(op_type, key, value=None):
    try:
        if op_type == 'get':
            # URL = ch.get_node(key)
            # response = requests.get(f"{URL}/{key}")
            response = get_html_data_lru(f"{BASE_URL}/tb/{key}")
        else:
            raise ValueError("Invalid operation type")
        # print(f"the response sent is {response}")
        response.raise_for_status()  # This will raise an error for non-2xx responses
        return True
    except Exception as e:
        # print(f"Error during {op_type} operation for key '{key}' and value '{value}': {e}")
        # print(f"the response sent is {response}")
        print(e)
        return False

# kv_store_operation("set", "key_1", "val_1")
# kv_store_operation("get", "mytbis_8.pdf")

# Worker thread function
def worker_thread():
    while not start_event.is_set():
        # Wait until all threads are ready to start
        pass

    while not operations_queue.empty():
        op, key, value = operations_queue.get()
        start_time = time.time()
        if kv_store_operation(op, key, value):
            latency = time.time() - start_time
            latencies_queue.put(latency)
        else:
            ops_dr = dropped_queue.get()
            ops_dr = ops_dr + 1
            dropped_queue.put(ops_dr)

# Monitoring thread function
def monitor_performance():
    last_print = time.time()
    while True:
        time.sleep(PRINT_INTERVAL)
        current_time = time.time()
        elapsed_time = current_time - last_print
        latencies = []
        # dropped_ops = []
        while not latencies_queue.empty():
            latencies.append(latencies_queue.get())
        # while not dropped_queue.empty():
        #     dropped_ops.append(dropped_queue.get())

        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            throughput = len(latencies) / elapsed_time
            print(f"[Last {PRINT_INTERVAL} seconds] Throughput: {throughput:.2f} ops/sec, "
                  f"Avg Latency: {avg_latency:.5f} sec/ops")
        last_print = time.time()

# Populate the operation queue with mixed 'set' and 'get' requests
for j in range(3):
    for i in range(100):
        # key = f"key_{i}"
        key = f"mytbis_{i}"
        op_type = 'get'
        value = None
        operations_queue.put((op_type, key, value))

# # Create and start worker threads
threads = [threading.Thread(target=worker_thread) for _ in range(NUM_THREADS)]

# Start the monitoring thread
monitoring_thread = threading.Thread(target=monitor_performance, daemon=True)
monitoring_thread.start()

# Starting benchmark
start_time = time.time()
start_event.set()  # Signal threads to start

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

# Calculate final results
total_time = time.time() - start_time
# total_ops = NUM_THREADS * OPS_PER_THREAD * 2 # times two for 'set' and 'get'
total_ops = NUM_THREADS * OPS_PER_THREAD # times two for 'set' and 'get'
total_latencies = list(latencies_queue.queue)
average_latency = sum(total_latencies) / len(total_latencies) if total_latencies else float('nan')
throughput = total_ops / total_time
dropped_num_ops = list(dropped_queue.queue)
error_rate = dropped_queue.get() / total_ops

print("\nFinal Results:")
print(f"Total operations: {total_ops}")
print(f"Total time: {total_time:.2f} seconds")
print(f"Throughput: {throughput:.2f} operations per second")
print(f"Average Latency: {average_latency:.5f} seconds per operation")
print(f"Error rate: {error_rate:.5f} number of failed operations / total number of operations")
