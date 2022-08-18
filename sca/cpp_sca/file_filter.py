# -*- coding: utf-8 -*-
import os
"""
codes filter *.cmake   CMakeLists.txt
called by cpp_sca.py
"""

"""
[proj_dir]: proj_dir to do component analysis
[return]: cmake_files to extract info
"""
def cmakeFilter(proj_dir: str):
    file_list = []
    for filepath, dirnames, filenames in os.walk(proj_dir):
        for name in filenames:
            # remove files hidden
            if name.startswith('.'):
                continue
            # filter *.cmake
            if name.endswith(tuple('.cmake')):
                file_list.append(os.path.join(filepath, name))
            # filter CMakeLists.txt
            if name == 'CMakeLists.txt':
                file_list.append(os.path.join(filepath, name))
    return file_list

"""
test for cmakeFilter()
"""
def main():
    file_list = cmakeFilter('./test_prog/')
    for file in file_list:
        print(file)
    
if __name__ == '__main__':
    main()