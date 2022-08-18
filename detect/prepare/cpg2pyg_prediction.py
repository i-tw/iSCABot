import os
import re
import torch
from torch_geometric.data import Data
import torch_geometric
from .myparse import tokenizer
import pydot
import numpy as np
from gensim.models import Word2Vec
import pickle
import pandas as pd
import json

#PARM
w2v_path = "/home/seed/model_prediction/data/w2v/w2v.model"
dot_path = "/home/seed/try_data/output/"
input_dir_path = "/home/seed/model_prediction/input/"
input_file_name = "1_input.pickle"
num_node = 250

# columns_list = ["funcname", "filename", "func", "code", "cpg", "tag"]

node_labels = ["META_DATA", "FILE", "NAMESPACE", "METHOD", "METHOD_PARAMETER_IN", "METHOD_PARAMETER_OUT", "METHOD_RETURN", "MEMBER", "PARAM",
               "TYPE", "TYPE_ARGUMENT", "TYPE_DECL", "TYPE_PARAMETER", "AST_NODE", "BLOCK", "CALL",
               "CALL_REPR", "CONTROL_STRUCTURE", "EXPRESSION", "FIELD_IDENTIFIER", "IDENTIFIER", "JUMP_LABEL", "JUMP_TARGET","LITERAL","LOCAL", "METHOD_REF", "MODIFIER", "RETURN", "TYPE_REF", "UNKNOWN", "CFG_NODE", "COMMENT",
               "FINDING", "KEY_VALUE_PAIR", "LOCATION", "TAG", "TAG_NODE_PAIR", "CONFIG_FILE", "BINDING",
               "DECLARATION","NULL"]
# print(len(node_labels))

operators = ['addition', 'addressOf', 'and', 'arithmeticShiftRight', 'assignment',
             'assignmentAnd', 'assignmentArithmeticShiftRight', 'assignmentDivision',
             'assignmentMinus', 'assignmentMultiplication', 'assignmentOr', 'assignmentPlus',
             'assignmentShiftLeft', 'assignmentXor', 'cast', 'conditionalExpression',
             'division', 'equals', 'fieldAccess', 'greaterEqualsThan', 'greaterThan',
             'indirectFieldAccess', 'indirectIndexAccess', 'indirection', 'lessEqualsThan',
             'lessThan', 'logicalAnd', 'logicalNot', 'logicalOr', 'minus', 'modulo', 'multiplication',
             'not', 'notEquals', 'or', 'postDecrement', 'plus', 'postIncrement', 'preDecrement',
             'preIncrement', 'shiftLeft', 'sizeOf', 'subtraction']

node_labels += operators

node_labels = {label: i for i, label in enumerate(node_labels)}
print(node_labels)

# get the type of the node label
def get_type(label):
    node_type = node_labels.get(label)  # Label embedding

    if node_type is None:
        print("node", f"LABEL {label} not in labels!")
        node_type = len(node_labels) + 1
    
    type_arr = np.zeros(len(node_labels) + 2)
    type_arr[node_type] = 1
    return type_arr


# get the type vector according to loaded word2vec model
def get_vectors(w2v_keyed_vectors, tokenized_code, type):
    vectors = []

    for token in tokenized_code:
        if token in w2v_keyed_vectors.vocab:
            vectors.append(w2v_keyed_vectors[token])
        else:
            # print(node.type, token, node.get_code(), tokenized_code)
            vectors.append(np.zeros(w2v_keyed_vectors.vector_size))
            if type not in ["Identifier", "Literal", "MethodParameterIn", "MethodParameterOut"]:
                msg = f"No vector for TOKEN {token} in {type}."
                print('embeddings', msg)
    return vectors

# a single node representation
def emb_row(type: str, node_code: str, w2v_keyed_vectors):     
    if node_code:
        tokenized_code = tokenizer(node_code, True)
        if not tokenized_code:
            # print(f"Dropped node {node}: tokenized code is empty.")
            msg = f"Empty TOKENIZED from node CODE {node_code}"
            print('embeddings', msg)
        
        # Get each token's learned embedding vector
        vectorized_code = np.array(get_vectors(w2v_keyed_vectors, tokenized_code, type))
        # The node's source embedding is the average of it's embedded tokens
        if vectorized_code.any():
            source_embedding = np.mean(vectorized_code, 0)
        else:
            source_embedding = np.zeros(w2v_keyed_vectors.vector_size)
    else:
        source_embedding = np.zeros(w2v_keyed_vectors.vector_size)
    
    # The node representation is the concatenation of label and source embeddings
    embedding = np.concatenate((get_type(type), source_embedding), axis=0)
    # embeddings.append(embedding)
    return embedding


