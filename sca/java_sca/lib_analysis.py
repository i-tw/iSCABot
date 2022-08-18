# -*- coding: utf-8 -*-
import os
import re
"""
codes analysis jar_dir
called by java_sca.py
"""

"""
[dir_path]: jar_dir to analysis module_name and module_version
[return]: module_name, module_version, module_path
called by jarAnalysis
"""
def libfileAnalysis(dir_path):
    modules = []

    # module_name #module_version
    module_regrex = re.compile(r'\s*([\-a-zA-Z0-9_]*)\-((\d+\.)+\d*)\.',re.I | re.M | re.S)
    
    # print(module_name)
    module_path = dir_path
    #module_info = []
    
    files = os.listdir(dir_path)
    for file in files:
        if file.endswith('.jar'):
            Module = re.search(module_regrex, file)
            if Module != None:
                module_name = Module.group(1)
                module_info = Module.group(2)
                modules.append([module_name,module_name,module_info,dir_path])
    return modules
                    
"""
[dir_path]: jar_dir to do analysis module_info
[return]: jar_dir_path to analysis
called by jarAnalysis
"""
def jarfileFetch(dir_path):
    jar_dir_list = []
    for filepath, dirnames, filenames in os.walk(dir_path):
        for name in filenames:
            # remove files hidden
            if name.startswith('.'):
                continue
            # fetch dir with __init__.py file
            if name.endswith('.jar'):
                jar_dir_list.append(filepath)
                break
    return jar_dir_list

"""
[dir_path]: lib_dir to do module analysis
[return]: modules and module_version in lib
"""
def libAnalysis(dir_path):
    module_vendor_version_path_dir = []
    # fetch jar_lib_path in dir_path
    jar_lib_path = jarfileFetch(dir_path)
    # analysis modules connected with version and path
    for lib in jar_lib_path:
        modules = libfileAnalysis(lib)
        if modules is not None:
            for module in modules:
                module_vendor_version_path_dir.append(module)
    return module_vendor_version_path_dir

"""
test for libAnalysis()
"""
def main():
    modules = libAnalysis("./test_prog/lib")
    for module in modules:
        print(module)
    
if __name__ == '__main__':
    main()