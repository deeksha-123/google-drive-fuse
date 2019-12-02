
from __future__ import print_function
from googleapiclient.http import MediaFileUpload,MediaIoBaseDownload
from httplib2 import Http
from googleapiclient.discovery import build
from oauth2client import file, client, tools
import io, os,sys
import getpass
import re, shutil
import shlex, errno
import difflib, pickle
from tempfile import mkstemp
print("drive")
x=os.getcwd()
#print(x)

g_drive = x+"/gdrive"
gmount = x+"/mount_point"

print("access")
directory = {}
cur_path = g_drive

SCOPES = 'https://www.googleapis.com/auth/drive'

mimeTypes = [ "application/vnd.google-apps.document", "application/vnd.google-apps.spreadsheet", "application/vnd.google-apps.presentation", "application/vnd.google-apps.drawing"]

def authentication():
    print("auth_drive called")
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('drive', 'v3', http=creds.authorize(Http()))
    return service

def list_drive(path, directory):
    print("list_drive called")
    service = authentication()
    folder_id = directory[path]
    results = service.files().list(q="'" + folder_id + "' in parents and trashed=false").execute()
    temp_directory = []
    items = results.get('files', [])
    if not path.endswith('/'):
        path = path + "/"

    if not items:
        print('Empty Directory')
    else:
        for item in items:
            temp_directory.append(path + item['name'])
            if item['mimeType'] == "application/vnd.google-apps.folder":
                    if not os.path.isdir(path + item['name']):
                        os.mkdir(path + item['name'])
                        print(item['name'])
                        directory[path + item['name']] = item['id']
                        cpath=path + item['name']
                        list_drive(cpath,directory)
            else:
                flag = False
                if item['mimeType'] in mimeTypes:
                    if not os.path.isfile(path + item['name']):
                        request = service.files().export_media(fileId=item['id'], mimeType='application/pdf')
                        flag = True
                else:
                    if not os.path.isfile(path + item['name']):
                        request = service.files().get_media(fileId=item['id'])
                        flag = True

                if flag:
                    directory[path + item['name']] = item['id']
                    fh = io.FileIO(path+item['name'], 'wb')
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        print(item['name'])

    
    return directory

def create_drive(path,folder_name, parent_id=None):
    print("create_drive called")
    service = authentication()

    folder = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    path=path+"/"+folder_name
    os.mkdir(path)
    if parent_id:
        folder['parents'] = [parent_id]

    file = service.files().create(body=folder, fields='id').execute()

    print('Folder Created Successfully')

    return file.get('id')


def upload_drive(file_path, file_name, folder_id,dest):
    print("upload_drive called")
    service = authentication()

    file_metadata = {
        'name': file_name,
        'parents' : [folder_id]
    }

    media = MediaFileUpload(file_path)

    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    dest_path=dest
    content = list_drive(dest_path,directory)
    #content.sort()


def copy(from_path, to_path, directory):
    print("copy_drive called")
    folder_id = directory[to_path]

    file_name = from_path[from_path.rfind('/')+1:]

    upload_drive(from_path, file_name, folder_id)
    
    

def move(from_path, to_path, directory):
    print("move_drive called")	
    file_id = directory[from_path]

    folder_id = directory[to_path]

    service = authentication()

    file = service.files().get(fileId=file_id, fields='parents').execute()

    previous_parents = ",".join(file.get('parents'))

    file = service.files().update(fileId=file_id, addParents=folder_id, removeParents=previous_parents, fields='id, parents').execute()

    del directory[from_path]

    if os.path.isdir(from_path):
        shutil.rmtree(from_path)
    else:
        os.remove(from_path)

    return directory


def trash(path, directory):
    print("trash_drive called")
    service = authentication()

    file_id = directory[path]

    file_metadata = {
        'trashed': 'true'
    }

    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)

    del directory[path]

    file = service.files().update(body=file_metadata, fileId=file_id).execute()

    return directory


def download(file_id, filename):
    print("download_drive called")
    service = authentication()

    request = service.files().get_media(fileId=file_id)

    fh = io.FileIO(filename, 'wb')

    downloader = MediaIoBaseDownload(fh, request)

    done = False

    while done is False:
        status, done = downloader.next_chunk()
        print(filename) #Downloaded files

