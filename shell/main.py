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

