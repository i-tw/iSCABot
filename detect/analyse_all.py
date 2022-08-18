import sys, getopt, os
import time, pymysql

import source2llvm, llvm2cpg, cpg2pandas
from mylog import llog

import prepare.cpg2pyg_prediction as cpg2pyg_prediction
import prediction_all


def main(argv):
    input_path = None
    llvm_path = None
    cpg_path = None
    output_path = None # save at ${output_path}/data.pkl

    log_file = None # file

    # === args parse begin ===
    try:
        opts, args = getopt.getopt(argv,"",["help","input-path=","output-path=","llvm-path=","cpg-path=","log="])
    except getopt.GetoptError:
        print('''analyse.py [options]\n''')
        print('''--input-path\t: source project dir''')
        print('''--llvm-path\t: LLVM IR code dir (tmp files)''')
        print('''--cpg-path\t: .bin.zip joern files dir (tmp files)''')
        print('''--output-path\t: final output dir, output pkl file is data.pkl''')
        print('''--log\t: log file''')
        sys.exit(2)
    for opt, arg in opts:
        if opt == "--help":
            print('''analyse.py [options]\n''')
            print('''--input-path\t: source project dir''')
            print('''--llvm-path\t: LLVM IR code dir (tmp files)''')
            print('''--cpg-path\t: cpg.bin joern files dir (tmp files)''')
            print('''--output-path\t: final output dir, output pkl file is data.pkl''')
            print('''--log\t: log file''')
            sys.exit()
        elif opt == "--input-path":
            input_path = arg
        elif opt == "--output-path":
            output_path = arg
        elif opt == "--llvm-path":
            llvm_path = arg
        elif opt == "--cpg-path":
            cpg_path = arg
        elif opt == "--log":
            log_file = arg
    
    if(input_path is None) or (output_path is None) or \
        (llvm_path is None) or (cpg_path is None) or \
        (log_file is None):
        print('''analyse.py [options]\n''')
        print('''--input-path\t: source project dir''')
        print('''--llvm-path\t: LLVM IR code dir (tmp files)''')
        print('''--cpg-path\t: .bin.zip joern files dir (tmp files)''')
        print('''--output-path\t: final output dir, output pkl file is data.pkl''')
        print('''--log\t: log file''')
        sys.exit(2)
        
    print("\n")
    print('Input Path:\t', input_path)
    print('LLVM IR Path:\t', llvm_path)
    print('Cpg.bin Path:\t', cpg_path)
    print('Output File:\t', os.path.join(output_path, "data.pkl"))
    print('Log File:\t', log_file)
    print("\n")
    # === args parse end ===

    # === source2pandas begin ===
    log_fp = open(log_file, "w")

    source2llvm.any2llvm(input_path, llvm_path, log_fp)

    llvm2cpg.convert_cpg(llvm_path, cpg_path, log_fp)

    cpg2pandas.gen_pkl(cpg_path, output_path, input_path, log_fp)

    llog(log_fp, "\n")
    llog(log_fp, "[info] Source2pandas Finished\n")
    llog(log_fp, f"""[info] Input Path:\t{input_path}\n""")
    llog(log_fp, f"""[info] LLVM IR Path:\t{llvm_path}\n""")
    llog(log_fp, f"""[info] Cpg.bin Path:\t{cpg_path}\n""")
    llog(log_fp, f"""[info] Output File:\t{os.path.join(output_path, "data.pkl")}\n""")
    llog(log_fp, f"""[info] Log File:\t{log_file}\n""")
    llog(log_fp, "\n")

    log_fp.close()
    # === source2pandas end ===


    # === pandas2output start ===
    dir_path = os.path.join(output_path, "data.pkl")
    cpg2pyg_prediction.cpg2pyg(dir_path)
    output = prediction_all.pyg2prediction(dir_path)
    print(output)
    # === pandas2output end ===
    

    # input var:    (list of dicts)
    # === output2mysql start ===
    connect = pymysql.connect(host='127.0.0.1',user='root',password='password',db='supplychain',charset='utf8')
    cur = connect.cursor()
    
    if output:
        name = output[0]['name']
        version = output[0]['version']
        now = time.localtime()
        date = time.strftime("%Y-%m-%d %H:%M:%S", now)
        
        sql = "DELETE FROM Vulndata where name=%s and version=%s;"
        cur.execute(sql,[name,version])
        connect.commit()
        
        for vulndata in output:
            sql = "INSERT INTO Vulndata VALUES(%s,%s,%s,%s,%s,%s);"
            cur.execute(sql,[name,version,vulndata['func'],vulndata['cwe_id'],vulndata['path'],date])
            connect.commit()
            
    cur.close()
    connect.close()
    # === output2mysql end ===
    

if __name__ == "__main__":
   main(sys.argv[1:])
