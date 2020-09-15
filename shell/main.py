#user/bin/env python3
import os
import re
import sys

#parent pid saved

pid = os.getpid()

def get_input():
    return os.read(0, 1024).decode()[:-1]

def exec_path(args):
    try:
        os.execve(args[0], args, os.environ)
    except FileNotFoundError:
        pass

def global_exec(args):
    for dir in re.split('[\x3a]', os.environ['PATH']):
        program = "%s/%s" % (dir, args[0])
        try:
            os.execve(program, args, os.environ)
        except FileNotFoundError:
            pass

def change_dir(query):
    cmd, path = re.split(' ', query)
    if path != '..':
        path = os.getcwd() + '/' +  path
    os.chdir(path)

def pipe_cmds(query):
    r,w = os.pipe()
    for f in (r,w):
        os.set_inheritable(f, True)
    # split by |
    cmds = [i.strip() for i in re.split('[\x7C]', query)]
    childs = []
    parent = True
    ev = 0
    for cmd in cmds:
        ev = ev + 1
        ab = os.fork()
        if ab:
            childs.append(ab)
           sys.stdout = os.fdopen(write, "w")
                fd = sys.stdout.fileno()
                os.set_inheritable(fd, True)
            else:
                os.close(0) # close stdin
                read = os.dup(r)
                for a in (r,w):
                    os.close(a)

                sys.stdin = os.fdopen(read, "r")
                fd = sys.stdin.fileno()
                os.set_inheritable(fd, True)

            args = [i.strip() for i in re.split('[\x20]', cmd)]
            global_exec(args)
            break
    if parent:
        for a in (r,w):
            os.close(a)

        for child in childs:
            os.waitpid(child, 0)

def command_output_to_file(query):
    cmd, file_path = [i.strip() for i in re.split('[\x3e]', query)] # split by >
    file_path = os.getcwd() + '/' + file_path
    cmd = [i.strip() for i in re.split('[\x20]', cmd)]

    rc = os.fork()
    if rc < 0:
        os.write(2, ("fork failed, returning with %d\n").encode())
        sys.exit(1)
    elif rc == 0:
        os.close(1) # close stdout

        sys.stdout = open(file_path, 'w+')
        fd = sys.stdout.fileno()
        os.set_inheritable(fd, True)
        os.dup(fd)

        global_exec(cmd)
        os.write(2, ("Command %s not found\n" % args[0]).encode())
        sys.exit(1) # we return with error beacuse execv overrides our current process memeory
    else:
        r_child = os.waitpid(rc, 0)

def execute_cmd(query):
    rc = os.fork()
    if rc < 0:
        os.write(2, ("fork failed, returning with %d\n").encode())
        sys.exit(1)
    elif rc == 0:
        args = [i.strip() for i in re.split('[\x20]', query)] # split by space
        if '\x2f' in args[0]:
            exec_path(args)
        else:
            global_exec(args)
        os.write(2, ("Command %s not found\n" % args[0]).encode())
        sys.exit(1) # we return with error beacuse execv overrides our current process memeory
    else:
        r_child = os.waitpid(rc, 0)


def process_user_query(query):
    if query == '':
        if not os.isatty(sys.stdin.fileno()):
            sys.exit(0)
        return
    elif 'exit' in query:
        sys.exit(0)
    elif 'cd' in query:
        change_dir(query)   # Handle change directory
    elif '\x03' in query:
        sys.exit(0)
    elif '\x7C' in query: # |
        pipe_cmds(query)  # Handle pipe command
    elif '\x3e' in query: # >
        # all output in the command is inputed into the specified file
        command_output_to_file(query)
    else:
        execute_cmd(query)

#file descriptor 0 is for std input
#file descriptor 1 is for std output
#file descriptor 2 is for std error

try:
    sys.ps1 = os.environ['PS1']
except KeyError:
    sys.ps1 = '$ '

if sys.ps1 is None:
    sys.ps1 = '$ '

if __name__ == '__main__':
    while True:
        os.write(1, sys.ps1.encode())
        command = get_input()
        process_user_query(command)                           process_user_query(command)