#!/usr/bin/env python

# jianjun create the psync project at feb 24,2011
# psync to for management the sync file to communitcat
# with reomte computer
# jianjun365222@gmail.com

import os, sys, subprocess, shlex

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
        f = {}
        if(line.startswith("F  ")):  # a file to sync
            f["type"] = "file"
            f["content"] = line.split()[1]
        elif(line.startswith("DS ")):   # a dir to sync
            f["type"] = "dir"
            f["content"] = _load_dir_tree(fd)

        f["remote"] = line.split("->")[1]

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
            fd.write('F  '+ f["content"]+ " -> "+ f["remote"]+ "\n")
        elif f["type"] == "dir":
            fd.write('DS '+ f["content"]["name"]+ " -> "+ f["remote"]+ '\n')
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
            print(file_path)
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
    elif os.path.isdir(local_path):
        sync_files.append(local_path)
    elif os.path.isfile(local_path):
        dir_tree = get_dir_tree(local_path)
        sync_files.append(dir_tree)

# remove a file from sync tree , path is a file or dir on the 
# computer
def remove_from_sync(path):
    remove_file = False
    found_file = False
    if os.path.ispath(path):
        remove_file = True

    for f in sync_files:
        if remove_file and f["type"] == "file" and f["content"] == path:
            sync_files.remove(f)
            found_file = True
            break
        elif !remove_file and f["type"] == "dir" and f["content"]["name"] == path:
            sync_files.remove(f)
            found_file = True
            break

    if not found_file:
        print("the path not contained in the sync list")

# get sync list
def list_sync_file(deep=None):
    pass

# make a sync to remote computer
def sync(push=None):
    push_file = True
    if push == False:
        push_file = False

    for f in sync_files:
        if f["type"] == "file":
            do_sync_file(f["content"],f["remote"])
        elif f["type"] == "dir":
            do_sync_dir(f["content"],f["remote"])

push_cmd = "rsync %(localfile)s %(username)s@%(hostname):%(remote)"
pull_cmd = "rsync %(username)s@%(hostname):%(remote) %(localfile)s"
create_dir_cmd = "ssh %(username)s@%(hostname)s \"cd %(path);mkdir %(dir_name)\" "
check_dir_exist = "rsync %(username)s@%(hostname)s:%(remote_dir)s|grep %(dir_name)s"

#first check if remote dir is exist , if not , create it
def _check_remote_dir(local_dir,remote_dir):
    cmd = check_dir_exist % {
        'username' : user_data["username"]
        'hostname' : user_data["hostname"]
        'remote_dir' : os.path.dirname(remote_dir)
        'dir_name' : os.path.basename(remote_dir)
        }

    ret = subprocess.call(cmd, shell=True)
    if ret == 0: # ok ,dir exist
        return

    # on , create one
    cmd = create_dir_cmd %{
        'username' : user_data["username"]
        'hostname' : user_data["hostname"]
        'path' : os.path.dirname(remote_dir)
        'dir_name' : os.path.basename(remote_dir)
        }

    ret = subprocess.call(cmd,shell=True)
    if ret == 1:
        print("error : can't create dir on remote computer!")
        os.exit()


#sync a local dir to a remote dir recursivly
def do_sync_dir(local_dir, remote_dir, sync_type=None):
    #if remote computer have not the dir , create it
    _check_remote_dir(local_dir["name"],remote_dir);
    
    for f in local_dir["filelist"]:
        f_dir = os.path.join(local_dir["name"],f)
        do_sync_file(f,remote_dir,sync_type)
        
    remote_dir = os.path.join(remote_dir,os.path.basename(local_dir["name"]))
    for d in local_dir["dirlist"]:
        do_sync_dir(d,remote_dir,sync_type)


#sync a local file with a remote file,default sync type is push
def do_sync_file(local_file, remote_dir, sync_type=None):
    if sync_type == 'pull':
        cmd = pull_cmd
    elif:
        cmd = push_cmd

    cmd = push_cmd % {
        'localfile' : local_file,
        'remote' : remote_file,
        'username' : user_data["username"]
        'hostname' : user_data["hostname"]
        }

    env = os.environ.copy()
    env["RSYNC_PASSWORD"] = user_data["password"]
    ret = subprocess.call(cmd, env=env, shell=True)
    if ret == -1:
        print("sync %s failed" % local_file)

def load_config_file():
    data = open(".config","r").readlines()
    for line in data:
        if line[0] = '#':
            continue
        try:
            key,val = line.strip().split('=',1)
            if key == 'password':
                val = base64.decodestring(val)
            user_data[key]=val
        except ValueError:
            pass

def set_remote_host(hostname,username,password):
    user_data['hostname'] = hostname
    user_data['username'] = username
    user_data['password'] = password

def save():
    data = open('.config','w')
    for key,val in user_data:
        if key == 'password':
            val = base64.encodestring(val)
        line = u"%s=%s" % (key , unicode(val))
        data.write(line)

def usage():
    sys.stderr.write("""Usage: %(progName)s [<option>]
Options:
    --now [ pull | push ]
         make a sync to remote computer now , the default is push
    --add localPath remotePath
         add a file or dir to the sync tree 
    --rm  path
         remove a file or dir frome the sync tree
    --list [ deep ]
         list the sync file list , if the deep is provided ,all subdirctoriry 
         will be printed
""" % {    "progName": os.path.split(sys.argv[0])[1],   })
    sys.exit(1)

def test():
    # mydir = get_dir_tree("/data/android/andorid_2.1/packages/apps/BluetoothChat")
    # sync_files.append(mydir)
    # sync_files.append("~/.emacs")
    # sync_files.append("/data/doc/english2.txt")
    load_sync_files()
    save_sync_files()

def main(argv):

    if len(argv) > 3:
        usage()

    # load the sync file 
    load_sync_files()
    load_config_file()

    sync_file_changed = False
    arg = argv[1]
    if arg.startswith("--now"):
        sync()
    elif arg.startswith("--add") or arg.startswith("--rm"):
        path = argv[2]
        if os.path.exist(path):
            if arg.startswith("--add"):
                add_to_sync(arg[2])
            else:
                remove_from_sync(arg[2])
            sync_file_changed = True                
        else:
            print("%1 did not exit in you system ,check it" % path)
    elif arg.startswith("--list"):
        deep_list=False
        if len(argv) == 3 and argv[2]=="deep":
            deep_list=True
        list_sync_file(deep)

    if sync_file_changed :
        save_sync_files()
            
if __name__ == '__main__':
    main(sys.argv)
