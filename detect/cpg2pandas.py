import os, copy, json, pyparsing, pickle
from shutil import ExecError
import pandas as pd
import re
import operator
from mylog import llog
import mxmlparser


class cpg2pandas:
    def __init__(self, log_fp):
        self.workpath = os.getcwd()
        self.tmppath = os.path.join(self.workpath, "tmp")
        self.log_fp = log_fp
        
        

        columns_list = [
            "index", "name", "version", 
            "funcname", "filename", "type",
            "funcid",
            "funccode", "beginline", "endline",
            "nodecode", "cpg", "tag", ]
        self.funcdata = pd.DataFrame(columns=columns_list)

    
    def set_target(self, targetpath:str):
        '''
        set self.targepath = targetpath

        Parameters:
            targetpath - absolute path of target project

        Returns:
            success:    0
            targetpath not exist:   -1
        '''
        if (not os.path.exists(targetpath)):
            return -1

        if(os.path.exists(self.tmppath)):
            llog(self.log_fp, f"""[Warning] [cpg2pandas] Tmp dir: {self.tmppath} existed, auto deleted\n""")
            if ( os.system(f"rm -rf {self.tmppath}")!=0):
                llog(self.log_fp, f"""[Error] [cpg2pandas] Tmp dir: {self.tmppath} delete failed\n""")
        if(not os.path.exists(self.tmppath)):
            os.mkdir(self.tmppath)

        if(os.path.exists(os.path.join(self.workpath,"workspace"))):
            llog(self.log_fp, f"""[Warning] [cpg2pandas] Workspace dir: {os.path.join(self.workpath,"workspace")} existed, auto deleted\n""")
            if ( os.system(f"""rm -rf {os.path.join(self.workpath,"workspace")}""")!=0):
                llog(self.log_fp, f"""[Error] [cpg2pandas] Workspace dir: {os.path.join(self.workpath,"workspace")} delete failed\n""")
            
        self.targetpath = targetpath
        return 0


     
    def joern_funcs(self):
        '''
        get all basic infomation of all function in self.targetpath(dir)
        clear and refill self.funcdata

        return:
            success:   self.funcdata
            error:  -1
        '''

        script = f"""
            @main def exec() = {{
                importCpg("{self.binpath}")
                cpg.method.toJsonPretty |> "{os.path.join(self.tmppath, "funcs.json")}"
                cpg.method.dotCpg14.toJsonPretty |> "{os.path.join(self.tmppath, "cpgs.json")}"
                cpg.all.toJsonPretty |> "{os.path.join(self.tmppath, "nodes.json")}"
            }}
        """


        with open(os.path.join(self.tmppath, "script.sc"),'w') as fp:
            fp.write(script)
            
        llog(self.log_fp, f"""[Info] [cpg2pandas] Start analyzing {self.binpath}\n""")
        command = f'''joern --script {os.path.join(self.tmppath, "script.sc")}'''
        if (os.system(command)!=0):
            llog(self.log_fp, f"""[Failed] [cpg2pandas] Analyzing {self.binpath} failed\n""")
            raise Exception()


        llog(self.log_fp, f"""[Info] [cpg2pandas] Start filling basic info for {self.binpath}\n""")
        func_list = []
        with open(os.path.join(self.tmppath, "funcs.json"), "r") as fp:
            func_list = json.load(fp)
        cur_datalen = len(self.funcdata)
        datalen = cur_datalen
        for func in func_list:
            if(func.get("_label") != "METHOD"):
                continue
            if(func.get("isExternal") != False):
                continue
            if(func.get("name") == "<global>"):
                continue
            if(func.get("name") == "__cxx_global_var_init"):
                continue
            if(len(re.findall("^(_GLOBAL__sub_I_).*(cpp)$", func.get("name"))) >= 1):
                continue

            filepath = func.get("filename")
            funcname = func.get("name")

            tag = 0

            self.funcdata.loc[datalen]  = {
                "funcname":func.get("name"),
                "filename":filepath,
                "funcid":func.get("id"),
                "cpg":"",
                "tag":tag
                }
            datalen += 1


        llog(self.log_fp, f"""[Info] [cpg2pandas] Start creating overall nodecode for {self.binpath}\n""")
        nodecode_dict = {}
        node_list = []
        with open(os.path.join(self.tmppath, "nodes.json"), "r") as fp:
            node_list = json.load(fp)
        for node in node_list:
            if (node.get("id") == None):
                llog(self.log_fp, f"""[Failed] [cpg2pandas] Start creating overall nodecode for {self.binpath} failed, some node with no id\n""")
                raise Exception()
            if (node.get("code" == None)):
                nodecode_dict[str(node.get("id"))] = ""
            else:
                nodecode_dict[str(node.get("id"))] = node.get("code")
        

        llog(self.log_fp, f"""[Info] [cpg2pandas] Start filling cpg info for {self.binpath}\n""")
        cpg_list = []
        with open(os.path.join(self.tmppath, "cpgs.json"), "r") as fp:
            cpg_list = json.load(fp)
        for cpg in cpg_list:
            check = "\""+pyparsing.Word("01234556789")+"\""+"[label"+"="+"\"(METHOD,"
            ans = check.search_string(cpg)
            if(len(ans) >= 1):
                self.funcdata.cpg[(self.funcdata.funcid == int(ans[0][1]))
                    & (self.funcdata.index>=cur_datalen)
                ] = cpg
            else:
                llog(self.log_fp, f"""[Warning] [cpg2pandas] {self.binpath}: method cpg with no root method\n""")

        llog(self.log_fp, f"""[Info] [cpg2pandas] Start filling codenode info for {self.binpath}\n""")
        check = "\""+pyparsing.Word("01234556789")+"\""+"[label"+"="+"\"("
        for i in range(cur_datalen, datalen):
            t = check.search_string(self.funcdata.loc[i,"cpg"])
            nowdict = {}
            if(len(t) == 0):
                self.funcdata.loc[i,"nodecode"] = json.dumps(nodecode_dict)
                # print(f"{i}")
                continue
            for item in t:
                nowdict[item[1]] = nodecode_dict.get(item[1])
            self.funcdata.loc[i,"nodecode"] = json.dumps(nowdict)    
        return self.funcdata



    def clear(self):
        if(os.path.exists(self.tmppath)):
            llog(self.log_fp, f"""[Info] [cpg2pandas] Delete tmp dir: {self.tmppath}\n""")
            if ( os.system(f"rm -rf {self.tmppath}")!=0):
                llog(self.log_fp, f"""[Error] [cpg2pandas] Tmp dir: {self.tmppath} delete failed\n""")
        

        if(os.path.exists(os.path.join(self.workpath,"workspace"))):
            llog(self.log_fp, f"""[Info] [cpg2pandas] Delete workspace dir: {os.path.join(self.workpath,"workspace")}\n""")
            if (os.system(f"""rm -rf {os.path.join(self.workpath,"workspace")}""")!=0):
                llog(self.log_fp, f"""[Error] [cpg2pandas] Workspace dir: {os.path.join(self.workpath,"workspace")} delete failed\n""")


        return 0

