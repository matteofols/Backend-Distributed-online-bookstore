import threading
from datetime import datetime
import os
import json

class Database:
    def __init__(self):
        self.cwd = os.getcwd()
        self.upload_folder = './DB_Trial/'
        self.books_database = self.get_metadata('textbook_metadata.json')  # This will store the books and their path
        self.operations_log = []  # This keeps track of all the operations with time logs
        self.users_database = self.get_metadata('users_metadata.json')
        self.lock = threading.Lock()

    def get_metadata(self, file_name):
        self.metadata_file = os.path.join(self.upload_folder, file_name)
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                self.database = json.load(f)
        else:
            self.database = {}
        return self.database

    def save_metadata(self, metadata_file, metadata):
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)

    def _get_timestamp(self):
        return datetime.now().strftime("%m-%d-%Y %H:%M:%S")

    def get_book(self, book_name): # Checks if a path exists and uses the path tp find the file and reads, it and returnes the information
        # with self.lock:
        timestamp = self._get_timestamp()
        self.operations_log.append(f'get_book({book_name}) - {timestamp}')
        with self.lock:
            if book_name in self.books_database:
                book_path = self.books_database[book_name]["file_loc"]
                if os.path.exists(book_path):  # Check if the file exists
                    try:
                        # with open(book_path, 'r') as file:
                        #     content = file.read()  # Read the file content
                        # return {"book_name": book_name, "path": book_path, "content": content}
                        self.books_database[book_name]["num_req"] = self.books_database[book_name]["num_req"] + 1
                        # return {"book_name": book_name, "path": book_path}
                    except Exception as e:
                        return {"Error": f'Failed to read file at {book_path}: {str(e)}'}
                else:
                    return {"Error": f'File at path {book_path} not found at {timestamp}.'}
            else:
                return {"Error": f'Book {book_name} not found at {timestamp}.'}
        return {"book_name": book_name, "path": book_path}

    def post_book(self, book_id, data, author):  # Adds a new book
        # with self.lock:
        timestamp = self._get_timestamp()
        path = "/Users/tejasds/Chin_college/CC/Project/CC_project_1/DB_Trial/Textbooks/" + book_id + ".pdf"
        temp_dict = {}
        self.operations_log.append(f'put_book({book_id}, {path}) - {timestamp}')
        with self.lock:
            temp_dict["file_loc"] = path
            temp_dict["num_req"] = 0
            temp_dict["Author"] = author
            self.books_database[book_id] = temp_dict
            try:
                with open(path, 'wb') as f:
                    f.write(data)
            except Exception as e:
                return {"Error": f'Failed to store file at {path}: {str(e)}'}
            # write the book to the hard disk
            # return {"Message": f'Book {book_id} was successfully added with path {path}'}
        self.save_metadata('/Users/tejasds/Chin_college/CC/Project/CC_project_1/DB_Trial/textbook_metadata.json', self.books_database)
        return {"Message": f'Book {book_id} was successfully added with path {path}'}

    def put_book(self, book_id, path, data): # Updates the path to the book
        # with self.lock:
        timestamp = self._get_timestamp()
        self.operations_log.append(f'post_book({book_id}, {path}) - {timestamp}')
        with self.lock:
            if book_id in self.books_database:
                try:
                    with open(path, 'wb') as f:
                        f.write(data)
                except Exception as e:
                    return {"Error": f'Failed to update file at {path}: {str(e)}'}
                # update the contents of the book as well.
                # return {"Message": f'Book {book_id} was successfully updated with path {path}'}
            else:
                return {"Error": f'Book {book_id}, not found.'}
        self.save_metadata('/Users/tejasds/Chin_college/CC/Project/CC_project_1/DB_Trial/textbook_metadata.json', self.books_database)
        return {"Message": f'Book {book_id} was successfully updated with path {path}'}

    def delete_book(self, book_name): # Deletes the book from the database
        # with self.lock:
        timestamp = self._get_timestamp()
        self.operations_log.append(f'delete_book({book_name}) - {timestamp}')
        with self.lock:
            if book_name in self.books_database:
                try:
                    os.remove(self.books_database[book_name]["file_loc"])
                    del self.books_database[book_name]
                except Exception as e:
                    return {"Error": f'Book {book_name} could not be deleted.'}
                # delete the book in the hard disk as well.
                # return {"Message": f'Book {book_name} was successfully deleted'}
            else:
                return {"Error": f'Book {book_name}, not found.'}
        self.save_metadata('/Users/tejasds/Chin_college/CC/Project/CC_project_1/DB_Trial/textbook_metadata.json', self.books_database)
        return {"Message": f'Book {book_name} was successfully deleted'}

    def get_user(self, username):
        # with self.lock:
        timestamp = self._get_timestamp()
        self.operations_log.append(f'get_user({username}) - {timestamp}')
        with self.lock:
            if username in self.users_database:
                return self.users_database[username]
            return {"Error": f'Username {username} not found.'}

    def put_user(self, username, password): # Adds a new user to the database
        # with self.lock:
        timestamp = self._get_timestamp()
        self.operations_log.append(f'put_user({username}, {password}) - {timestamp}')
        with self.lock:
            self.users_database[username] = password
            return {"Message": f'User {username} was successfully added.'}
        self.save_metadata('users_metadata.json', self.users_database)

    def post_user(self, username, password): # I'm gueesing this will be used to update the users's password?
        # with self.lock:
        timestamp = self._get_timestamp()
        self.operations_log.append(f'post_user({username}, {password}) - {timestamp}')
        with self.lock:
            if username in self.users_database:
                self.users_database[username] = password
                return {"Message": f'User {username}\'s password was successfully updated'} # I'm not sure if we should return the password too?
            else:
                return {"Error": f'Username {username} not found.'}
        self.save_metadata('users_metadata.json', self.users_database)

    def delete_user(self, username): # Deletes the user from the database
        # with self.lock:
        timestamp = self._get_timestamp()
        self.operations_log.append(f'delete_user({username}) - {timestamp}')
        with self.lock:
            if username in self.users_database:
                del self.users_database[username]
                return {"Message": f'User {username} was successfully deleted'}
            else: # Error for trying to delete a user that doesn't exists
                return {"Error": f'Username {username} not found.'}
        self.save_metadata('users_metadata.json', self.users_database)
