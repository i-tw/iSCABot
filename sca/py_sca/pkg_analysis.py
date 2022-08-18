# -*- coding: utf-8 -*-
import os
import re
"""
codes analysis pkg_dir
called by py_sca.py
"""

"""
[dir_path]: pkg_dir with init_file to analysis module_name and module_version
[return]: module_name, module_version, module_path
called by pkgAnalysis
"""
def pkgfileAnalysis(dir_path):
    modules = {}
    # module_name
    module_name = dir_path.split('/')[-1]
    # print(module_name)
    module_path = dir_path
    module_info = []
    # module_version in __init__.py or version.py
    files = os.listdir(dir_path)
    for file in files:
        if file == '__init__.py' or file == 'version.py':
            file_path = os.path.join(dir_path, file)
            # rematch __version__ = "module_version"
            with open(file_path, 'r', encoding = 'UTF-8') as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if re.match(r'__version__.*=.*".*".*', line):
                        slices = line.split('"')
                        module_version = slices[1].strip()
                        module_info.append(module_version)
                        module_info.append(module_path)
                        modules[module_name] = module_info
                        return modules
                    if re.match(r"__version__.*=.*'.*'.*", line):
                        slices = line.split("'")
                        module_version = slices[1].strip()
                        module_info.append(module_version)
                        module_info.append(module_path)
                        modules[module_name] = module_info
                        return modules
            return None
                    
"""
[dir_path]: pkg_dir to do analysis module_info
[return]: pkg_dir_path to analysis
called by pkgAnalysis
"""
def pkgfileFetch(dir_path):
    pkg_dir_list = []
    for filepath, dirnames, filenames in os.walk(dir_path):
        for name in filenames:
            # remove files hidden
            if name.startswith('.'):
                continue
            # fetch dir with __init__.py file
            if name == '__init__.py':
                pkg_dir_list.append(filepath)
    return pkg_dir_list

"""
[dir_path]: pkg_dir to do module analysis
[return]: modules and module_version, module_path in pkgs
"""
def pkgAnalysis(dir_path):
    module_version_path_dir = {}
    # fetch py_pkg_path in dir_path
    py_pkg_path = pkgfileFetch(dir_path)
    # analysis modules connected with version and path
    for pkg in py_pkg_path:
        module_info = pkgfileAnalysis(pkg)
        if module_info is not None:
            module_version_path_dir.update(module_info)
    return module_version_path_dir

"""
test for srcAnalysis()
"""
def main():
    modules = pkgAnalysis("E:/Anaconda3/envs/pytorch/Lib/site-packages/")
    for module_name, module_info in modules.items():
        print(module_name, module_info)
    
if __name__ == '__main__':
    main()