import os
import json

from tqdm import tqdm
from utility.parser import arg_parse

args = arg_parse()


def create_apk_info():
    if not os.path.exists('metadata/config'):
        os.mkdir('metadata/config')
    if not os.path.exists('metadata/config/apk_info.json'):
        apk_list = {}
        with open(file='metadata/apk_info.csv', mode='r') as apk_fp:
            for apk_info in apk_fp.readlines():
                apk_pair = apk_info.strip('\n').split(',')
                apk_id = int(apk_pair[0])
                dot_idx = apk_pair[1].strip('\n').rindex('.')
                apk_name = apk_pair[1][:dot_idx]
                apk_list[apk_id] = apk_name
        with open(file='metadata/config/apk_info.json', mode='w') as apk_fp:
            json.dump(apk_list, fp=apk_fp)


def create_lib_info():
    if not os.path.exists('metadata/config/lib_info.json'):
        lib_list = {}
        with open(file='metadata/lib_info.csv', mode='r') as lib_fp:
            for lib_info in lib_fp.readlines():
                lib_pair = lib_info.strip('\n').split(',')
                lib_id = int(lib_pair[0])
                lib_name = lib_pair[1]
                lib_list[lib_id] = lib_name
        with open(file='metadata/config/lib_info.json', mode='w') as lib_fp:
            json.dump(obj=lib_list, fp=lib_fp)


def get_apk_lib_info(train_dataset):
    # 需要创建一个dict，为apk和lib的调用关系
    apk_lib_info = {}
    test_apk_lib_info = {}
    # 先把test的写进去   , 这都什么逻辑啊啊啊啊啊
    for file in os.listdir(train_dataset):
        if 'testing' in file:
            test_file_name = file
        if 'CF' in file:
            train_file_name = file

    with open(file=train_dataset + '/' + test_file_name, mode='r') as fp:
        for line in fp.readlines():
            line = line.strip('\n')
            obj = json.loads(line)
            apk_id, libs = obj['app_id'], obj['tpl_list']
            test_apk_lib_info[apk_id] = libs
    # 这个需要重写
    with open(file=train_dataset + '/' + train_file_name, mode='r') as fp:
        for line in fp.readlines():
            line = line.strip('\n')
            app_id = int(line.split(',')[0])
            tpl_list = [int(tpl) for tpl in line.split(',')[1:]]
            apk_lib_info[app_id] = tpl_list

    # 到这结束，apk_lib_list中都是train的info，还需要再把test_dict的内容放到apk_lib_info_dict中
    for test_apk_id, libs in test_apk_lib_info.items():
        apk_lib_info[test_apk_id] = libs
    return apk_lib_info


def create_dict_file(train_dataset):
    # 这里创建dict文件
    parser = arg_parse()
    apk_list = json.load(open(file='metadata/config/apk_info.json', mode='r'))
    lib_list = json.load(open(file='metadata/config/lib_info.json', mode='r'))

    if not os.path.exists(train_dataset + '/apk_lib_info.json'):
        apk_lib_fp = open(file=train_dataset + "/apk_lib_info.json", mode='w')
        apk_lib_dict = get_apk_lib_info(train_dataset)
        json.dump(obj=apk_lib_dict, fp=apk_lib_fp)
        apk_lib_fp.close()
    else:
        with open(file=train_dataset + '/apk_lib_info.json', mode='r') as fp:
            apk_lib_dict = json.load(fp)

    # 循环对所有的apk创建数据
    for apk_id, apk_lib_list in apk_lib_dict.items():
        apk_name = apk_list[apk_id]
        dict_file_name = 'dict__' + apk_name + '.txt'
        dict_file_fp = open(file=train_dataset + '/' + parser.dict_path + '/' + dict_file_name, mode='w')
        write_id = 1
        write_name = str(write_id) + '\t' + apk_name + '\n'
        dict_file_fp.write(write_name)

        for lib_id in apk_lib_list:
            write_id += 1
            lib_name = lib_list[str(lib_id)]
            write_name = str(write_id) + '\t#DEP#' + lib_name + '\n'
            dict_file_fp.write(write_name)
        dict_file_fp.close()


