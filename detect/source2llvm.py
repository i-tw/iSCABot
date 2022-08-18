import mxmlparser
import os, re
from mylog import llog


def check_c_cpp(target, log_fp):
    command = f"""file -bNn0 {target}"""
    r = os.popen(command) 
    info = r.readlines()
    if(len(info) >= 1):
        line = info[0]
        if(re.match("^(C\+\+ source)", line) is not None):
            return True
        if(re.match("^(C source)", line) is not None):
            return True
    
    return False

def check_elf(target, log_fp):
    command = f"""file -bNn0 {target}"""
    r = os.popen(command)   
    info = r.readlines()
    if(len(info) >= 1):
        line = info[0]
        if(re.match("^(ELF)", line) is not None):
            return True
    return False


def source2llvm(target_path ,src_dir, inc_cmd, output_path, log_fp):
    for root, dirs, files in os.walk(os.path.join(target_path, src_dir)):
        for dir in files:
            # if (dir.split('.')[-1] == "c" or dir.split('.')[-1] == "cpp"):
            target = os.path.join(root, dir)
            # print(target, "=====")
            if(check_c_cpp(target, log_fp)):
                output_name = os.path.join(output_path, os.path.join(root.replace(target_path, "", 1).lstrip('/'),f"{dir}.ll"))
                # print(output_name, "========")
                if (os.system(f"""clang -c -S -emit-llvm {os.path.join(root,dir)} {inc_cmd} -o {output_name}""") != 0):
                    llog(log_fp, f"""[Failed] [source2llvm] compile {os.path.join(root,dir)} to llvm code failed\n""")
                else:
                    llog(log_fp, f"""[Info] [source2llvm] compile {os.path.join(root,dir)} to llvm code succeed\n""")

def bin2llvm(target_path, bin_dir, output_path, log_fp):
    for root, dirs, files in os.walk(os.path.join(target_path, bin_dir)):
        for dir in files:
            if (os.path.isfile(os.path.join(root,dir))):
                output_name = os.path.join(output_path, os.path.join(root.replace(target_path, "", 1).lstrip('/'),f"{dir}.c"))
                # target.o 生成 target.o.bc  target.o.c  target.o.config.json  target.o.dsm  target.o.ll
                if (os.system(f"""retdec-decompiler {os.path.join(root,dir)} -o {output_name}""") != 0):
                    tmp = os.path.join(output_path, os.path.join(root.replace(target_path, "", 1).lstrip('/'),f"{dir}.c"))
                    os.system(f"""rm {tmp}""")
                    tmp = os.path.join(output_path, os.path.join(root.replace(target_path, "", 1).lstrip('/'),f"{dir}.config.json"))
                    os.system(f"""rm {tmp}""")
                    tmp = os.path.join(output_path, os.path.join(root.replace(target_path, "", 1).lstrip('/'),f"{dir}.dsm"))
                    os.system(f"""rm {tmp}""")
                    tmp = os.path.join(output_path, os.path.join(root.replace(target_path, "", 1).lstrip('/'),f"{dir}.ll"))
                    os.system(f"""rm {tmp}""")
                    llog(log_fp, f"""[Failed] [bin2llvm] decompile {os.path.join(root,dir)} to llvm binary code failed\n""")
                else:
                    tmp = os.path.join(output_path, os.path.join(root.replace(target_path, "", 1).lstrip('/'),f"{dir}.c"))
                    os.system(f"""rm {tmp}""")
                    tmp = os.path.join(output_path, os.path.join(root.replace(target_path, "", 1).lstrip('/'),f"{dir}.config.json"))
                    os.system(f"""rm {tmp}""")
                    tmp = os.path.join(output_path, os.path.join(root.replace(target_path, "", 1).lstrip('/'),f"{dir}.dsm"))
                    os.system(f"""rm {tmp}""")
                    tmp = os.path.join(output_path, os.path.join(root.replace(target_path, "", 1).lstrip('/'),f"{dir}.ll"))
                    os.system(f"""rm {tmp}""")
                    llog(log_fp, f"""[Info] [bin2llvm] decompile {os.path.join(root,dir)} to llvm binary code succeed\n""")


def any2llvm(target_path, output_path, log_fp):
    # target_path: target project dir
    # output_path: output dir
    # log_path: error log

    llog(log_fp, f"""[Info] Start turning source project to llvm code\n""")
    llog(log_fp, f"""[Info] Target Path: {target_path}\n""")
    llog(log_fp, f"""[Info] Output Path: {output_path}\n""")

    if(os.path.isfile(target_path)):
        llog(log_fp, f"""[Error] Output Path: {target_path} is a file\n""")
        return

    if(not os.path.isdir(target_path)):
        llog(log_fp, f"""[Error] Target Path: {target_path} is not existed\n""")
        return

    if(os.path.isfile(output_path)):
        llog(log_fp, f"""[Error] Output Path: {output_path} is a file\n""")
        return

    if(os.path.isdir(output_path)):
        llog(log_fp, f"""[Warning] Output Path: {output_path} is already existed, auto deleted\n""")
        os.system(f"""rm -rf {output_path}""")

    llog(log_fp, f"""[Info] Create Output dir: {output_path}\n""")
    os.system(f"""mkdir {output_path}""")
    for root, dirs, files in os.walk(target_path):
        for name in dirs:
            # print(os.path.join(output_path, name))
            os.system(f"""mkdir {os.path.join(output_path, os.path.join(root.replace(target_path, "", 1).lstrip('/'), name))}""")

    info = mxmlparser.mxmlparser(target_path, log_fp)
    if(info == None):
        return

    # print(info)

    inc_cmd = ""
    for dir in info["include"]:
        inc_cmd = inc_cmd + "-I \"" + os.path.join(target_path, dir) + "\" "

    llog(log_fp, """[Info] Start truning c/cpp files to llvm code\n""")
    for src_dir in info["source"]:
        source2llvm(target_path, src_dir, inc_cmd, output_path, log_fp)

    llog(log_fp, """[Info] Start truning binary files to llvm code\n""")
    for bin_dir in info["binary"]:
        bin2llvm(target_path, bin_dir, output_path, log_fp)


if __name__ == '__main__':
    target_path = "./source_data"
    output_path = "./source_date_llvm"
    log_path = "./source2llvm.log"
    log_fp = open(log_path, "w")
    any2llvm(target_path, output_path, log_fp)
    log_fp.close()
