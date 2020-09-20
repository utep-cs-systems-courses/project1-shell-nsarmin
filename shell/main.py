#user/bin/env python3
import os
import re
import sys

def path(args):
    for dir in re.split(":", os.environ['PATH']): # try each directory in the path
        program = "%s/%s" % (dir, args[0])
        #os.write(1, ("Child:  ...trying to exec %s\n" % program).encode())
        try:
            os.execve(program, args, os.environ) # try to exec program
        except FileNotFoundError:
            pass
    #os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
    sys.exit(1)                 # terminate with error
