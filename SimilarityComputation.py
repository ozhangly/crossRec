import math

from tqdm import tqdm
from utility.Graph import Graph
from utility.DataReader import *
from utility.parser import arg_parse


def cos_similarity():
    parser = arg_parse()
    train_projects = read_train_project(file_name='metadata/config/train_info.json') # key: str, val: str
    test_projects  = read_test_project(file_name='metadata/config/test_info.json') # key: str, val: str

    train_keys = train_projects.keys()   # set<str>
    test_keys = test_projects.keys()     # set<str>

    all_train_libs = set()

    graph = Graph()

    print('构造train_graph 进度条:', end='')
    for train_key in tqdm(train_keys):
        train_project = train_projects[train_key]
        train_graph_file_name = 'graph__' + train_project + '.txt'
        train_dict_file_name  = 'dict__' + train_project + '.txt'

        train_libs = get_libraries(parser.dict_path + train_dict_file_name)
        all_train_libs = all_train_libs | train_libs

        train_dictionary = get_dictionary(parser.dict_path + train_dict_file_name) # train_dictionary: key:int, val:str

        train_graph = Graph(train_graph_file_name=parser.graph_path + train_graph_file_name, train_dictionary=train_dictionary)

        graph.combine(train_graph, train_dictionary)

    lib_weight = dict()

    print('test计算相似度进度', end='')
    for test_key in tqdm(test_keys):          # test_key: str
        all_libs = set()
        all_libs = all_libs | all_train_libs
        combined_graph = Graph(graph=graph)
        sim = dict()            # sim: key: int, val: double

        test_pro = test_projects[test_key]
        dict_test_pro_file_name = 'dict__' + test_pro + '.txt'
        graph_test_pro_file_name = 'graph__' + test_pro + '.txt'
        # 拿第test_pro的一半的lib
        test_libs = get_half_libraries(parser.dict_path + dict_test_pro_file_name)

        all_libs = all_libs | test_libs
        
        test_dictionary = extract_half_dictionary(dict_test_pro_file_name, parser.ground_truth_path, parser)    # test_dictionary: key:int val:str

        test_graph = Graph(train_graph_file_name=parser.graph_path + graph_test_pro_file_name, train_dictionary=test_dictionary)
        combined_graph.combine(test_graph, test_dictionary)
        combined_dictionary = combined_graph.get_dictionary()

        graph_edges = combined_graph.getoutlinks()

        graph_key_set = graph_edges.keys()  # graph_key_set: set<int>

        for start_node in graph_key_set:
            out_links = graph_edges[start_node]
            for end_node in out_links:
                if end_node in lib_weight.keys():
                    freq = lib_weight[end_node] + 1.0
                else:
                    freq = 1.0
                lib_weight[end_node] = freq         # lib_weight: key: int, val: double

        # 在图中所有的项目的project
        num_project = len(graph_key_set)
        for lib_id in lib_weight.keys():
            freq = lib_weight[lib_id]
            weight = num_project/freq
            idf = math.log(weight)
            lib_weight[lib_id] = idf

        for train_key in train_keys:
            train_project = train_projects[train_key]
            train_libs = get_libraries(parser.dict_path + 'dict__' + train_project + '.txt')
            # train_libs.union(test_libs)
            train_libs = train_libs | test_libs
            lib_set = []
            for lib in train_libs:
                lib_set.append(lib)
            size = len(train_libs)

            vector1 = []
            vector2 = []
            for i in range(size):
                lib = lib_set[i]
                if lib in test_libs:
                    lib_id = combined_dictionary[lib]
                    vector1.append(lib_weight[lib_id])
                else:
                    vector1.append(0.0)
                if lib in train_libs:
                    lib_id = combined_dictionary[lib]
                    vector2.append(lib_weight[lib_id])
                else:
                    vector2.append(0.0)
            val = compute_cos_similarity(vector1, vector2)
            sim[train_key] = val

        sorted_sim = sorted(sim.items(), key=lambda d: d[1], reverse=True)
        with open(file=parser.similarities_path + test_pro + '.txt', mode='w') as fp:
            for key, val in sorted_sim:
                content = test_pro + '\t' + train_projects[key] + '\t' + str(val) + '\n'
                fp.write(content)


def compute_cos_similarity(vector1, vector2):
    scalar, norm1, norm2 = 0., 0., 0.
    length = len(vector1)
    for i in range(length):
        scalar += (vector1[i] * vector2[i])
        norm1 += (vector1[i] * vector1[i])
        norm2 += (vector2[i] * vector2[i])

    return scalar/math.sqrt(norm1*norm2)


if __name__ == '__main__':
    cos_similarity()