# generating a PyG dataset for each function input
def cpg2pyg_func(node_code: dict, all_dot_data: str, target: int):
    """
    # converge cpgs to pyg
    """
    # indextable cpg-node-index 2 pyg-node-index
    # node_feature
    # edge_index    
    pyg_node_index = 0
    node_index_table = {}
    node_feature_list = []
    edge_index_list = []
    
    # load the w2v model
    w2vmodel = Word2Vec.load(w2v_path)
    pattern = re.compile('(?<=\"\().*(?=\)\")')
      
    # reach dot data
    dot_data = pydot.dot_parser.parse_dot_data(all_dot_data)[0]
    # reach nodes data
    nodes_data = dot_data.get_nodes()
    for node in nodes_data:
        # get node_index, node_label
        cpg_node_index = node.get_name()
        
        node_label = node.get_label()
        node_label = pattern.findall(node_label)
        if node_label:
            node_label = node_label[0]
        else:
            node_label = ''
        # if node_feature has been saved, quit
        if cpg_node_index in node_index_table:
            continue
        # else process node_feature into vec and save
        node_index_table[cpg_node_index] = pyg_node_index
        # print(node_label)
        label = node_label.split(',',1)  #seperate type & value
        
        # Define type and label
        type = label[0]
        if ("<operator>" in type) or ("<operators>" in type):
            type = type.split(".")[-1]
        
        value = node_code.get(eval(cpg_node_index))
        
        # generate single node representation
        node_vec = emb_row(type, value, w2vmodel.wv)
        node_feature_list.append(node_vec)
        pyg_node_index += 1

    #reach edges data
    edges_data = dot_data.get_edges()
    for edge in edges_data:
        #get src and dst for certain edge and save in edge_index_list
        cpg_src = edge.get_source()
        cpg_dst = edge.get_destination()
        # print("src = "+ cpg_src + "dst = " + cpg_dst)
        src_to_dst = [node_index_table[cpg_src], node_index_table[cpg_dst]]
        edge_index_list.append(src_to_dst)
    
    # node_feature = torch.from_numpy(node_feature_list).float()
    node_feature = torch.tensor(node_feature_list).float()
    node_feature_compl = torch.zeros(num_node, w2vmodel.wv.vector_size + 2 + len(node_labels)).float()
    if node_feature.size(0) > num_node:
        node_feature_compl = torch.zeros(num_node, w2vmodel.wv.vector_size + len(node_labels)+2).float()
        node_feature_compl = node_feature[:num_node,:]
    else:
        node_feature_compl[:node_feature.size(0), :] = node_feature
    edge_index = torch.tensor(edge_index_list)
    label = torch.tensor([target])
    
    pyg_data = Data(x = node_feature_compl, edge_index = edge_index.t().contiguous(), y = label)
    # pyg_data.coalesce()
    return pyg_data

def cpg2pyg_return(dir_path: str):    
    with open(dir_path,"rb") as fp:
        cc = pickle.load(fp)
        
    cc["input"] = cc.apply(lambda row: cpg2pyg_func(json.loads(row.nodecode),row.cpg,row.tag), axis=1)  
    
    return cc[["input","tag", "index"]]

def cpg2pyg(dir_path: str):        
    pyg_data = cpg2pyg_return(dir_path)
    file_name = input_file_name
    with open(input_dir_path + file_name, 'wb') as handle:
        pickle.dump(pyg_data, handle)
    
    
def main():
    print("converting cpg to pyg...")
    files = os.listdir(dot_path)
    for file in files:
        pyg_data = cpg2pyg_return(dot_path + file)
        print(pyg_data)
        # i = file[:6]
        # saving input dataset
        file_name = input_file_name
        print(f"Saving input dataset {file_name}.")
        with open(input_dir_path + file_name, 'wb') as handle:
            pickle.dump(pyg_data, handle)



if __name__ == '__main__':
    main()