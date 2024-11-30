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
file_path = "/Users/tejasds/Downloads/Cloud_Computing_Homework_3.pdf"

# Client operation function
def kv_store_operation(op_type, key, author, value=None):
    try:
        if op_type == 'set':
            with open(file_path, 'rb') as file:
                # response = requests.post(url, data=file)
                response = requests.post(f"{BASE_URL}/tb/{key}/{author}", data=file)
            # response = get_html_data_lru(f"{BASE_URL}/tb/{key}")
        else:
            raise ValueError("Invalid operation type")
        response.raise_for_status()  # This will raise an error for non-2xx responses
        return True
    except Exception as e:
        # print(f"Error during {op_type} operation for key '{key}' and value '{value}': {e}")
        # print(f"the response sent is {response}")
        print(e)
        return False

# kv_store_operation("set", "key_1", "val_1")
for i in range(300):
    key = f"mytbis_{i}"
    op_type = 'set'
    value = None
    author = f"ABC_{i}"
    # print(i)
    kv_store_operation(op_type, key, author, value)
# kv_store_operation("get", "mytbis_8.pdf")
