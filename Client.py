import SecurityService as ss
import base64
import json
import requests
import sys

commands = "FIND <filename> \n OPEN <filename> \n CLOSE <filename> \n READ <filename> \n CHECK <filename> \
           \n WRITE <filename> <updated content> \n ADD <filename> <file server> \n LIST \n HELP \n QUIT"

ss_url = 'http://127.0.0.1:8001/'
ds_url = 'http://127.0.0.1:8002/'
ls_url = 'http://127.0.0.1:8003/'

def get_help():
    return print("The possible commands are: ", commands)


def main():

    # user login, each new client will be asked to log on, their details will then be stored in the SS database
    userId = input("Please Enter Username: ")
    userPassword = input("Please Enter Password: ")

    encId = base64.urlsafe_b64encode(ss.encrypt(userId, userPassword).encode()).decode()

    print('Accessing Security Service')
    authDirJson = {'user_id': userId, 'password': userPassword, 'encrypted_id': encId, 'server_id': 'File Server 1'}
    print('Sending', authDirJson)


    authReq = requests.post(ss_url+'auth', json=authDirJson)
    encToken = authReq.json()['token']
    decToken = json.loads(ss.decrypt(base64.urlsafe_b64decode(encToken).decode(), userPassword))
    print(decToken)

    opened_files = []
    connected = True
    print("For a list of all possible commands, type HELP.")
    while connected:
        cmd = input("Please Enter Command >: ")

        if cmd == "HELP":
            get_help()

        elif cmd == "QUIT":
            print("Goodbye!")
            sys.exit()

        elif "FIND" in cmd:
            filename = cmd.split()[1]
            read_file = requests.get(ds_url+"get_directory/"+filename)
            print(read_file.text)

        elif "OPEN" in cmd:
            filename = cmd.split()[1]
            opened_files, msg = open(opened_files, filename, userId)
            print(msg)

        elif "CLOSE" in cmd:
            filename = cmd.split()[1]
            opened_files, msg = close(opened_files, filename)
            print(msg)

        elif "READ" in cmd:
            filename = cmd.split()[1]
            file = read(opened_files, filename)
            print(file)

        elif "WRITE" in cmd:
            filename = cmd.split()[1]
            if len(cmd.split()) > 2:
                content = cmd.split(' ', 2)[2]
                msg = write(opened_files, filename, content)
                print(msg)
            else:
                print('WRITE requires two arguments, <filename> and  <updated content>')

        elif "ADD" in cmd:
            filename = cmd.split()[1]
            if len(cmd.split()) > 2 :
                filepath = cmd.split(' ', 2)[2]
                msg = add(filename, filepath)
                print(msg)
            else:
                print('ADD requires two arguments, <filename> and  <file server>')

        elif "LIST" in cmd:
            if len(opened_files) > 1:
                print(opened_files)
            else:
                print("No files opened.")

        elif "CHECK" in cmd:
            filename = cmd.split()[1]
            check = requests.get(ls_url+"check/"+filename)
            print(check.text)

        else:
            print("Please provide correct commands, for more information on the commands, type HELP"
                  "\nMake sure to include file extensions in name (i.e. .txt etc)")


def open(opened_files, filename, userId):
    for file in opened_files:
        if file['filename'] == filename:
            return opened_files, 'File already opened.'
    open_file = requests.get(ds_url + "open?" + 'filename='+filename + '&userId='+userId)
    if open_file.status_code != 200:
        return opened_files, open_file.text.strip('{}')
    opened_files.append(open_file.json())
    return opened_files, 'File successfully opened.'


def close(opened_files, filename):
    for file in opened_files:
        if file['filename'] == filename:
            close = requests.post(ls_url+"unlock", json=file)
            opened_files.remove(file)
            return opened_files, "File successfully closed."
    return opened_files, "Error: No file of such name is opened."


def read(opened_files, filename):
    for file in opened_files:
        if file['filename'] == filename:
            return file['file_content']
    return "Error: No file of such name is opened."


def write(opened_files, filename, content):
    for file in opened_files:
        if file['filename'] == filename:
            file['file_content'] = content
            updated_file = requests.post(ds_url+"write", json=file)
            return updated_file.text
    return "Error: No file of such name is opened."


def add(filename, filepath):
    file = {'filename': filename, 'filepath': filepath}
    post = requests.post(ds_url+"add", json=file)
    return post.text


if __name__ == "__main__":
    main()