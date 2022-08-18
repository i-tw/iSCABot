# -*- coding: utf-8 -*-
import os
import json
from packaging.specifiers import SpecifierSet
"""
codes check vulns according to component info[vendor, product, version]
called by java_sca.py
"""

"""
[vuln_data_dir]: path of java_vuln_data(spec).json
[return]: vuln_data
"""
def vulnFetch(vuln_data_dir):
    if os.path.exists(vuln_data_dir):
        with open(vuln_data_dir, 'r', encoding = 'utf-8') as f:
            # fetch vuln_data in dict format
            vuln_data = json.loads(f.read())
            return vuln_data["CVE_Items"]
        
"""
[vuln_data_dir]: vuln_data
[component_info_list]: component to check for vulns
[return]: vuln_info
"""
def vulnCheck(vuln_data_dir: str, component_list: list):
    vuln_comp_list = []
    # fetch vuln_data from dir
    cve_datas = vulnFetch(vuln_data_dir)
    # check for cve_vuln
    for component_info in component_list:
        # get vendor, product, version, path
        vendor = component_info[0]
        product = component_info[1]
        version = component_info[2]
        path = component_info[3]
        for cve_info in cve_datas:
            # efficiency
            # scan_pause = 0
            # get cpe_match evidence
            cpe_nodes = cve_info["configurations"]["nodes"]
            for cpe_node in cpe_nodes:
                cpe_matches = cpe_node["cpe_match"]
                for cpe_match in cpe_matches:
                    # split for vendor and product
                    cpe_info = cpe_match["cpe23Uri"]
                    cpe_info_details = cpe_info.split(":")
                    cpe_vendor = cpe_info_details[3]
                    cpe_product = cpe_info_details[4]
                    # check for vendor, product
                    if cpe_vendor == vendor or cpe_product == product:
                        # check for version
                        version_key_lower = "versionStartIncluding"
                        version_key_higher = "versionEndExcluding"
                        if version_key_lower in cpe_match:
                            cpe_version_lower = cpe_match["versionStartIncluding"]
                            if version_key_higher in cpe_match:
                                cpe_version_higher = cpe_match["versionEndExcluding"]
                                version_specifier = ">=" + cpe_version_lower + ",<" + cpe_version_higher
                            else:
                                version_specifier = ">=" + cpe_version_lower
                        else:
                            if version_key_higher in cpe_match:
                                cpe_version_higher = cpe_match["versionEndExcluding"]
                                version_specifier = "<" + cpe_version_higher
                            else:
                                continue
                        spec_set = SpecifierSet(specifiers = version_specifier)
                        if spec_set.contains(version):
                            vuln_comp_info = {}
                            # version matched, extract vuln_info
                            cve_id = cve_info["cve"]["CVE_data_meta"]["ID"]
                            description = cve_info["cve"]["description"]["description_data"][0]["value"]
                            affect_version = version_specifier
                            # save for later use
                            vuln_comp_info["name"] = product
                            vuln_comp_info["version"] = version
                            vuln_comp_info["module_path"] = ""
                            vuln_comp_info["src_path"] = path
                            vuln_comp_info["cve_id"] = cve_id
                            vuln_comp_info["description"] = description
                            vuln_comp_info["affect_version"] = affect_version
                            vuln_comp_list.append(vuln_comp_info)
    return vuln_comp_list

"""
test for vulnCheck()
"""
def main():
    component_list = [["junit", "junit", "4.7.1", "./test_prog/lib"]]
    vuln_list = vulnCheck("./vuln_data/nvdcve_2020.json", component_list)
    for vuln in vuln_list:
        print("------------------------")
        for key, value in vuln.items():
            print(f'{key}: {value}\n')
            
if __name__ == '__main__':
    main()