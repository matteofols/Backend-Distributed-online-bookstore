
import threading
from datetime import datetime
import os

class Database:
    def __init__(self):
        self.books_database = {}  # This will store the books and their path
        self.operations_log = []  # This keeps track of all the operations with time logs
        self.users_database = {}
        self.lock = threading.Lock()

    def _get_timestamp(self):
        return datetime.now().strftime("%m-%d-%Y %H:%M:%S")

    def get_book(self, book_id): # Checks if a path exists and uses the path tp find the file and reads, it and returnes the information
        with self.lock:
            timestamp = self._get_timestamp()
            self.operations_log.append(f'get_book({book_id}) - {timestamp}')
            if book_id in self.books_database:
                book_path = self.books_database[book_id]
                if os.path.exists(book_path):  # Check if the file exists
                    try:
                        with open(book_path, 'r') as file:
                            content = file.read()  # Read the file content
                        return {"book_id": book_id, "path": book_path, "content": content}
                    except Exception as e:
                        return {"Error": f'Failed to read file at {book_path}: {str(e)}'}
                else:
                    return {"Error": f'File at path {book_path} not found.'}
            else:
                return {"Error": f'Book {book_id} not found.'}
    
    def put_book(self, book_id, path):  # Adds a new book
        with self.lock:
            timestamp = self._get_timestamp()
            self.operations_log.append(f'put_book({book_id}, {path}) - {timestamp}') 
            self.books_database[book_id] = path
            return {"Message": f'Book {book_id} was successfully added with path {path}'}

    def post_book(self, book_id, path): # Updates the path to the book
        with self.lock:
            timestamp = self._get_timestamp()
            self.operations_log.append(f'post_book({book_id}, {path}) - {timestamp}')
            if book_id in self.books_database:
                self.books_database[book_id] = path
                return {"Message": f'Book {book_id} was successfully updated with path {path}'}
            else:
                return {"Error": f'Book {book_id}, not found.'}

    def delete_book(self, book_id): # Deletes the book from the database
        with self.lock:
            timestamp = self._get_timestamp()
            self.operations_log.append(f'delete_book({book_id}) - {timestamp}')
            if book_id in self.books_database:
                del self.books_database[book_id]
                return {"Message": f'Book {book_id} was successfully deleted'}
            else:
                return {"Error": f'Book {book_id}, not found.'}

    def get_user(self, username): 
        with self.lock:
            timestamp = self._get_timestamp()
            self.operations_log.append(f'get_user({username}) - {timestamp}') 
            if username in self.users_database:
                return self.users_database[username]
            return {"Error": f'Username {username} not found.'}
    
    def put_user(self, username, password): # Adds a new user to the database
        with self.lock:
            timestamp = self._get_timestamp()
            self.operations_log.append(f'put_user({username}, {password}) - {timestamp}') 
            self.users_database[username] = password
            return {"Message": f'User {username} was successfully added.'}

    def post_user(self, username, password): # I'm gueesing this will be used to update the users's password?
        with self.lock:
            timestamp = self._get_timestamp()
            self.operations_log.append(f'post_user({username}, {password}) - {timestamp}')
            if username in self.users_database:
                self.users_database[username] = password
                return {"Message": f'User {username}\'s password was successfully updated'} # I'm not sure if we should return the password too?
            else:
                return {"Error": f'Username {username} not found.'}

    def delete_user(self, username): # Deletes the user from the database
        with self.lock:
            timestamp = self._get_timestamp()
            self.operations_log.append(f'delete_user({username}) - {timestamp}')
            if username in self.users_database:
                del self.users_database[username]
                return {"Message": f'User {username} was successfully deleted'}
            else: # Error for trying to delete a user that doesn't exists
                return {"Error": f'Username {username} not found.'}