# -*- coding: utf-8 -*-
import re
"""
codes extract [vendor, product, version] info of third-party
called by cpp_sca.py
"""

"""
define regex patterns
IgnoreCase
DOTALL
MULTILINE
"""
# regex to obtain the project version
project_version_regex = re.compile(r'^\s*set\s*\(\s*VERSION\s*"([^"]*)"\)',
                             re.I | re.M | re.S)
# regex to obtain variables
# group(1) var
# group(2) value
set_var_regex = re.compile(r'^\s*set\s*\(\s*([\-a-zA-Z0-9_]*)\s+"?([\-a-zA-Z0-9_\.\$\{\}]*)"?\s*\)*',
                           re.I | re.M | re.S)
# regex to find inlined variables to replace them
# group(1) var 
# group(2) var without ${} --- connected with set_var_regex--group(1)
inl_var_regex = re.compile(r'(\$\s*\{([^\}]*)\s*\})',
                           re.I | re.M | re.S)
# regex to extract product information
project = re.compile(r'^ *project *\([ \n]*(\w+)[ \n]*.*?\)',
                     re.I | re.M | re.S)
# regex to extract product and version information
# group(1) product
# group(2) version
set_version = re.compile(r'^\s*set\s*\(\s*(\w+)_version\s+"?(\d+[^"\)]+)\s*"?\)',
                        re.I | re.M | re.S)

"""
[file_path]: file to get variables
[return]: a table map var_value to var_name
"""
def getVariables(file_path: str):
    var_val_table = {}
    with open(file_path, 'r', encoding = 'UTF-8') as f:
        lines = f.readlines()
        for line in lines:
            # match variables: var in group(1) and val in group(2)
            matcher = set_var_regex.search(line)
            # variable matched
            if matcher is not None:
                var_val_table[matcher.group(1)] = matcher.group(2)
    return var_val_table

"""
[file_path]: file to do component analysis
[return]: component_info [file_path, file_path]
"""
def prodVersExtract(file_path: str):
    # save prod_info
    prod_info_list = []
    # get var_val_table
    var_val_table = getVariables(file_path)
    # to_save project_name_version
    # only one in certain cmakefile
    no_proj_name = 1
    no_proj_vers = 1
    project_name = ''
    project_version = ''
    # analysis product and version
    with open(file_path, 'r', encoding = 'UTF-8') as f:
        lines = f.readlines()
        for line in lines:
            line_r = line
            # -----------------------------------------------------
            # step1--map variables
            # -----------------------------------------------------
            var_matcher = inl_var_regex.search(line_r)
            # inline_var_matched
            map_time = 0
            while var_matcher is not None:
                replaced = 0
                var_name = var_matcher.group(2)
                # check in var_val_table for map
                if var_name in var_val_table:
                    var_value = var_val_table[var_name]
                    if var_value != var_matcher.group(1):
                        line_r = re.sub(var_matcher.group(1), var_value, line_r)
                        replaced = 1
                        map_time += 1
                if not replaced:
                    break
                if map_time > 3:
                    break
                # considering multiple assignment for variables
                var_matcher = inl_var_regex.search(line_r)
            # print(line_r)
            # -----------------------------------------------------
            # step2--extract project and version
            # -----------------------------------------------------
            if no_proj_name:
                # match proj_name for cmakefile
                proj_name_matcher = project.search(line_r)
                if proj_name_matcher is not None:
                    project_name = proj_name_matcher.group(1)
                    no_proj_name = 0
            if no_proj_vers:
                # match proj_version for cmakefile
                proj_vers_matcher = project_version_regex.search(line_r)
                if proj_vers_matcher is not None:
                    project_version = proj_vers_matcher.group(1)
                    no_proj_vers = 0
            # -----------------------------------------------------
            # step3--extract product and version
            # -----------------------------------------------------
            prod_vers_matcher = set_version.search(line_r)
            if prod_vers_matcher is not None:
                # get product and version raw data
                product = prod_vers_matcher.group(1)
                version = prod_vers_matcher.group(2)
                # preprocess product
                if product.startswith("ALIASOF_"):
                    product = product.replace("ALIASOF_", "")
                if product.startswith("_"):
                    product = product[1:]
                if product.endswith("lib"):
                    product = "lib" + product[:-3]
                # save product_info to prod_info
                product_info = [product, product, version, file_path, "prod_version"]
                prod_info_list.append(product_info)
    if not no_proj_name:
        if not no_proj_vers:
            # save project_info
            product_info = [project_name, project_name, project_version, file_path, "proj"]
            prod_info_list.append(product_info)
    return prod_info_list

"""
test for prodVersExtract()
"""
def main():
    prod_info_list = prodVersExtract('./test_prog/3rdparty/ffmpeg/ffmpeg_version.cmake')
    for prod_info in prod_info_list:
        print(prod_info)
        
if __name__ == '__main__':
    main()