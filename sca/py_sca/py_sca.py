# -*- coding: utf-8 -*-
import src_analysis
import pkg_analysis
import vuln_check
import sys
import pymysql
import time
"""
codes analysis py_src_pkg and return vulns
"""

"""
[pkg_module]: module_info from pkg_analysis
[src_module]: module_info from src_analysis
[return]: module called by src and pkg_info
"""
def moduleFetch(pkg_module: dict, src_module: dict):
    module_to_check = {}
    # traverse src and pkg
    for name1, info1 in src_module.items():
        for name2, info2 in pkg_module.items():
            if name1 == name2:
                # concat module_info
                info2.append(info1[0])
                module_to_check[name1] = info2
                break
    return module_to_check

"""
[prog_dir]: dir of prog with src and pkg
[return]: module with vuln 
"""
def pySca(prog_dir):
    print("checking...")
    # fetch src_module
    src_dir = prog_dir + "/src/"
    src_module = src_analysis.srcAnalysis(src_dir)
    # fetch pkg_module
    pkg_dir = prog_dir + "/pkg/"
    pkg_module = pkg_analysis.pkgAnalysis(pkg_dir)
    # filter module_to_check
    module_to_check = moduleFetch(pkg_module, src_module)
    # check for vuln
    module_vuln_list = vuln_check.vulnCheck("/home/seed/sca/py_sca/vuln_data/py_vuln_data.json", module_to_check)
    return module_vuln_list
    
"""
test for py_sca
"""
def main():
    dir_to_scan = sys.argv[2]
    project_name = sys.argv[1]
    vulns = pySca(dir_to_scan)
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
    sql = "INSERT INTO Projects values('" + project_name + "','Python'," + str(vuln_num) +",'" + date +"');" 
    cur.execute(sql)
    connect.commit()
    # update new data to Vulns
    if vulns:
        for vuln in vulns:
            sql = "INSERT INTO Vulns VALUES (%s,%s,%s,%s,%s,%s,%s);"
            cur.execute(sql,[project_name,vuln['module_name'],vuln['module_version'],vuln['module_path'].replace("/var/www/project/",''),vuln['cve_id'],vuln['description'],vuln['affect_version']])
            #sql = "INSERT INTO Vulns VALUES('" + project_name + "','" + vuln['module_name'] + "','" + vuln['module_version'] + "','" + vuln['module_path'].replace("/var/www/project/",'') + "','" + vuln['cve_id'] + "','" + vuln['description'] + "','" + vuln['affect_version'] +"');"
            #cur.execute(sql)
            connect.commit()
    cur.close()
    connect.close()
    
if __name__ == '__main__':
    main()