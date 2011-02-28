#!/usr/bin/env python

# jianjun create the psync project at feb 24,2011
# psync to for management the sync file to communitcat
# with reomte computer
# jianjun365222@gmail.com

import os, sys


# the sync file list , orginazed as a list of dir or files
# dir contains files , the structure is descript bellow
#
#      |--"name":dir name
#      |
# dir -|--"filelist":["filename1","filename2",]
#      |
#      |--"dirlist":["structrue of dir list",]
#
# dir = {"name":"root","parent":None,"filelist":[],"dirlist":[]}

sync_files=[]
sync_file="./synclist"
user_data={}

#save a dir structure to file
def _save_dir_tree(fd, dirdic):
    #if(os.path.isfile(dirdic)):
    #    return
    fd.write("di "+ os.path.join(dirdic["name"]) +'\n')
    for f in dirdic["filelist"]:
        fd.write("f  "+ os.path.join(dirdic["name"],f)+'\n')
    
    for d in dirdic["dirlist"]:
        _save_dir_tree(fd,d)
    fd.write("do "+ os.path.join(dirdic["name"]) +'\n')    

#read frome the file , at a line started by "di" ,
#and read on , to construct a dir structrue
def _load_dir_tree(fd):
    dir_tree={}

    dir_tree["name"]=fd.readline().split()[1]
    dir_tree["filelist"]=[]
    dir_tree["dirlist"]=[]

    while 1:
        line = fd.readline()
        if not line:
            break
        if(line.startswith("f ")):
            dir_tree["filelist"].append(line.split()[1])
        if(line.startswith("di ")):
            dir_tree["dirlist"].append(_load_dir_tree(fd))
        if(line.startswith("do")):
            return dir_tree

    return dir_tree

#load sync file from disk to sync_files
def load_sync_files():
    fd = open(sync_file,"r")
    while 1:
        line = fd.readline()
        if not line:
            break
        if(line.startswith("F  ")):  # a file to sync
            sync_files.append(line.split()[1])
        if(line.startswith("DS ")):   # a dir to sync
            sync_files.append(_load_dir_tree(fd))
    fd.close()

#save sync_files sync file to disk 
def save_sync_files():
    fd = open(sync_file,"w")
    for f in sync_files:
        if isinstance(f,str):
            fd.write('F  '+ f+ "\n")
        elif isinstance(f,dict):
            fd.write('DS '+ f["name"]+ '\n')
            _save_dir_tree(fd,f)
    fd.close()


# get a tree object of the dirpath on the computer
def get_dir_tree(dirpath):

    if(os.path.isfile(dirpath)):
        return []

    # this is a dir
    current = {}
    current['name'] = dirpath
    current['filelist'] = []
    current['dirlist'] = []

    for f in os.listdir(dirpath):
        file_path = os.path.join(dirpath,f)

        if os.path.isfile(file_path):
            print(file_path)
            current['filelist'].append(f)
        if os.path.isdir(file_path):
            current['dirlist'].append( get_dir_tree( file_path ) )

    return current


# get a path's position in sync file
# if it is a new path , return -1
def get_file_index_position(path):
    pass

# add a file to sync list
def add_to_sync(path):
    if(os.path.isdir(path)):
        pass

# remove a file from sync tree , path is a file or dir on the 
# computer
def remove_sync(path):

    if os.path.ispath(path):
        if path in sync_files:
            sync_files.remove(path)

    elif os.path.isdir(path):
        for item in sync_files:
            if isinstance(item,dict) and item[name] == path:
                sync_files.remove(item)

    elif :
        print("the path not contained in the sync list")

# get sync list
def get_sync_list():
    pass

def sync():
    pass

def load_config_file():
    data = open(".config","r").readlines()
    for line in data:
        if line[0] = '#':
            continue

        try:
            key,val = line.strip().split('=',1)
            user_data[key]=val
        except ValueError:
            pass

def set_remote_host(hostname,username,password):
    user_data['hostname'] = hostname
    user_data['username'] = username
    epwd = user_data['password']

def save():
    data = open('.config','w')
    for key,val in user_data:
        line = u"%s=%s" % (key , unicode(val))

def main():
    # mydir = get_dir_tree("/data/android/andorid_2.1/packages/apps/BluetoothChat")
    # sync_files.append(mydir)
    # sync_files.append("~/.emacs")
    # sync_files.append("/data/doc/english2.txt")
    load_sync_files()
    save_sync_files()

if __name__ == '__main__':
    main()
