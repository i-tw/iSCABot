import source2llvm, llvm2cpg, cpg2pandas
import sys, getopt, os
from mylog import llog


def main(argv):
    input_path = None
    llvm_path = None
    cpg_path = None
    output_path = None # save at ${output_path}/data.pkl

    log_file = None # file

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

    log_fp = open(log_file, "w")

    source2llvm.any2llvm(input_path, llvm_path, log_fp)

    llvm2cpg.convert_cpg(llvm_path, cpg_path, log_fp)

    cpg2pandas.gen_pkl(cpg_path, output_path, input_path, log_fp)

    llog(log_fp, "\n")
    llog(log_fp, "Finished\n")
    llog(log_fp, f"""Input Path:\t{input_path}\n""")
    llog(log_fp, f"""LLVM IR Path:\t{llvm_path}\n""")
    llog(log_fp, f"""Cpg.bin Path:\t{cpg_path}\n""")
    llog(log_fp, f"""Output File:\t{os.path.join(output_path, "data.pkl")}\n""")
    llog(log_fp, f"""Log File:\t{log_file}\n""")
    llog(log_fp, "\n")

    log_fp.close()

if __name__ == "__main__":
   main(sys.argv[1:])
