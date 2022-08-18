# -*- coding: utf-8 -*-
#import src_analysis
import lib_analysis
import vuln_check
import re
from library_list import known_lib_list
import time
import sys
import pymysql
"""
codes analysis java_src_lib and return vulns
"""

"""
[lib_module]: module_info from lib_analysis
[known_lib_list]: known usual used libraries list
[return]: module called by lib_info
"""
def moduleFetch(lib_module: list, known_lib_list: list):
    module_to_check = []
    # traverse lib
    for module in lib_module:
        for name2 in known_lib_list: 
            if re.match(module[0],name2,re.I) != None:
                module_to_check.append(module)
            
    return module_to_check

"""
[prog_dir]: dir of prog with src and pkg
[return]: module with vuln 
"""
def javaSca(prog_dir):
    print("checking...")
    # fetch lib_module
    lib_dir = prog_dir #+'lib/'
    lib_module = lib_analysis.libAnalysis(lib_dir)
    # filter module_to_check and extract component_list
    component_list = moduleFetch(lib_module, known_lib_list)
    
    #return component_list
    
    # check for vuln
    module_vuln_list = vuln_check.vulnCheck('/home/seed/sca/java_sca/vuln_data/nvdcve_2020.json', component_list)
    return module_vuln_list

    #return module_to_check
    
"""
test for java_sca
"""
def main():
    dir_to_scan = sys.argv[2]
    project_name = sys.argv[1]
    vulns = javaSca(dir_to_scan)
    # for vuln in vulns:
      #  print("--------------------------")
       # for key, value in vuln.items():
        #    print(f"[{key}]: {value}\n")
    # connect to mysql
    connect = pymysql.connect(host='127.0.0.1',user='root',password='password',db='supplychain',charset='utf8')
    cur = connect.cursor()
    # delete old data
    sql = "DELETE FROM Projects where proj_name='" + project_name +"';"
    cur.execute(sql)
    connect.commit()
    sql = "DELETE FROM Vulns where proj_name='" + project_name +"';"
    cur.execute(sql)
    connect.commit()
    # update new data to Projects
    vuln_num = len(vulns)
    now = time.localtime()
    date = time.strftime("%Y-%m-%d %H:%M:%S", now)
    sql = "INSERT INTO Projects values('" + project_name + "','JAVA'," + str(vuln_num) +",'" + date +"');" 
    cur.execute(sql)
    connect.commit()
    # update new data to Vulns
    if vulns:
        for vuln in vulns:
            sql = "INSERT INTO Vulns VALUES (%s,%s,%s,%s,%s,%s,%s);"
            cur.execute(sql,[project_name,vuln['name'],vuln['version'],vuln['src_path'].replace("/var/www/project/",''),vuln['cve_id'],vuln['description'],vuln['affect_version']])
            #sql = "INSERT INTO Vulns VALUES('" + project_name + "','" + vuln['module_name'] + "','" + vuln['module_version'] + "','" + vuln['module_path'].replace("/var/www/project/",'') + "','" + vuln['cve_id'] + "','" + vuln['description'] + "','" + vuln['affect_version'] +"');"
            #cur.execute(sql)
            connect.commit()
    cur.close()
    connect.close()
if __name__ == '__main__':
    main()