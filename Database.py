from threading import Lock
from datetime import datetime
from pymongo import MongoClient

class Database:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:5000/")
        self.db = self.client['online_bookstore']
        self.books_db = self.db['books'] # This will store the books and their path
        self.users_db = self.db['users'] 
        self.operations_log = []  # This keeps track of all the operations with time logs
        self.lock = Lock()
# These two functions are no longer needed
    # def get_metadata(self, file_name):
    #     self.metadata_file = os.path.join(self.upload_folder, file_name)
    #     if os.path.exists(self.metadata_file):
    #         with open(self.metadata_file, 'r') as f:
    #             self.database = json.load(f)
    #     else:
    #         self.database = {}
    #     return self.database

    # def save_metadata(self, metadata_file, metadata):
    #     with open(metadata_file, 'w') as f:
    #         json.dump(metadata, f)

    def _get_timestamp(self):
        return datetime.now().strftime("%m-%d-%Y %H:%M:%S")

    @lru_cache(maxsize=3)  # Cache the 3 most frequently accessed books
    def _cached_get_book(self, book_name):
        print(f"Fetching '{book_name}' from the database (not cache).") # For testing if the caching works
        return self.books_db.find_one({"book_name": book_name})

    def get_book(self, book_name): # Checks if a path exists and uses the path tp find the file and reads, it and returnes the information
        # with self.lock:
        timestamp = self._get_timestamp()
        self.operations_log.append(f'get_book({book_name}) - {timestamp}')
        with self.lock:
            book = self._cached_get_book(book_name)
            if book:
                # Increment the request count
                self.books_db.update_one(
                    {"book_name": book_name}, {"$inc": {"num_req": 1}}
                )
                return book
            else:
                return {"Error": f'Book {book_name} not found at {timestamp}.'}
            
    def post_book(self, book_id, author):  # Adds a new book
        timestamp = self._get_timestamp()
        self.operations_log.append(f'post_book({book_id}) - {timestamp}')
        with self.lock:
            book = {
                "book_id": book_id,
                "file_loc": f"/path/to/{book_id}.pdf",
                "num_req": 0,
                "author": author,
            }
            self.books_db.insert_one(book)
            self._cached_get_book.cache_clear()
            return {"Message": f'Book {book_id} was successfully added.'}


    def put_book(self, book_id, data): # Updates the path to the book
        timestamp = self._get_timestamp()
        self.operations_log.append(f'put_book({book_id}) - {timestamp}')
        with self.lock:
            result = self.books_db.update_one({"book_id": book_id}, {"$set": data})
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