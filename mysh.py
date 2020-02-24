import os
import sys
import subprocess

def built_in_check(cmd):
    if((cmd =="cd") or (cmd == "exit")):
        return True
    else:
        return False 
    
def mycd(cmd):
    cmdlen = len(cmd)
    if(cmdlen == 1 or cmd[1] == "~"):
        os.chdir(os.environ['HOME'])
    else:
        if(os.path.isdir(cmd[1])):
            os.chdir(cmd[1])
        else:
            sys.stderr.write("No such file or directory\n")     

def count_pipe(cmd):
    count = 0
    for i in cmd:
        if(i == '|'):
            count += 1
    return count
def split_proc(cmd):
    proc_argv = []
    tmp = []
    for i in range(len(cmd)):
        if(cmd[i] != "|"):
            tmp.append(cmd[i])
        else:
            proc_argv.append(tmp)
            tmp = []
    proc_argv.append(tmp)
    return proc_argv    

def show_proc(proc_argv):
    for i in range(len(proc_argv)):
        print(str(i)+" th Proc")
        for j in range(len(proc_argv[i])):
            if(proc_argv[i][j] == "<"):
                print("redir in: "+ proc_argv[i][j+1])
                break
            elif(proc_argv[i][j] == ">"):
                print("redir out: "+ proc_argv[i][j+1])
                break
            else:
                print("proc_argv[" +str(j)+ "]: " +proc_argv[i][j])        
        print("")    

def is_redirect(cmd):
    for x in cmd:
        if(x == ">" or x == ">>" or x == "<"):
            return True
    return False        

while True:
    sys.stderr.write("mysh$ ")
    usr_in = input() 
    usr_split = usr_in.split()
    proc_argv = split_proc(usr_split)
    show_proc(proc_argv)
    for i in range(len(proc_argv)):
        if(built_in_check(proc_argv[i][0])==False):
            pid = os.fork()
            if(pid < 0):
                sys.stderr.write()
            elif(pid == 0):
                if(is_redirect(proc_argv[i])==True):
                    mark = proc_argv[i][-2]
                    if(mark == ">"):
                        try:
                            fd = open(proc_argv[i][-1],'w')
                            try:
                                fno = fd.fileno()                
                                os.dup2(fno,sys.stdout.fileno())
                                if(os.execvp(proc_argv[i][0],proc_argv[i][0:-2]) < 0):
                                    exit(1)
                            finally:
                                fd.close
                        except:
                            sys.stderr.write("file open error")
                    elif(mark == ">>"):
                        try:
                            fd = open(proc_argv[i][-1],'a')
                            try:
                                fno = fd.fileno()                
                                os.dup2(fno,sys.stdout.fileno())
                                if(os.execvp(proc_argv[i][0],proc_argv[i][0:-2]) < 0):
                                    exit(1)
                            finally:
                                fd.close
                        except:
                            sys.stderr.write("file open error")

                    elif(mark == "<"):
                        try:
                            fd = open(proc_argv[i][-1],'r')
                            try:
                                fno = fd.fileno()                
                                os.dup2(fno,sys.stdin.fileno())
                                if(os.execvp(proc_argv[i][0],proc_argv[i][0:-2]) < 0):
                                    exit(1)
                            finally:
                                fd.close
                        except:
                            sys.stderr.write("file open error")

                else: 
                    if(os.execvp(proc_argv[i][0],proc_argv[i]) < 0):
                        exit(1)                      
            else:
                os.waitpid(pid,0)
        else:
            if(proc_argv[i][0] == "cd"):
                mycd(proc_argv[i])
            elif(proc_argv[i][0] == "exit"):
                sys.exit(0)
