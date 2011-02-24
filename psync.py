#!/usr/bin/env python

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

#save a dir structure to file
def _save_dir(fd, dir):
    if(os.path.isfile(dirpath)):
        return

def save_sync_files():
    pass

def load_sync_files():
    pass

# get a tree object of the dirpath
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

# remove a file from sync list
def remove_sync(path):
    pass

# get sync list
def get_sync_list():
    pass


def sync():
    pass

def main():
    get_dir_tree("/data/android/andorid_2.1/packages/apps/BluetoothChat")

if __name__ == '__main__':
    main()
