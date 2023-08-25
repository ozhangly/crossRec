import os
import time
import json

from tqdm import tqdm
from utility.parser import arg_parse


def create_apk_info():
    if not os.path.exists('metadata/config'):
        os.mkdir('metadata/config')
    if not os.path.exists('metadata/config/apk_info.json'):
        apk_list = {}
        print('creating apk_info file....')
        with open(file='metadata/apk_info.csv', mode='r') as apk_fp:
            for apk_info in tqdm(apk_fp.readlines()):
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
        print('creating lib_info file...')
        with open(file='metadata/lib_info.csv', mode='r') as lib_fp:
            for lib_info in tqdm(lib_fp.readlines()):
                lib_pair = lib_info.strip('\n').split(',')
                lib_id = int(lib_pair[0])
                lib_name = lib_pair[1]
                lib_list[lib_id] = lib_name
        with open(file='metadata/config/lib_info.json', mode='w') as lib_fp:
            json.dump(obj=lib_list, fp=lib_fp)


def get_apk_lib_info():
    # 需要创建一个dict，为apk和lib的调用关系
    apk_lib_info = {}
    test_apk_lib_info = {}
    # 先吧test的写进去
    with open(file='metadata/config/testing_0_removed_num_1.json', mode='r') as fp:
        for line in fp.readlines():
            line = line.strip('\n')
            obj = json.loads(line)
            apk_id, libs = obj['app_id'], obj['tpl_list']
            test_apk_lib_info[apk_id] = libs
    with open(file='metadata/relation.csv', mode='r') as rel_fp:
        for apk_lib in rel_fp.readlines():
            apk_lib_pair = apk_lib.strip('\n').split(',')
            apk_id = int(apk_lib_pair[0])
            lib_id = int(apk_lib_pair[1])
            if apk_id in test_apk_lib_info.keys():
                continue
            if apk_id not in apk_lib_info.keys():
                apk_lib_list = [lib_id]
                apk_lib_info[apk_id] = apk_lib_list
            else:
                apk_lib_info[apk_id].append(lib_id)
        # 到这结束，apk_lib_list中都是train的info，还需要再把test_dict的内容放到apk_lib_info_dict中
        for test_apk_id, libs in test_apk_lib_info.items():
            apk_lib_info[test_apk_id] = libs
    return apk_lib_info


def create_dict_file():
    # 需要在relation中读到调用关系，并且创建dict和graph文件
    # 这里创建dict文件
    parser = arg_parse()
    apk_list = json.load(open(file='metadata/config/apk_info.json', mode='r'))
    lib_list = json.load(open(file='metadata/config/lib_info.json', mode='r'))

    if not os.path.exists('metadata/dict'):
        os.mkdir('metadata/dict')

    if not os.path.exists('metadata/config/apk_lib_info.json'):
        apk_lib_fp = open(file="metadata/config/apk_lib_info.json", mode='w')
        apk_lib_dict = get_apk_lib_info()
        json.dump(obj=apk_lib_dict, fp=apk_lib_fp)
        apk_lib_fp.close()
    else:
        with open(file='metadata/config/apk_lib_info.json', mode='r') as fp:
            apk_lib_dict = json.load(fp)

    prog_bar = tqdm(desc='creating dict file....',
                    leave=True,
                    total=len(apk_lib_dict))

    # 循环对所有的apk创建数据
    for apk_id, apk_lib_list in apk_lib_dict.items():
        prog_bar.update()
        apk_name = apk_list[apk_id]
        dict_file_name = 'dict__' + apk_name + '.txt'
        dict_file_fp = open(file=parser.dict_path + dict_file_name, mode='w')
        write_id = 1
        write_name = str(write_id) + '\t' + apk_name + '\n'
        dict_file_fp.write(write_name)

        for lib_id in apk_lib_list:
            write_id += 1
            lib_name = lib_list[str(lib_id)]
            write_name = str(write_id) + '\t#DEP#' + lib_name + '\n'
            dict_file_fp.write(write_name)
        dict_file_fp.close()
    prog_bar.close()
    print('create dict file complete')



def create_graph_file():
    apk_list = json.load(fp=open(file='metadata/config/apk_info.json', mode='r'))

    if not os.path.exists('metadata/graph'):
        os.mkdir('metadata/graph')

    if not os.path.exists('metadata/config/apk_lib_info.json'):
        w_l_fp = open(file='metadata/config/apk_lib_info.json', mode='w')
        apk_lib_dict = get_apk_lib_info()
        json.dump(obj=apk_lib_dict, fp=w_l_fp)
        w_l_fp.close()
    else:
        with open(file='metadata/config/apk_lib_info.json', mode='r') as al_fp:
            apk_lib_dict = json.load(fp=al_fp)

    prog_bar = tqdm(desc='creating graph file....',
                    leave=True,
                    total=len(apk_lib_dict))
    for apk_id, apk_lib_list in apk_lib_dict.items():
        prog_bar.update()
        apk_name = apk_list[apk_id]
        graph_file_name = 'graph__' + apk_name + '.txt'
        graph_file_fp = open(file='metadata/graph/' + graph_file_name, mode='w')
        write_lib = [i+2 for i in range(len(apk_lib_list))]
        for w_l in write_lib:
            content = str(1) + '#' + str(w_l) + '\n'
            graph_file_fp.write(content)
        graph_file_fp.close()
    prog_bar.close()
    print('creat graph file complete')



def create_test_file():
    if not os.path.exists('metadata/config/test_info.json'):
        apk_info = json.load(open(file='metadata/config/apk_info.json', mode='r'))
        test_file_fp = open(file='metadata/config/test_info.json', mode='w')
        test_project_info = {}
        with open(file='metadata/config/testing_0_removed_num_1.json', mode='r') as fp:
            for test_pro in fp.readlines():
                test_pro = test_pro.strip('\n')
                test_pro_obj = json.loads(test_pro)
                test_apk_id  = str(test_pro_obj['app_id'])
                test_apk_name = apk_info[test_apk_id]
                test_project_info[test_apk_id] = test_apk_name

        json.dump(obj=test_project_info, fp=test_file_fp)
        test_file_fp.close()




def create_train_file():
    if not os.path.exists('metadata/config/train_info.json'):
        apk_info = json.load(open(file='metadata/config/apk_info.json', mode='r'))
        test_info = json.load(open(file='metadata/config/test_info.json', mode='r'))
        train_info = dict()

        for apk_id, apk_name in apk_info.items():
            if apk_id not in test_info.keys():
                train_info[apk_id] = apk_name

        with open(file='metadata/config/train_info.json', mode='w') as train_fp:
            json.dump(obj=train_info, fp = train_fp)


def create_data():
    create_apk_info()
    create_lib_info()
    create_dict_file()
    create_graph_file()
    create_test_file()
    create_train_file()

