# -*- coding: utf-8 -*-
import re
import os
"""
codes analysis src_dir
called by py_sca.py
"""

"""
[file_path]: py_src_file to do component analysis
[return]: modules and src_file_path used in py_src_file
called by srcAnalysis()
"""
def srcfileAnalysis(file_path):
    modules = {}
    with open(file_path, 'r', encoding = 'UTF-8')  as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            # analysis module_name according to rematch
            if re.match(r'import.+', line):
                # import module_name as alis_name
                slices = line.split(",")
                for slicee in slices:
                    slicee = slicee.strip()
                    words = slicee.split()
                    if words[0] == 'import':
                        modules[words[1]] = [file_path]
                    else:
                        modules[words[0]] = [file_path]
            if re.match(r'from.+import', line):
                #from module_name import func_name
                words = line.split()
                modules[words[1].split(".")[0]] = [file_path]
    return modules

"""
RE1 = r'^\s*import\s+([\-a-zA-Z0-9]*)'
RE2 = r'^\s*from\s+([\-a-zA-Z0-9]*)\s*import'
RE3 = r'^\s*__version__.*=.*["\']?([^"\']*)["\']?'
[dir_path]: src_dir to do component analysis
[return]: py_src_files to do component analysis
called by srcAnalysis()
"""
def srcfileFetch(dir_path):
    file_path_list = []
    for filepath, dirnames, filenames in os.walk(dir_path):
        for name in filenames:
            # remove files hidden
            if name.startswith('.'):
                continue
            # fetch py_src_files
            if name.endswith(tuple('.py')):
                file_path_list.append(os.path.join(filepath, name))
    return file_path_list

"""
[dir_path]: src_dir to do component analysis
[return]: modules and src_file_path used in src_dir
"""
def srcAnalysis(dir_path):
    module_src_path_dir = {}
    # fetch py_src_file_path in dir_path
    py_src_files = srcfileFetch(dir_path)
    # analysis modules connected to src_path where module is imported
    for file in py_src_files:
        module_src_path_dir.update(srcfileAnalysis(file))
    return module_src_path_dir

"""
test for srcAnalysis()
"""
def main():
    modules = srcAnalysis("F:/i_tw/my_projects/SSC_security/2_sca/safety-develop/safety/")
    for module_name, src_path in modules.items():
        print(module_name, src_path)
    
if __name__ == '__main__':
    main()