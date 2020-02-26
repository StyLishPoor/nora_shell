import os
import sys
#ビルトインか確認
def built_in_check(cmd):
    if((cmd =="cd") or (cmd == "exit")):
        return True
    else:
        return False 

#cdの実装    
def mycd(cmd):
    cmdlen = len(cmd)
    if(cmdlen == 1 or cmd[1] == "~"):
        os.chdir(os.environ['HOME'])
    else:
        if(os.path.isdir(cmd[1])):
            os.chdir(cmd[1])
        else:
            sys.stderr.write("No such file or directory\n")     

#pipeの数をカウント
def count_pipe(cmd):
    count = 0
    for i in cmd:
        if(i == '|'):
            count += 1
    return count

#pipeの位置で命令を分割
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

#一応，proc_argvを表示（多分消す）
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

#リダイレクトが必要か確認
def is_redirect(cmd):
    for x in cmd:
        if(x == ">" or x == ">>" or x == "<"):
            return True
    return False        

#両端以外のパイプ処理，cmdを実行
def pipe_continue(r_old,w_old,cmd):
    r_new, w_new = os.pipe()
    pid = os.fork()
    if(pid < 0):
        sys.stderr.write("fork error")
    elif(pid == 0):
        os.dup2(r_old,0)
        os.dup2(w_new,1)
        os.close(r_old)
        os.close(w_new)
        if(os.execvp(cmd[0],cmd) < 0):
            exit(1)
    else:
        #ここで親プロセスのr,wをclose
        os.close(r_old)
        os.close(w_old)
        os.waitpid(pid,0)
    return r_new,w_new

    

while True:
    sys.stderr.write("mysh$ ")
    usr_in = input() 
    usr_split = usr_in.split()
    proc_argv = split_proc(usr_split)
    #show_proc(proc_argv)
    #パイプ無しの場合
    if(count_pipe(usr_split)==0):
        # コマンドの数だけループ
        for i in range(len(proc_argv)): 

            #ビルトインではない場合
                if(built_in_check(proc_argv[i][0])==False): 
                    pid = os.fork()
                    if(pid < 0):
                        sys.stderr.write("fork error")
                    elif(pid == 0):
                        #リダイレクト処理(ここ関数化させたい)
                        if(is_redirect(proc_argv[i])==True): 
                            mark = proc_argv[i][-2]
                            if(mark == ">"): 
                                try:
                                    fd = open(proc_argv[i][-1],'w') 
                                    #必ずcloseするために例外処理
                                    try:
                                        fno = fd.fileno()                
                                        os.dup2(fno,sys.stdout.fileno())
                                        if(os.execvp(proc_argv[i][0],proc_argv[i][0:-2]) < 0):
                                            exit(1)
                                    finally:
                                        fd.close
                                except:
                                    sys.stderr.write("file open error¥n")
                            #以下，">"の場合と同様        
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
                                    sys.stderr.write("file open error¥n")

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
                                    sys.stderr.write("file open error¥n")
                        #リダイレクト処理のない通常バージョン
                        else: 
                            if(os.execvp(proc_argv[i][0],proc_argv[i]) < 0):
                                exit(1)                      
                    else: 
                        os.waitpid(pid,0)
                #　ビルトインコマンドの処理    
                else: 
                    if(proc_argv[i][0] == "cd"):
                        mycd(proc_argv[i])
                    elif(proc_argv[i][0] == "exit"):
                        sys.exit(0)
                      
    #パイプ処理(とりあえず１段)
    else:
        r,w = os.pipe()
        pd1 = os.fork()
        #最初のプロセス（lsとか）
        if(pd1 < 0):
            sys.stderr.write("fork error")
        elif(pd1 == 0):
            os.close(r)
            #まず，標準出力を書き込み領域へ
            os.dup2(w,1)
            os.close(w)
            if(os.execvp(proc_argv[0][0],proc_argv[0]) < 0):
                exit(1)
        else:
            os.waitpid(pd1,0)
        
        #次のプロセス（grepとかwcとか）
        pd2 = os.fork()
        if(pd2 < 0):
            sys.stderr.write("fork error")
        elif(pd2 == 0):
            os.close(w)
        #読み取り領域から標準入力へ
            os.dup2(r,0)
            os.close(r)
            if(os.execvp(proc_argv[1][0],proc_argv[1]) < 0):
                exit(1)
        else:
            os.close(r)
            os.close(w)
            os.waitpid(pd2,0)
            
    #パイプ処理(多段)
    else:
        #コマンドの数だけ実行
        cmd_num = len(proc_argv)
        r_tmp,w_tmp = os.pipe()
        for i in range(cmd_num):
            #最初と最後は異なる
            #最初の処理
            if(i == 0):
                pid = os.fork()
                if(pid < 0):
                    sys.stderr.write("fork error")
                elif(pid == 0):
                        os.close(r_tmp)
                        os.dup2(w_tmp,1)
                        os.close(w_tmp)
                        if(os.execvp(proc_argv[i][0],proc_argv[i]) < 0):
                            exit(1)
                else:
                    os.waitpid(pid,0)
            #途中の処理
            elif(i > 0 and i < cmd_num-1):
                r_tmp,w_tmp = pipe_continue(r_tmp,w_tmp,proc_argv[i])
            #最後の処理
            else:
                pid = os.fork()
                if(pid < 0):
                    sys.stderr.write("fork error")
                elif(pid == 0):
                    os.close(w_tmp)
                    os.dup2(r_tmp,0)
                    os.close(r_tmp)
                    if(os.execvp(proc_argv[i][0],proc_argv[i]) < 0):
                        exit(1)
                else:
                    os.close(r_tmp)
                    os.close(w_tmp) 
                    os.waitpid(pid,0)
