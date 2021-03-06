#!/usr/bin/env python3.1

#
#   jianjun create the psync project at feb 24,2011
#   psync to for management the sync file to communicate
#   with reomte computer
#   jianjun365222@gmail.com
# 

import os, sys, subprocess, shlex, getopt, base64
from datetime import datetime

# the sync file list , orginazed as a list of dir or files
# dir contains files , the structure is descript bellow
#
#      |--"name":dir name
#      |  
#      |
# dir -|--"filelist":["filename1","filename2",]
#      |
#      |--"dirlist":["structrue of dir list",]
#
# dir = {"name":"root","remote":None,"filelist":[],"dirlist":[]}
#

#element is dictionary {"type":dir_or_file,"content":file.name.path_or_dir.
#                       structure,"remote_path":remote_location}
sync_files=[]

sync_file="./synclist"

user_data={}

SYNCDIR = True

#read frome the file , at a line started by "di" ,
#and read on , to construct a dir structrue
def _load_dir_tree(fd,dir_name=None):
    dir_tree={}

    if dir_name is None:
        dir_tree["name"]=fd.readline().split()[1]
    else :
        dir_tree["name"]=dir_name

    dir_tree["filelist"]=[]
    dir_tree["dirlist"]=[]

    while 1:
        line = fd.readline()
        if not line:
            break
        if(line.startswith("do")):
            return dir_tree
        elif(line.startswith("f ")):
            dir_tree["filelist"].append(line.split()[1])
        elif(line.startswith("di ")):
            dir_tree["dirlist"].append(_load_dir_tree(fd,line.split()[1]))
        else:
            print("Error synclist file!")
            exit(1)

    return dir_tree

#load sync file from disk to sync_files
def load_sync_files():
    fd = open(sync_file,"r")
    while 1:
        line = fd.readline()
        if not line:
            break
        f = {}

        if(line.startswith("F  ")):  # a file to sync
            f["type"] = "file"
            f["content"] = line.split()[1]
        elif(line.startswith("DS ")):   # a dir to sync
            f["type"] = "dir"
            f["content"] = _load_dir_tree(fd)

        f["remote_path"] = line.split("->")[1].strip()

        sync_files.append(f)
    fd.close()

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

#save sync_files sync file to disk 
def save_sync_files():
    fd = open(sync_file,"w")
    for f in sync_files:
        if f["type"] == "file":
            fd.write('F  '+ f["content"]+ " -> "+ f["remote_path"]+ "\n")
        elif f["type"] == "dir":
            fd.write('DS '+ f["content"]["name"]+ " -> "+ f["remote_path"]+ '\n')
            _save_dir_tree(fd,f["content"])
    fd.close()


# get a tree object of the dirpath on the computer
def _get_dir_tree(dirpath):
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
            current['filelist'].append(f)
        if os.path.isdir(file_path):
            current['dirlist'].append( _get_dir_tree( file_path ) )

    return current


# get a path's position in sync file
# if it is a new path , return -1
def get_file_index_position(path):
    pass

# add a file to sync list
def add_to_sync(local_path,remote_path):
    if not os.path.exists(local_path):
        printf("%1 did not exists in you system!" % local_path)

    f = {}

    if os.path.isdir(local_path):
        f["type"] = "dir"
        f["content"] = _get_dir_tree(local_path)
    elif os.path.isfile(local_path):
        f["type"] = "file"
        f["content"] = local_path

    f["remote_path"] = remote_path
    sync_files.append(f)

# remove a file from sync tree , path is a file or dir on the 
# computer
def remove_from_sync(path=None):
    remove_file = False
    found_file = False
    if os.path.isfile(path):
        remove_file = True

    for f in sync_files:
        if remove_file and f["type"] == "file" and f["content"] == path:
            sync_files.remove(f)
            found_file = True
            break
        elif remove_file is not True and f["type"] == "dir" and f["content"]["name"] == path:
            sync_files.remove(f)
            found_file = True
            break

    if not found_file:
        print("the path not contained in the sync list")

