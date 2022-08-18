# -*- coding: utf-8 -*-
import json
import os
from packaging.specifiers import SpecifierSet
"""
codes check module_vuln with vuln_data
called by py_sca.py
"""

"""
[vuln_data_dir]: path of py_vuln_data(spec).json
[return]: vuln_data
"""
def vulnFetch(vuln_data_dir):
    if os.path.exists(vuln_data_dir):
        with open(vuln_data_dir) as f:
            # fetch vuln_data in dict format
            vuln_data = json.loads(f.read())
            return vuln_data
    
"""
[pkg]: pkg_name
[spec]: affect_version
[db]: vuln_data
[return]: vuln_pkg_data
"""
def get_vulnerabilities(pkg, spec, db):
    for entry in db[pkg]:
        for entry_spec in entry["specs"]:
            if entry_spec == spec:
                yield entry

"""
[vuln_data_dir]: vuln_data
[module_to_check]: modules_to_check
[return]: module_with_vuln
"""
def vulnCheck(vuln_data_dir, module_to_check):
    vuln_module_list = []
    # full_data
    vuln_data = vulnFetch(vuln_data_dir)
    # print(vuln_data)
    # only_specs
    vuln_specs = vulnFetch("/home/seed/sca/py_sca/vuln_data/py_vuln_spec.json")
    vuln_pkgs = frozenset(vuln_specs.keys())
    for module_name, module_info in module_to_check.items():
        # fetch module_version and module_name
        module_version = module_info[0]
        # name should be preprocessed
        name = module_name.replace("_", "-").lower()
        if name in vuln_pkgs:
            for specifier in vuln_specs[name]:
            # check version
                spec_set = SpecifierSet(specifiers = specifier)
                if spec_set.contains(module_version):
                # vuln exists in module
                    for data in get_vulnerabilities(name, specifier, vuln_data):
                        vuln_module = {}
                        # save name, version, path
                        vuln_module["module_name"] = module_name
                        vuln_module["module_version"] = module_version
                        vuln_module["module_path"] = module_info[1]
                        vuln_module["src_path"] = module_info[2]
                        # save vuln info
                        cve_id = data.get("cve")
                        vuln_module["cve_id"] = cve_id
                        vuln_module["description"] = data.get("advisory")
                        vuln_module["affect_version"] = specifier
                        vuln_module_list.append(vuln_module)
    return vuln_module_list