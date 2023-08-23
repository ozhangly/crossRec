import json
import os


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


def get_half_libraries(file_name):
    ret = set()
    dictionary = dict()
    lib_count, half = 0, 0
    with open(file=file_name, mode='r') as fp:
        for line in fp.readlines():
            pair = line.strip('\n').split('\t')
            id   = int(pair[0])
            name = pair[1]
            dictionary[id] = name
            if name.find('#DEP#') != -1:
                lib_count += 1

        size = lib_count
        half = round(size/2)
        lib_count = 0
        for key in dictionary.keys():
            artifact = dictionary[key]
            if artifact.find('#DEP#') != -1:
                ret.add(artifact)
                lib_count += 1
            if lib_count == half:
                break

    return ret


def extract_half_dictionary(file_name, ground_truth_path, parser, get_also_user=False):
    dictionary = dict()
    ret = dict()

    lib_count, half = 0, 0
    with open(file=parser.dict_path + file_name, mode='r') as fp:
        for line in fp.readlines():
            pair = line.strip('\n').split('\t')
            id = int(pair[0])
            name = pair[1]
            dictionary[id] = name
            if name.find('#DEP#') != -1:
                lib_count += 1
    size = lib_count
    half = round(size/2)
    enough_lib = False
    lib_count = 0

    ground_truth_file_name = ground_truth_path + file_name

    # 如果不存在再写这个ground_truth，否则的话直接跳过
    with open(file=ground_truth_file_name, mode='w') as fp:
        for test_key in dictionary.keys():
            artifact = dictionary[test_key]  # dictionary: key:int, val:str
            if lib_count == half:
                enough_lib = True
            if artifact.find('#DEP#') != -1:
                if enough_lib is False:
                    ret[test_key] = artifact
                else:
                    fp.write(str(test_key) + '\t' + artifact + '\n')
                lib_count += 1
            else:
                if get_also_user is True or artifact.find('#DEP#') == -1:
                    ret[test_key] = artifact

    return ret  # dict: key: int, val: str


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
            count+=1
            if count == size:
                break

    return project


def get_similarity_projects(file_name, top_n, parser):
    # 这样做不是更好吗？
    libraries = set()
    project = dict()
    all_neighbours = dict()

    cnt = 0
    # 读取相似project
    with open(file=file_name, mode='r') as fp:
        for line in fp.readlines():
            pair = line.strip('\n').split('\t')
            name = pair[1]
            project[cnt] = name
            lib = get_libraries(parser.dict_path + 'dict__' + name + '.txt')
            all_neighbours[cnt] = lib
            cnt += 1
            libraries = libraries | lib
            if len(libraries) >= top_n:
                break

    return project, all_neighbours, libraries

