import xml.etree.ElementTree as ET
import os
from mylog import llog

def mxmlparser(target_path:str, log_fp):
    info = {}
    try:
        mytree =  ET.parse(os.path.join(target_path, "conf.xml"))
    except:
        llog(log_fp, "[Error] Open conf.xml failed\n")
        return None
    
    root_n = mytree.getroot()
    if(root_n.tag != "configure"):
        llog(log_fp, """[Error] conf.xml: the root element's tag must be "configure"\n""")
        return None
    
    base_n = root_n.find("basic")
    if(base_n is None):
        llog(log_fp, """[Error] conf.xml: cannot find basic configure\n""")
        return None

    try:
        info["name"] = base_n.find("name").text
    except:
        info["name"] = ""
        llog(log_fp, """[Warning] conf.xml: cannot find project name\n""")
    try:
        info["version"] = base_n.find("version").text
    except:
        info["version"] = ""
        llog(log_fp, """[Warning] conf.xml: cannot find project version\n""")

    project_n = root_n.find("project")
    if(project_n is None):
        llog(log_fp, """[Error] conf.xml: cannot find project configure\n""")
        return None
    
    src_n = project_n.find("source")
    info["source"] = []
    if(src_n is None):
        pass
    else:
        for item in src_n.findall("dir"):
            info["source"].append(item.text)

    if (info["source"] == []):
        llog(log_fp, f'''[Warning] No source dir\n''')
    
    inc_n = project_n.find("include")
    info["include"] = []
    if(inc_n is None):
        pass
    else:
        for item in inc_n.findall("dir"):
            info["include"].append(item.text)

    if (info["include"] == []):
        llog(log_fp, f'''[Warning] No include dir\n''')

    bin_n = project_n.find("binary")
    info["binary"] = []
    if(bin_n is None):
        pass
    else:
        for item in bin_n.findall("dir"):
            info["binary"].append(item.text)

    if (info["binary"] == []):
        llog(log_fp, f'''[Warning] No binary dir\n''')

    return info

def mxmlparser_get_basic(target_path:str, log_fp):
    info = {}
    try:
        mytree =  ET.parse(os.path.join(target_path, "conf.xml"))
    except:
        llog(log_fp, "[Error] Open conf.xml failed\n")
        return None
    
    root_n = mytree.getroot()
    if(root_n.tag != "configure"):
        llog(log_fp, """[Error] conf.xml: the root element's tag must be "configure"\n""")
        return None
    
    base_n = root_n.find("basic")
    if(base_n is None):
        llog(log_fp, """[Error] conf.xml: cannot find basic configure\n""")
        return None

    try:
        info["name"] = base_n.find("name").text
    except:
        info["name"] = ""
        llog(log_fp, """[Warning] conf.xml: cannot find project name\n""")
    try:
        info["version"] = base_n.find("version").text
    except:
        info["version"] = ""
        llog(log_fp, """[Warning] conf.xml: cannot find project version\n""")

    return info


if __name__ == '__main__':
    target_path = "./source_data"
    log_path = "./mxmlparser.log"
    log_fp = open(log_path, "w")
    print(mxmlparser(target_path, log_fp))
    log_fp.close()