# get sync list
def print_sync_list(dir_tree=None,deep=False):
    if dir_tree is None:
        for f in sync_files:
            if f["type"] == "file":
                print("FILE "+ f["content"]+ " -> "+ f["remote_path"])
            elif f["type"] == "dir":
                print("DIR  "+ f["content"]["name"]+ " -> "+ f["remote_path"])
                if deep :
                    print_sync_list(f["content"])

    else:
        for f in dir_tree["filelist"]:
            print("f "+f)
        for f in dir_tree["dirlist"]:
            print("d "+f["name"])
            print_sync_list(f)

# make a sync to remote computer
def sync(sync_type = None):
    if sync_type==None:
        sync_type = "push"
    if sync_type not in ["push","pull"]:
        error("please choose right sync method: push,push or None")

    color_green_start = "\033[102m\033[95m"
    color_cyan_start = "\033[95m"
    color_end = "\033[0m"
    sync_sign = color_green_start+ "<-"+ color_end
    if sync_type == "push":
        sync_sign = color_green_start+ "->"+ color_end

    start_time = datetime.now()
    print("Remote  %s\nStart Time    %s\nType  %s \n" % (user_data["hostname"],start_time,sync_type))

    for f in sync_files:
        if f["type"] == "file":
            print("%sSYNC FILE%s : local: %s %s remote: %s" % (color_cyan_start,color_end,f["content"],sync_sign,f["remote_path"]) )
            do_sync_file(f["content"],f["remote_path"],sync_type)
        elif f["type"] == "dir":
            print("%sSYNC DIR%s : local: %s %s remote: %s" % (color_cyan_start,color_end,f["content"]["name"],sync_sign,f["remote_path"]) )
            do_sync_dir(f["content"],f["remote_path"],sync_type)
    end_time = datetime.now()
    print("\nsync end at %s" %(end_time))
    print("time used: %s " % (end_time - start_time))

push_cmd = "rsync -av  %(localfile)s %(username)s@%(hostname)s:%(remote)s > /dev/null"
pull_cmd = "rsync -av  %(username)s@%(hostname)s:%(remote)s %(localfile)s > /dev/null"
create_dir_cmd = "ssh %(username)s@%(hostname)s \"cd %(path)s;mkdir %(dir_name)s\" >/dev/null "
check_dir_exist = "rsync %(username)s@%(hostname)s:%(remote_dir)s|grep ^d.*\ %(dir_name)s$ > /dev/null"

#first check if remote dir is exist , if not , create it
def _check_remote_dir(local_dir,remote_dir):
    cmd = check_dir_exist % {
        'username' : user_data["username"],
        'hostname' : user_data["hostname"],
        'remote_dir' : os.path.dirname(remote_dir)+"/",
        'dir_name' : os.path.basename(local_dir)
        }

    ret = subprocess.call(cmd, shell=True)
    if ret == 0: # ok ,dir exist
        return

    # on , create one
    cmd = create_dir_cmd %{
        'username' : user_data["username"],
        'hostname' : user_data["hostname"],
        'path' : os.path.dirname(remote_dir),
        'dir_name' : os.path.basename(local_dir)
        }

    ret = subprocess.call(cmd,shell=True)
    if ret == 1:
        print("error : can't create dir on remote computer!")
        os.exit()


#sync a local dir to a remote dir recursivly
def do_sync_dir(local_dir, remote_dir, sync_type=None):
    #if remote computer have not the dir , create it
    print(" syncing %s " % local_dir["name"] )

    if SYNCDIR :
        if sync_type == "push":
            do_sync_file(local_dir["name"]+"/",remote_dir,sync_type)
        else:
            do_sync_file(local_dir["name"],remote_dir+"/",sync_type)
        return

    _check_remote_dir(local_dir["name"],remote_dir);
    
    #for f in local_dir["filelist"]:
    do_sync_file(" ".join(local_dir["filelist"]),remote_dir,sync_type)
        
    base_dir = remote_dir
    for d in local_dir["dirlist"]:
        remote_dir = os.path.join(base_dir,os.path.basename(d["name"]))
        do_sync_dir(d,remote_dir,sync_type)