####################################################################################################################


#loading data from directory.txt into dictionary
def load():
    print("load called:")
    global directory
    try:
        directory_pckl = open("directory.txt","rb")
        if(os.stat("directory.txt").st_size != 0):
            directory = pickle.load(directory_pckl)
        else:
            directory = { g_drive : 'root' }
        directory_pckl.close()
    except:
        directory = { g_drive : 'root' }
        with open('directory.txt', 'wb') as f:
            pickle.dump(directory, f)#when the function is executed for the first time 

#updating directory.txt
def store():
    print("store called:")
    global directory
    directory_pckl = open("directory.txt","wb")
    pickle.dump(directory, directory_pckl)
    directory_pckl.close()

#changing the directory path 
def cd(inp):
    print("cd called:")
    global directory
    global cur_path
    
    if inp == "..":
        if not cur_path == g_drive:
            cur_path = cur_path.rpartition("/")[0]
    elif inp == ".":
        cur_path = cur_path
    else:
        cur_path = cur_path + "/" +inp
        # print(cur_path)
    if not os.path.isdir(cur_path):
        cur_path = cur_path.rpartition("/")[0]
        print("Not a directory")
        return
    directory = list_drive(cur_path, directory)
    store()

#removing file or folder from the drive
def rm(inp):
    print("rm called:")
    global directory

    if inp not in directory.keys():
        print("No such file/directory")
        return

    directory =trash(inp, directory)
    store()

#listing the files in the drive
def ls() :
    print("ls called:")	
    content = os.listdir(cur_path)
    content.sort()
    for i in content : 
        print(i)

#making a new directory in google drive
def mkdir(inp,folder_name):
    print("mkdir called:")
    if not os.path.isdir(folder_name):
        parent_id = directory[cur_path]
        folder_id =create_drive(inp,folder_name, parent_id)
        directory[cur_path + '/' + folder_name] = folder_id
    else:
        print("Directory already exists")
    	
#moving file from source to destination
def move(from_path, to_path):
    print("move called:")
    global directory

    if from_path not in directory.keys():
        print("Invalid source")
        return

    if to_path not in directory.keys():
        print("Invalid destination")
        return

    if os.path.isfile(to_path):
        print("Destination should be a directory")
        return

    directory = move(from_path, to_path, directory)

    store()

#copying a file 
def copy(from_path, to_path):
    print("copy called:")
    global directory

    if from_path not in directory.keys():
        print("Invalid source")
        return

    if to_path not in directory.keys():
        print("Invalid destination")
        return

    if os.path.isfile(to_path):
        print("Destination should be a directory")
        return

    copy(from_path, to_path, directory)

#uploading a new file into the drive
def uploading(source,destination):
    print("upload called:")
    if destination.endswith("/"):
        destination = destination[:-1]
        print(destination)
    if os.path.isdir(destination):
        folder_id = directory[destination]
        if os.path.exists(source):
            filename = source[source.rfind('/')+1:]
            upload_drive(source,filename,folder_id,destination)
        else:
            print("Invalid source")
    else:
        print("Invalid destination")

if __name__ == '__main__':

    if not os.path.isdir(g_drive):
        os.mkdir(g_drive)

    if not os.path.isdir(gmount):
        os.mkdir(gmount)

    load()
    store()
    cd('..')
    os.system('clear')
    while True:
        
        
        print("\033[2;32;40m################################################INFINITE LOOP DRIVE########################################################")
        print("")
        inp = input("\033[1;31;40m$$ ")
        cmd = inp.split()[0]
        if cmd == "mkdir":
            mkdir(cur_path,inp.split()[1])        

        if cmd == "upload":
            print("Uploading...")
            uploading(inp.split()[1], g_drive+inp.split()[2])
        if cmd == "copy":
            print("Copying...")
            copy(cur_path + inp.split()[1], g_drive + inp.split()[2])        
        if cmd == "rm":
            print("Removing...")
            rm(cur_path + "/" + inp.split()[1])
        if cmd == "cd":
            cd(inp.split()[1]) 
        if cmd == "ls":
            cd('.')
            ls()
        if cmd == "move":
            print("Moving...")
            move(cur_path +inp.split()[1], g_drive + inp.split()[2])
        if cmd == "exit":
            store()
            exit()

        store()