def create_graph_file(train_dataset):
    apk_list = json.load(fp=open(file='metadata/config/apk_info.json', mode='r'))

    if not os.path.exists(train_dataset + '/apk_lib_info.json'):
        w_l_fp = open(file=train_dataset + '/apk_lib_info.json', mode='w')
        apk_lib_dict = get_apk_lib_info(train_dataset)
        json.dump(obj=apk_lib_dict, fp=w_l_fp)
        w_l_fp.close()
    else:
        with open(file=train_dataset + '/apk_lib_info.json', mode='r') as al_fp:
            apk_lib_dict = json.load(fp=al_fp)

    for apk_id, apk_lib_list in apk_lib_dict.items():
        apk_name = apk_list[apk_id]
        graph_file_name = 'graph__' + apk_name + '.txt'
        graph_file_fp = open(file=train_dataset + '/' + args.graph_path + '/' + graph_file_name, mode='w')
        write_lib = [i+2 for i in range(len(apk_lib_list))]
        for w_l in write_lib:
            content = str(1) + '#' + str(w_l) + '\n'
            graph_file_fp.write(content)
        graph_file_fp.close()


def create_test_file(train_dataset):
    if not os.path.exists(train_dataset + '/test_info.json'):
        apk_info = json.load(open(file='metadata/config/apk_info.json', mode='r'))
        test_file_fp = open(file=train_dataset + '/test_info.json', mode='w')
        test_project_info = {}
        # 我需要拿到testing测试的json文件
        for file in os.listdir(train_dataset):
            if 'testing' in file:
                test_file_name = file
                break

        with open(file=train_dataset + '/' + test_file_name, mode='r') as fp:
            for test_pro in fp.readlines():
                test_pro = test_pro.strip('\n')
                test_pro_obj = json.loads(test_pro)
                test_apk_id  = str(test_pro_obj['app_id'])
                test_apk_name = apk_info[test_apk_id]
                test_project_info[test_apk_id] = test_apk_name

        json.dump(obj=test_project_info, fp=test_file_fp)
        test_file_fp.close()


def create_train_file(train_dataset):
    if not os.path.exists(train_dataset + '/train_info.json'):
        apk_info = json.load(open(file='metadata/config/apk_info.json', mode='r'))
        test_info = json.load(open(file=train_dataset + '/test_info.json', mode='r'))
        train_info = dict()

        for apk_id, apk_name in apk_info.items():
            if apk_id not in test_info.keys():
                train_info[apk_id] = apk_name

        with open(file=train_dataset + '/train_info.json', mode='w') as train_fp:
            json.dump(obj=train_info, fp=train_fp)


def scan_folder(train_dataset):
    base_path = train_dataset + '/'
    if not os.path.exists('metadata/config'):
        os.mkdir('metadata/config')
    if not os.path.exists(base_path + args.dict_path):
        os.mkdir(base_path + args.dict_path)
    if not os.path.exists(base_path + args.graph_path):
        os.mkdir(base_path + args.graph_path)
    if not os.path.exists(base_path + args.ground_truth_path):
        os.mkdir(base_path + args.ground_truth_path)
    if not os.path.exists(base_path + args.similarities_path):
        os.mkdir(base_path + args.similarities_path)
    if not os.path.exists(base_path + args.recommendation_path):
        os.mkdir(base_path + args.recommendation_path)


def create_data(train_dataset):
    scan_folder(train_dataset)
    create_apk_info()
    create_lib_info()
    create_dict_file(train_dataset)          # 这个就要求在数据集中创建了
    create_graph_file(train_dataset)
    create_test_file(train_dataset)
    create_train_file(train_dataset)

