# havent included the write concern to replicate writes. Make sure to add that if this doesnt work

from threading import Lock
from datetime import datetime
from pymongo import MongoClient
from functools import lru_cache
from bson.binary import Binary
from pymongo.errors import ConnectionFailure, WriteError, OperationFailure
import logging
from pymongo import WriteConcern

class Database:
    def __init__(self):
        try:
            # uncomment second line after setting up mongo replicas.
            self.client = MongoClient("mongodb://localhost:27017/")
            # self.client = MongoClient("mongodb://localhost:27017,localhost:27017,localhost:27017/?replicationSet=myReplicaSet")
            self.db = self.client['online_bookstore']
            self.books_db = self.db['books'] # This will store the books and their path
            self.users_db = self.db['users']
            self.operations_log = []  # This keeps track of all the operations with time logs
            self.lock = Lock()
        except ConnectionFailure as e:
            print(f'Could not connect to MongoDB: {e}')
            raise

    def _get_timestamp(self):
        return datetime.now().strftime("%m-%d-%Y %H:%M:%S")

    @lru_cache(maxsize=10)  # Cache the 3 most frequently accessed books
    def _cached_get_book(self, book_name):
        print(f"Fetching '{book_name}' from the database (not cache).") # For testing if the caching works
        fetched_book = self.books_db.find_one({"book_id": book_name})
        # print(fetched_book)
        if fetched_book != None:
            # return fetched_book["book_content"]
            return fetched_book
        else:
            return None

    def get_book(self, book_name): # Checks if a path exists and uses the path tp find the file and reads, it and returnes the information
        # with self.lock:
        timestamp = self._get_timestamp()
        self.operations_log.append(f'get_book({book_name}) - {timestamp}')
        with self.lock:
            book = self._cached_get_book(book_name)
            if book != None:
                # Increment the request count
                self.books_db.update_one(
                    {"book_id": book_name}, {"$inc": {"num_req": 1}}
                )
                return book
            else:
                return {"Error": f'Book {book_name} not found at {timestamp}.'}

    def post_book(self, book_id, data, author):  # Adds a new book
        timestamp = self._get_timestamp()
        self.operations_log.append(f'post_book({book_id}) - {timestamp}')
        with self.lock:
            try:
                book = {
                    "book_id": book_id,
                    "book_content": Binary(data),
                    "num_req": 0,
                    "author": author,
                }
                self.books_db.insert_one(book)
                self._cached_get_book.cache_clear()
                return {"Message": f'Book {book_id} was successfully added.'}
            except:
                return {"Error": f'Book {book_id} could not be saved at {timestamp}.'}

    def put_book(self, book_id, data): # Updates the path to the book
        timestamp = self._get_timestamp()
        self.operations_log.append(f'put_book({book_id}) - {timestamp}')
        with self.lock:
            # result = self.books_db.update_one({"book_id": book_id}, {"$set": data}) //
            result = self.books_db.update_one({"book_id": book_id},  {"$set": {"binary_field": Binary(data)}})
            if result.matched_count > 0:
                self._cached_get_book.cache_clear()
                return {"Message": f'Book {book_id} was successfully updated.'}
            else:
                return {"Error": f'Book {book_id} not found.'}

    def delete_book(self, book_name): # Deletes the book from the database
        timestamp = self._get_timestamp()
        self.operations_log.append(f'delete_book({book_name}) - {timestamp}')
        with self.lock:
            result = self.books_db.delete_one({"book_name": book_name})
            if result.deleted_count > 0:
                self._cached_get_book.cache_clear()
                return {"Message": f'Book {book_name} was successfully deleted.'}
            else:
                return {"Error": f'Book {book_name} not found.'}

    def get_user(self, username):
        # with self.lock:
        timestamp = self._get_timestamp()
        self.operations_log.append(f'get_user({username}) - {timestamp}')
        with self.lock:
            user = self.users_db.find_one({"username": username})
            if user:
                return user
            else:
                return {"Error": f'Username {username} not found.'}
    def put_user(self, username, password): # Adds a new user to the database
        # with self.lock:
        timestamp = self._get_timestamp()
        self.operations_log.append(f'put_user({username}) - {timestamp}')
        with self.lock:
            user = {"username": username, "password": password}
            self.users_db.insert_one(user)
            return {"Message": f'User {username} was successfully added.'}


    def post_user(self, username, password): # I'm gueesing this will be used to update the users's password?
        # with self.lock:
        timestamp = self._get_timestamp()
        self.operations_log.append(f'post_user({username}) - {timestamp}')
        with self.lock:
            result = self.users_db.update_one({"username": username}, {"$set": {"password": password}})
            if result.matched_count > 0:
                return {"Message": f'User {username}\'s password was successfully updated.'}
            else:
                return {"Error": f'Username {username} not found.'}

    def delete_user(self, username): # Deletes the user from the database
        timestamp = self._get_timestamp()
        self.operations_log.append(f'delete_user({username}) - {timestamp}')
        with self.lock:
            result = self.users_db.delete_one({"username": username})
            if result.deleted_count > 0:
                return {"Message": f'User {username} was successfully deleted.'}
            else:
                return {"Error": f'Username {username} not found.'}
