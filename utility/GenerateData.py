import os
import json

from time import time
from tqdm import tqdm
from utility.parser import arg_parse

args = arg_parse()


def create_apk_info():
    if not os.path.exists(args.config_path):
        os.mkdir(args.config_path)
    if not os.path.exists(args.config_path + '/apk_info.json'):
        apk_list = {}
        with open(file=args.config_path + '/apk_info.csv', mode='r') as apk_fp:
            for apk_info in apk_fp.readlines():
                apk_pair = apk_info.strip('\n').split(',')
                apk_id = int(apk_pair[0])
                dot_idx = apk_pair[1].strip('\n').rindex('.')
                apk_name = apk_pair[1][:dot_idx]
                apk_list[apk_id] = apk_name
        with open(file=args.config_path + '/apk_info.json', mode='w') as apk_fp:
            json.dump(apk_list, fp=apk_fp)


def create_lib_info():
    if not os.path.exists(args.config_path + '/lib_info.json'):
        lib_list = {}
        with open(file=args.config_path + '/lib_info.csv', mode='r') as lib_fp:
            for lib_info in lib_fp.readlines():
                lib_pair = lib_info.strip('\n').split(',')
                lib_id = int(lib_pair[0])
                lib_name = lib_pair[1]
                lib_list[lib_id] = lib_name
        with open(file=args.config_path + '/lib_info.json', mode='w') as lib_fp:
            json.dump(obj=lib_list, fp=lib_fp)


def get_apk_lib_info(train_dataset):
    print('creating apk_lib info.....')
    # 记录一下创建apk_lib的时间
    start_time = time()
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

    # 到这结束，apk_lib_info中都是train的info，还需要再把test_dict的内容放到apk_lib_info_dict中
    for test_apk_id, libs in test_apk_lib_info.items():
        apk_lib_info[test_apk_id] = libs
    res_s = 'apk_lib_info created finish.     [%.4fs]' % (time() - start_time)
    print(res_s)
    return apk_lib_info


def create_dict_file(train_dataset):
    # 这里创建dict文件
    apk_list = json.load(open(file=args.config_path + '/apk_info.json', mode='r'))
    lib_list = json.load(open(file=args.config_path + '/lib_info.json', mode='r'))

    if not os.path.exists(train_dataset + '/apk_lib_info.json'):
        apk_lib_fp = open(file=train_dataset + "/apk_lib_info.json", mode='w')
        apk_lib_dict = get_apk_lib_info(train_dataset)
        json.dump(obj=apk_lib_dict, fp=apk_lib_fp)
        apk_lib_fp.close()
    else:
        with open(file=train_dataset + '/apk_lib_info.json', mode='r') as fp:
            apk_lib_dict = json.load(fp)

    if len(os.listdir(train_dataset + '/' + args.dict_path)) == 0:
        dict_process_bar = tqdm(desc='creating dict file....', total=len(apk_lib_dict), leave=True)
        # 循环对所有的apk创建数据
        for apk_id, apk_lib_list in apk_lib_dict.items():
            apk_name = apk_list[str(apk_id)]
            dict_file_name = 'dict__' + apk_name + '.txt'
            dict_file_fp = open(file=train_dataset + '/' + args.dict_path + '/' + dict_file_name, mode='w')
            write_id = 1
            write_name = str(write_id) + '\t' + apk_name + '\n'
            dict_file_fp.write(write_name)

            for lib_id in apk_lib_list:
                write_id += 1
                lib_name = lib_list[str(lib_id)]
                write_name = str(write_id) + '\t#DEP#' + lib_name + '\n'
                dict_file_fp.write(write_name)
            dict_process_bar.update()
            dict_file_fp.close()
        dict_process_bar.close()


def create_graph_file(train_dataset):
    apk_list = json.load(fp=open(file=args.config_path + '/apk_info.json', mode='r'))

    if not os.path.exists(train_dataset + '/apk_lib_info.json'):
        w_l_fp = open(file=train_dataset + '/apk_lib_info.json', mode='w')
        apk_lib_dict = get_apk_lib_info(train_dataset)
        json.dump(obj=apk_lib_dict, fp=w_l_fp)
        w_l_fp.close()
    else:
        with open(file=train_dataset + '/apk_lib_info.json', mode='r') as al_fp:
            apk_lib_dict = json.load(fp=al_fp)

    if len(os.listdir(train_dataset + '/' + args.graph_path)) == 0:
        graph_process_bar = tqdm(desc='create graph file....', total=len(apk_lib_dict), leave=True)

        for apk_id, apk_lib_list in apk_lib_dict.items():
            apk_name = apk_list[apk_id]
            graph_file_name = 'graph__' + apk_name + '.txt'
            graph_file_fp = open(file=train_dataset + '/' + args.graph_path + '/' + graph_file_name, mode='w')
            write_lib = [i+2 for i in range(len(apk_lib_list))]
            for w_l in write_lib:
                content = str(1) + '#' + str(w_l) + '\n'
                graph_file_fp.write(content)
            graph_process_bar.update()
            graph_file_fp.close()
        graph_process_bar.close()


def create_test_file(train_dataset):
    print('creating test file...')
    start_time = time()
    if not os.path.exists(train_dataset + '/test_info.json'):
        apk_info = json.load(open(file=args.config_path + '/apk_info.json', mode='r'))
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
    res_s = 'test_file created finish.    [%.4fs]' % (time() - start_time)
    print(res_s)


def create_train_file(train_dataset):
    # 按道理来说，这样创建train_file是不正确的, 重新创建一下
    # 就算apk_lib_info 那里没问题，但是在这里根据apk_lib_info创建train是绝对有问题的
    print('creating train file...')
    start_time = time()
    if not os.path.exists(train_dataset + '/train_info.json'):
        train_apk_lib_fp = open(file='%s/train_%s.csv' % (train_dataset, args.dataset), mode='r')
        apk_info_fp = open(file=args.config_path + '/apk_info.json', mode='r')

        apk_info = json.load(apk_info_fp)
        train_info = {}
        with open(file=train_dataset + '/train_info.json', mode='w') as fp:
            for l in train_apk_lib_fp.readlines():
                l = l.strip('\n').split(',')
                apk_id = l[0]
                apk_name = apk_info[str(apk_id)]
                train_info[apk_id] = apk_name
            json.dump(obj=train_info, fp=fp)

        train_apk_lib_fp.close()
        apk_info_fp.close()
    res_s = 'created train file finish     [%.4fs]' % (time() - start_time)
    print(res_s)


def scan_folder(train_dataset):
    base_path = train_dataset + '/'
    if not os.path.exists(args.config_path):
        os.mkdir(args.config_path)
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
    # 需要在以下步骤中加上进度条
    create_dict_file(train_dataset)          # 这个就要求在数据集中创建了
    create_graph_file(train_dataset)
    create_test_file(train_dataset)
    create_train_file(train_dataset)
