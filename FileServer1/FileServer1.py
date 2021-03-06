from flask_api import FlaskAPI, status
from flask import request
import requests
import base64
import json
import os

app = FlaskAPI(__name__)

server_name = 'File Server 1'
server_key = 'server_1_key'
file_path = 'files/'
lock_server = 'http://127.0.0.1:8003/lock'


@app.route('/find/<filename>', methods=['GET'])
def find_file(filename):
    try:
        open(os.path.join(file_path, filename))
    except:
        return {'Error:': 'File Not Found.'}, status.HTTP_404_NOT_FOUND
    return {'Server: ': server_name,'file_path': '/'+file_path}


@app.route('/open', methods=['GET'])
def open_file():
    file = request.args.to_dict()
    try:
        opened_file = open(os.path.join(file_path, file['filename']))
        is_locked = requests.post(lock_server, json=file)
        if is_locked.text == 'true':
            return {'Error:': 'File is already locked'}, status.HTTP_409_CONFLICT
        else:
            content = opened_file.read()
            return {'filename': file['filename'], 'file_content': content, 'server_port': '8007'}
    except:
        return {'Error:': 'File Not Found.'}, status.HTTP_404_NOT_FOUND


@app.route('/write', methods=['POST'])
def write_file():
    updated_file = request.json
    filename = updated_file['filename']
    try:
        new_content = updated_file['file_content']
        file = open(os.path.join(file_path, filename), "wb+")
        file.write(new_content.encode())
    except:
        return {'Error:': 'File Not Found.'}, status.HTTP_404_NOT_FOUND
    return {'filename': filename, 'message': 'File successfully written.'}


@app.route('/add', methods=['POST'])
def add_file():
    new_file = request.json
    try:
        open(os.path.join(file_path, new_file['filename']))
        return 'File already exists in this directory.'
    except:
        file = open(os.path.join(file_path, new_file['filename']), "wb")
        file.write(str("This is file "+new_file['filename']).encode())
        file.close()
        return 'File succesfully added.'


@app.route('/name', methods=['GET'])
def get_server_name():
    return server_name


if __name__=='__main__':
    app.run(port=8007)