import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory, send_file, jsonify
import tools
# import jsonify
from Database import Database

# make a config file to store the below variables and then you can use them.
# also make note of how the book is requested by the users.

UPLOAD_FOLDER = './DB_Trial/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = Database()

@app.route('/tb/<file_name>', methods=['GET'])
def get_pdf(file_name):
    book_info = db.get_book(file_name)
    if "path" in book_info:
        # return send_file(book_info["path"], mimetype='application/pdf', attachment_filename='book.pdf')
        return send_file(book_info["path"], mimetype='application/pdf')
    return jsonify(book_info), 404

@app.route('/tb/<file_name>', methods=['DELETE'])
def delete_pdf(file_name):
    book_info = db.delete_book(file_name)
    if "Message" in book_info:
        return jsonify({'success': 'PDF deleted successfully'}), 200
    return jsonify({'error': 'PDF not found'}), 404

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host='127.0.0.1', port=8000, debug=True)
