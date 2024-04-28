# 试一试多进程能快一点吗
# 确实能快一点
import math
import os.path

from tqdm import tqdm
from utility.Graph import Graph
from utility.DataReader import *
from multiprocessing import Pool
from multiprocessing import cpu_count
from utility.parser import arg_parse

parser = arg_parse()


def compute_one_train_sim(one_train_param):
    train_key = one_train_param[0]
    train_project = one_train_param[1]
    test_libs = one_train_param[2]['test_libs']
    train_dataset = one_train_param[2]['train_dataset']
    combined_dictionary = one_train_param[2]['combined_dictionary']
    lib_weight = one_train_param[2]['lib_weight']

    train_libs = get_libraries('%s/%s/dict__%s.txt' % (train_dataset, parser.dict_path, train_project))
    train_libs = train_libs | test_libs

    lib_set = []
    for lib in train_libs:
        lib_set.append(lib)
    size = len(lib_set)
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

        # 计算cos相似度
    scalar, norm1, norm2 = 0., 0., 0.
    length = len(vector1)
    for i in range(length):
        scalar += (vector1[i] * vector2[i])
        norm1 += (vector1[i] * vector1[i])
        norm2 += (vector2[i] * vector2[i])
    if norm1 * norm2 == 0:
        val = 0
    else:
        val = scalar / math.sqrt(norm1 * norm2)
    return train_key, val


def cos_similarity(train_dataset):
    train_projects = read_train_project(file_name=train_dataset + '/train_info.json')  # key: str, val: str
    test_projects = read_test_project(file_name=train_dataset + '/test_info.json')  # key: str, val: str

    train_keys = train_projects.keys()  # set<str>
    test_keys = test_projects.keys()  # set<str>

    all_train_libs = set()

    graph = Graph()

    train_graph_prog_bar = tqdm(desc='generating train call graph',
                                leave=True,
                                total=len(train_keys))

    for train_key in train_keys:
        train_project = train_projects[train_key]
        train_graph_file_name = 'graph__' + train_project + '.txt'
        train_dict_file_name = 'dict__' + train_project + '.txt'

        train_libs = get_libraries(train_dataset + '/' + parser.dict_path + '/' + train_dict_file_name)
        all_train_libs = all_train_libs | train_libs

        train_dictionary = get_dictionary(
            train_dataset + '/' + parser.dict_path + '/' + train_dict_file_name)  # train_dictionary: key:int, val:str

        train_graph = Graph(train_graph_file_name=train_dataset + '/' + parser.graph_path + '/' + train_graph_file_name,
                            train_dictionary=train_dictionary)

        graph.combine(train_graph, train_dictionary)
        train_graph_prog_bar.update()
    train_graph_prog_bar.close()
    print('train call graph generated finish')

    lib_weight = dict()

    sim_prog_bar = tqdm(desc='similarity computation progress',
                        leave=True,
                        total=len(test_keys))
    for test_key in test_keys:  # test_key: str

        # 这里的test_key是test_info中的，是所有的test，但是由于讨论len(tpl_list)为0的情况，没有创建len(tpl_list) == 0的dict文件，所以在这里会报错
        # 判断一下
        # 这种情况就是当len(tpl_list) == 0的情况时，不计算相似度
        if not os.path.exists(train_dataset + '/' + parser.dict_path + '/dict__' + test_projects[test_key] + '.txt'):
            continue

        all_libs = set()
        all_libs = all_libs | all_train_libs
        combined_graph = Graph(graph=graph)

        test_pro = test_projects[test_key]
        dict_test_pro_file_name = 'dict__' + test_pro + '.txt'
        graph_test_pro_file_name = 'graph__' + test_pro + '.txt'

        # test_libs-> 剩下的lib，就是dict中所有的library
        test_libs = get_train_libraries(train_dataset + '/' + parser.dict_path + '/' + dict_test_pro_file_name)

        all_libs = all_libs | test_libs

        # ************************************************************************
        # 这里将移除的lib放到recommendation文件夹中，所以需要拿到移除的lib_id
        test_dictionary = extract_train_dictionary(dict_test_pro_file_name,
                                                   test_key,
                                                   parser,
                                                   train_dataset)  # test_dictionary: key:int val:str
        # *************************************************************************

        test_graph = Graph(
            train_graph_file_name=train_dataset + '/' + parser.graph_path + '/' + graph_test_pro_file_name,
            train_dictionary=test_dictionary)

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
                lib_weight[end_node] = freq  # lib_weight: key: int, val: double

        # 在图中所有的项目的project
        num_project = len(graph_key_set)
        for lib_id in lib_weight.keys():
            freq = lib_weight[lib_id]
            weight = num_project / freq
            idf = math.log(weight)
            lib_weight[lib_id] = idf

        param_dict = {'test_libs': test_libs, 'train_dataset': train_dataset,
                      'combined_dictionary': combined_dictionary, 'lib_weight': lib_weight}
        multi_input = [(key, val, param_dict) for key, val in train_projects.items()]
        pool = Pool(int(cpu_count() // 2.0))

        sim_list = pool.map(compute_one_train_sim, multi_input)
        pool.close()
        pool.join()

        sorted_sim = sorted(sim_list, key=lambda d: d[1], reverse=True)
        with open(file=train_dataset + '/' + parser.similarities_path + '/' + test_pro + '.txt', mode='w') as fp:
            for key, val in sorted_sim:
                content = test_pro + '\t' + train_projects[key] + '\t' + str(val) + '\n'
                fp.write(content)
        sim_prog_bar.update()

    sim_prog_bar.close()
    print('similarity calculation finish')
