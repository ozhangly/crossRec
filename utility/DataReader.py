import json
import os

from typing import Dict


def read_train_project(file_name):
    with open(file=file_name, mode='r') as fp:
        ret = json.load(fp)
    return ret          # ret: map对象


def read_test_project(file_name):
    with open(file=file_name, mode='r') as fp:
        ret = json.load(fp)
    return ret          # ret: map对象


def get_libraries(file_name):
    libraries = set()
    with open(file=file_name, mode='r') as fp:
        for line in fp.readlines():
            vals = line.strip('\n').split('\t')
            if vals[1].find('#DEP#') != -1:
                libraries.add(vals[1])
    return libraries        # set 字符串对象


def get_dictionary(file_name):
    ret = {}
    with open(file=file_name, mode='r') as fp:
        for line in fp.readlines():
            line = line.strip('\n').split('\t')
            id = int(line[0])
            vals = line[1]
            if id == 1 or vals.find('#DEP#') != -1:
                ret[id] = vals

    return ret            # ret: map对象<int, string>


# 用来拿到训练的lib, dict中所有lib都是用来训练的lib
# 直接返回所有的set就完事
def get_train_libraries(file_name):
    ret = set()
    with open(file=file_name, mode='r') as fp:
        for line in fp.readlines():
            pair = line.strip('\n').split('\t')
            name = pair[1]
            if name.find('#DEP#') != -1:
                ret.add(name)
    return ret


# 提取train的lib，将remove的lib写入到ground_truth中
def extract_train_dictionary(file_name, test_key, args, train_dataset, get_also_user=False) -> Dict:
    lib_cnt = 0
    ret = dict()
    with open(file='%s/%s/%s' % (train_dataset, args.dict_path, file_name), mode='r') as fp:
        for line in fp.readlines():
            pair = line.strip('\n').split('\t')
            id = int(pair[0])
            name = pair[1]
            if name.find('#DEP#') != -1:
                lib_cnt += 1
                ret[id] = name
            elif get_also_user or name.find('#DEP#') == -1:
                ret[id] = name
    # 将移除的
    test_apk_lib_info = get_test_apk_info(train_dataset)
    removed_tpl_list = test_apk_lib_info[int(test_key)]['removed_tpls']     # ground_truth

    # 还需要知道被移除的lib名字
    with open(file=args.config_path + '/lib_info.json', mode='r') as fp:
        lib_info = json.load(fp=fp)

    # 写ground_truth
    with open(file='%s/%s/%s' % (train_dataset, args.ground_truth_path, file_name), mode='w') as fp:
        for removed_tpl in removed_tpl_list:
            lib_cnt += 1
            write_s = '%d\t%s\n' % (lib_cnt, lib_info[str(removed_tpl)])
            fp.write(write_s)
    return ret

# 这里是用来提取ground_truth的，需要在设置一个remove_n参数
# def extract_half_dictionary(file_name, ground_truth_path, dict_path, get_also_user=False):
#     dictionary = dict()
#     ret = dict()
#
#     lib_count, half = 0, 0
#     with open(file=dict_path + '/' + file_name, mode='r') as fp:
#         for line in fp.readlines():
#             pair = line.strip('\n').split('\t')
#             id = int(pair[0])
#             name = pair[1]
#             dictionary[id] = name
#             if name.find('#DEP#') != -1:
#                 lib_count += 1
#     size = lib_count
#     half = round(size/2)
#     enough_lib = False
#     lib_count = 0
#
#     ground_truth_file_name = ground_truth_path + '/' + file_name
#
#     # 如果不存在再写这个ground_truth，否则的话直接跳过
#     with open(file=ground_truth_file_name, mode='w') as fp:
#         for test_key in dictionary.keys():
#             artifact = dictionary[test_key]  # dictionary: key:int, val:str
#             if lib_count == half:
#                 enough_lib = True
#             if artifact.find('#DEP#') != -1:
#                 if enough_lib is False:
#                     ret[test_key] = artifact
#                 else:
#                     fp.write(str(test_key) + '\t' + artifact + '\n')
#                 lib_count += 1
#             else:
#                 if get_also_user is True or artifact.find('#DEP#') == -1:
#                     ret[test_key] = artifact
#
#     return ret  # dict: key: int, val: str


def get_similarity_matrix(file_name, num_neighbours):
    sim = dict()
    count = 0
    with open(file=file_name, mode='r') as fp:
        for line in fp.readlines():
            pair = line.strip('\n').split('\t')
            val = float(pair[2])
            sim[count] = val
            count += 1
            if count == num_neighbours:
                break
    return sim


def get_most_similarity_projects(file_name, size):
    project = dict()
    count = 0
    with open(file=file_name, mode='r') as fp:
        for line in fp.readlines():
            pair = line.strip('\n').split('\t')
            name = pair[1]
            project[count] = name
            count += 1
            if count == size:
                break

    return project


def get_similarity_projects(train_dataset, file_name, args):
    libraries = set()
    project = dict()
    all_neighbours = dict()
    top_n = args.recommend_top_n

    cnt = 0
    sim_file_path = '%s/%s/%s.txt' % (train_dataset, args.similarities_path, file_name)
    with open(file=sim_file_path, mode='r') as fp:
        for line in fp.readlines():
            pair = line.strip('\n').split('\t')
            name = pair[1]
            project[cnt] = name
            lib = get_libraries('%s/%s/dict__%s.txt' % (train_dataset, args.dict_path, name))
            all_neighbours[cnt] = lib
            cnt += 1
            libraries = libraries | lib
            # 首先还是先拿到num of neighbours的project
            if cnt >= args.numofneighbours:
                # 防止libraries不够top_n的情况
                if len(libraries) >= top_n:
                    break

    return project, all_neighbours, libraries


def create_libname2id(config_path):
    id2lib_name = json.load(fp=open(file=config_path + '/lib_info.json', mode='r'))
    lib_name2id = dict()

    for id, name in id2lib_name.items():
        id = int(id)
        lib_name2id[name] = id

    return lib_name2id


def create_apk_name2id(training_dataset, dataset_name):
    test_path = training_dataset + '/' + dataset_name + '/test_info.json'
    id2apk_name = json.load(fp=open(file=test_path, mode='r'))
    apk_name2id = dict()

    for id, name in id2apk_name.items():
        id = int(id)
        apk_name2id[name] = id

    return apk_name2id


def get_test_apk_info(training_dataset):

    file_list = os.listdir(training_dataset)
    for file in file_list:
        if 'testing' in file:
            test_file_name = file
            break

    apk_info_list = {}
    with open(file=training_dataset + '/' + test_file_name, mode='r') as fp:
        for info in fp.readlines():
            val = {}
            obj = json.loads(info.strip('\n'))
            val['removed_tpls'] = obj['removed_tpl_list']
            val['tpl_list'] = obj['tpl_list']
            apk_info_list[obj['app_id']] = val
    return apk_info_list
