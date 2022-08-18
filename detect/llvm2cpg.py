import os
from mylog import llog


def convert_cpg(target_path, output_path, log_fp):

    llog(log_fp, f"""[Info] Start turning llvm code to cpg\n""")
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

    for root, dirs, files in os.walk(target_path):
        for dir in files:
            output_path_name = os.path.join(output_path, os.path.join(root.replace(target_path, "", 1).lstrip('/'), ""))
            # output_path_name = os.path.join(output_path, root.replace(target_path+"/",""))
            try:
                if (os.system(f"""llvm2cpg --output-dir={output_path_name} -output-name={dir}.bin.zip {os.path.join(root,dir)}""") != 0):
                    llog(log_fp, f"""[Failed] [llvm2cpg] convert {os.path.join(target_path,dir)} to cpg.bin.zip failed\n""")
                    
                else:
                    llog(log_fp, f"""[Info] [llvm2cpg] convert {os.path.join(target_path,dir)} to cpg.bin.zip succeed\n""")
            except:
                llog(log_fp, f"""[Failed] [llvm2cpg] convert {os.path.join(target_path,dir)} to cpg.bin.zip failed\n""")
                continue



if __name__ == '__main__':
    target_path = "./source_data_llvm"
    output_path = "./source_data_cpg"
    log_path = "./llvm2cpg.log"
    log_fp = open(log_path, "w")
    convert_cpg(target_path, output_path, log_fp)
    log_fp.close()
