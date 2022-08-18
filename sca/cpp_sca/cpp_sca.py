# -*- coding: utf-8 -*-
import file_filter
import cmake_extract
import vuln_check
# import time
import os
import sys
import pymysql
import time
"""
codes analysis C/C++ project and return values
"""

"""
[proj_path]: project to analysis
[return]: vuln_info
"""
def cppSca(proj_path: str):
    # filter cmake file
    file_list = file_filter.cmakeFilter(proj_path)
    # extract component_list
    component_list = []
    for file in file_list:
        component_info = cmake_extract.prodVersExtract(file)
        if component_info:
            component_list.extend(component_info)
    # check vulns
    database_list = []
    for filepath, dirnames, filenames in os.walk('/home/seed/sca/cpp_sca/vuln_data/'):
        for name in filenames:
            if name.endswith(tuple('.json')):
                database_list.append(os.path.join(filepath, name))
    vuln_list = []
    for database in database_list:
        # print(database)
        vuln_list.extend(vuln_check.vulnCheck(database, component_list))
    return vuln_list

"""
test for cpp_sca
"""
def main():
    dir_to_scan = sys.argv[2]
    project_name = sys.argv[1]
    vulns = cppSca(dir_to_scan)
    #for vuln in vulns:
       # print("------------------------")
        #for key, value in vuln.items():
            #print(f'[{key}]: {value}\n')
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
    sql = "INSERT INTO Projects values('" + project_name + "','C/C++'," + str(vuln_num) +",'" + date +"');" 
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