def gen_pkl(target_path, output_path, xml_path, log_fp):
    llog(log_fp, f"""[Info] Start turning cpg to pkl file\n""")
    llog(log_fp, f"""[Info] Target Path: {target_path}\n""")
    llog(log_fp, f"""[Info] Output Path: {output_path}\n""")

    if(os.path.isfile(target_path)):
        llog(log_fp, f"""[Error] Output Path: {target_path} is a file\n""")
        return

    if(not os.path.isdir(target_path)):
        llog(log_fp, f"""[Error] Target Path: {target_path} is not existed\n""")
        return

    if(os.path.isfile(output_path)):
        llog(log_fp, f"""[Error] Output Path: {output_path} is a file\n""")
        return

    if(os.path.isdir(output_path)):
        llog(log_fp, f"""[Warning] Output Path: {output_path} is already existed, auto deleted\n""")
        os.system(f"""rm -rf {output_path}""")

    llog(log_fp, f"""[Info] Create Output dir: {output_path}\n""")
    os.system(f"""mkdir {output_path}""")

    columns_list = [
            "index", "name", "version", 
            "funcname", "filename", "type",
            "funcid",
            "funccode", "beginline", "endline",
            "nodecode", "cpg", "tag", ]
    data = pd.DataFrame(columns=columns_list)

    for root, dirs, files in os.walk(target_path):
        for file in files:
            try:
                c2p = cpg2pandas(log_fp)
                target = os.path.join(root, file)
                c2p.set_target(target)
                c2p.binpath = (target)
                c2p.joern_funcs()
                
                if re.match(".*(\.bc\.bin\.zip)$", file) is not None:
                    c2p.funcdata["type"] = "binary"
                elif re.match(".*(\.ll\.bin\.zip)$", file) is not None:
                    c2p.funcdata["type"] = "source"

                # edit filename to file origin path
                origin_file = re.sub("(\.((bc)|(ll))\.bin\.zip)$", "", file)
                origin_path = os.path.join(xml_path, os.path.join(root.replace(target_path, "", 1).lstrip('/'), origin_file))
                c2p.funcdata["filename"] = origin_path

                data = data.append(c2p.funcdata, ignore_index=True)
                c2p.clear()
            except:
                llog(log_fp, f"""[Failed] [cpg2pandas] {target} failed\n""")
                pass
            llog(log_fp, f"""[Info] [cpg2pandas] {target} succeed\n""")
    
    name = "data.pkl"
    data["index"] = data.index

    basic_info = mxmlparser.mxmlparser_get_basic(xml_path, log_fp)
    data["version"] = basic_info["version"]
    data["name"] = basic_info["name"]

    with open(os.path.join(output_path, name), "wb") as ffp:
        pickle.dump(data, ffp)
            
if __name__ == '__main__':
    target_path = "./source_data_cpg"
    output_path = "./source_data_pandas"
    log_path = "./cpd2pandas.log"
    log_fp = open(log_path, "w")
    gen_pkl(target_path, output_path, log_fp)
    log_fp.close()
    
