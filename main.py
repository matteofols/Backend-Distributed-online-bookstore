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
    book_info = db.get_book(file_name[:-4])
    if "path" in book_info:
        # return send_file(book_info["path"], mimetype='application/pdf', attachment_filename='book.pdf')
        return send_file(book_info["path"], mimetype='application/pdf')
    return jsonify(book_info), 404

@app.route('/tb/<file_name>', methods=['PUT'])
def put_pdf(file_name):
    # if 'pdf_file' not in request.files:
    #     return request.data, 400

    pdf_file = request.data
    # pdf_data = pdf_file.read()
    print(db.books_database[file_name[:-4]])
    book_path = db.books_database[file_name[:-4]]["file_loc"]
    book_info = db.put_book(file_name[:-4], book_path, pdf_file)
    if "Message" in book_info:
        # return send_file(book_info["path"], mimetype='application/pdf', attachment_filename='book.pdf')
        return jsonify(book_info), 200
    return jsonify(book_info), 404

@app.route('/tb/<file_name>/<author>', methods=['POST'])
def post_pdf(file_name, author):
    # if 'File' not in request.files:
    #     return request.files, 400
    # pdf_file = str(request.data.decode('utf-8'))
    pdf_file = request.data
    # pdf_data = pdf_file.read()
    # print(db.books_database[file_name[:-4]])
    # book_path = db.books_database[file_name[:-4]]["file_loc"]
    book_info = db.post_book(file_name[:-4], pdf_file, author)
    if "Message" in book_info:
        # return send_file(book_info["path"], mimetype='application/pdf', attachment_filename='book.pdf')
        return jsonify(book_info), 200
    return jsonify(book_info), 404

@app.route('/tb/<file_name>', methods=['DELETE'])
def delete_pdf(file_name):
    book_info = db.delete_book(file_name[:-4])
    if "Message" in book_info:
        return jsonify({'success': 'PDF deleted successfully'}), 200
    return jsonify({'error': 'PDF not found'}), 404

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host='127.0.0.1', port=8000, debug=True)
