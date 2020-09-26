#user/bin/env python3
import os
import re
import sys

def exe(args): #exec
    for dir in re.split(":", os.environ['PATH']): # try each directory in the path
        program = "%s/%s" % (dir, args[0])
        try:
            os.execve(program, args, os.environ) # try to execute program
        except FileNotFoundError:
            pass
        os.write(2, ("Command %s not found. Try again.\n" % args[0]).encode())
        sys.exit(1)


def run_cmd(command):
    rc = os.fork()      #create child process
    args = command.copy()#copies the commands to the child

    if rc < 0:#fork forked up
        os.write(1, ("fork failed, returning %d\n" % rc).encode())#inform user of error that occured
        sys.exit(1)
    #continue checking for commands if the fork did not fail
    if '&' in args:
        args.remove('&')#remove & and continue the process
    if rc == 0:#child running
        if '>' in args:#redirect output
            os.close(1)#close current write
            os.open(args[-1], os.O_CREAT | os.O_WRONLY);#opens output file to write in
            os.set_inheritable(1, True)#allows child to inherit
            newArg = args[0:args.index(">")]#updates arguments to get the cmd we need to run
            exe(newArg)
        elif '<' in args:#redirect input
            os.close(0)#close current read
            os.open(args[-1], os.O_RDONLY);#opens input to read from
            os.set_inheritable(0, True)#allows child to inherit
            newArg = args[0:args.index("<")]#updates arguments to get the cmd we need to run
            exe(newArg)
        elif '/' in args[0]:
            prog = args[0]#get program path
            try:
                os.execve(prog,args,os.environ)#attempt running program at given path
            except FileNotFoundError:
                os.write(1,("File not found at %s\n" % prog).encode())#give user failure
        elif '|' in args:
            writeCommands = args[0:args.index("|")]
            readCommands = args[args.index("|") + 1:]
            pr, pw = os.pipe()
        #no command runs so just run cmd givin
        exe(args)
    #        if "ls" in args:
    #            items = os.listdir(os.getcwd())#lists current items in current dir
    #            for i in range(len(items)):
    #                os.write(1,(items[i]+ "\t").encode())
    #            os.write(1,("\n").encode())
    elif not '&' in command:
        childPidCode = os.wait()#wait and get child pid with return code