#sync a local file with a remote file,default sync type is push
def do_sync_file(local_file, remote_dir, sync_type=None):
    if sync_type == 'pull':
        cmd = pull_cmd
    else:
        cmd = push_cmd

    cmd = cmd % {
        'localfile' : local_file,
        'remote' : remote_dir,
        'username' : user_data["username"],
        'hostname' : user_data["hostname"]
        }

    env = os.environ.copy()
    #env["RSYNC_PASSWORD"] = user_data["password"]
    ret = subprocess.call(cmd, env=env, shell=True)
    if ret == -1:
        print("sync %s failed" % local_file)

def load_config_file():
    data = open(".config","r").readlines()
    for line in data:
        if line[0] == '#':
            continue
        try:
            key,val = line.strip().split('=',1)
            if key == 'password':
                pass#val = base64.decodestring(val)
            user_data[key]=val
        except ValueError:
            pass
    if not "hostname" in user_data.keys() or not "username" in user_data.keys():
        error("missing remote hostname and username ,you have to set configure file")


def set_remote_host(hostname=None,username=None,password=None):
    if hostname != None:
        user_data['hostname'] = hostname
    if username != None:
        user_data['username'] = username
    if password != None:
        user_data['password'] = password

def save():
    data = open('.config','w')
    print(user_data)
    for key,val in user_data.items():
        if key == 'password':
            pass#val = base64.encodestring(val.encode('utf-8'))
        line = "%s=%s\n" % (key , val)
        data.write(line)
 
def usage():
    sys.stderr.write("""
Usage: 
Add a sync file  : psync --add localpath --to remotepath
Make a push sync : psync [--push]
Make a pull sync : psync --pull
Remove a file from sync :psync --rm filepath
List sync files and dirctorys : psync --list [--deep]

Options:
    --config [host|user|passwd] value
         set the configure value
    --pull 
         make a pull sync to remote computer 
    --push 
         make a push sync to remote computer 
    --add localPath 
         add a file or dir to the sync tree 
    --to remotePath
         set remotepath
    --rm path
         remove a file or dir frome the sync tree
    --list
         list the sync file list 
    --deep
        if the deep is provided ,all subdirctoriry will be printed
    --help
        print this message
""" % {    "progName": os.path.split(sys.argv[0])[1],   })

def error(msg):
    print(msg)
    usage()
    sys.exit(2)


def test():
    print("---run test---")

    mydir = _get_dir_tree("/data/android/andorid_2.1/packages/apps/BluetoothChat")
    element1 = {"type":"dir","content":mydir,"remote_path":"/data/own"}
    sync_files.append(element1)

    element2 = {"type":"file","content":"~/.emacs","remote_path":"/data/own"}
    sync_files.append(element2)

    element3 = {"type":"file","content":"/data/tmp/test.py","remote_path":"/data/tmp"}
    sync_files.append(element3)

    save_sync_files()

def main(argv):
    if argv[1]=="--test":
        test()
        return

    # load the sync file 
    load_sync_files()
    load_config_file()

    sync_file_changed = False
    arg = argv[1]

    local_file=None
    remote_file=None
    print_tree=False
    deep_print=False
    
    try:
        opts, args = getopt.getopt(argv[1:], "l:r:", ["help", "pull","push","add=","to=","rm=","list","deep","test","config="])
    except getopt.GetoptError as err:
        error(err)
    for o, a in opts:

        if o == "--help":
            usage()
            exit(0)
        elif o == "--pull":
            sync("pull")
        elif o == "--push":
            sync("push")
        elif o == "--list":
            print_tree=True
        elif o == "--add":
            sync_file_changed=True
            local_file=a
        elif o == "--to":
            remote_file=a
        elif o == "--rm":
            sync_file_changed=True
            remove_from_sync(a)
        elif o == "--deep":
            deep_print=True
        elif o == "--config":
            if len(argv) != 4:
                error("missing arguments!")
            value = argv[-1:][0]
            if a=="hostname":
                set_remote_host(hostname=value)
            elif a=="username":
                set_remote_host(username=value)
            elif a=="password":
                set_remote_host(password=value)
            else:
                error("no such configure value!")
            save()
        else:
            error("Wrong arguments : %s ! " % o)

    if local_file != None and remote_file != None:
        add_to_sync(local_file,remote_file)
    elif print_tree:
        print_sync_list(deep=deep_print)

    if sync_file_changed :
        save_sync_files()
            
if __name__ == '__main__':
    main(sys.argv)




