import json
from utility.parser import arg_parse
from tqdm import tqdm

parser = arg_parse()

def create_libname2id():
    id2lib_name = json.load(fp=open(file='metadata/config/lib_info.json', mode='r'))
    lib_name2id = dict()

    for id, name in id2lib_name.items():
        id = int(id)
        lib_name2id[name] = id

    return lib_name2id


def create_apk_name2id():
    id2apk_name = json.load(fp=open(file='metadata/config/test_info.json', mode='r'))
    apk_name2id = dict()

    for id, name in id2apk_name.items():
        id = int(id)
        apk_name2id[name] = id

    return apk_name2id

def get_test_apk_info():
    apk_info_list = {}
    with open(file='metadata/config/testing_0_removed_num_1.json', mode='r') as fp:
        for info in fp.readlines():
            obj = json.loads(info.strip('\n'))
            val = {}
            val['removed_tpls'] = obj['removed_tpl_list']
            val['tpl_list'] = obj['tpl_list']
            apk_info_list[obj['app_id']] = val
    return apk_info_list

def generate_test_json():
    lib_name2id = create_libname2id()
    apk_name2id = create_apk_name2id()
    test_apk_info = get_test_apk_info()

    with open(file='metadata/output/test_wide_deep_change(1).json', mode='w') as w_fp:
        for apk_name, id in tqdm(apk_name2id.items()):
            write_dict = {}
            recommend_list = []
            with open(file=parser.recommendation_path + apk_name + '.txt', mode='r') as fp:
                for lib in fp.readlines():
                    lib = lib.strip('\n').replace('#DEP#', '')
                    lib_name = lib.split('\t')[0]
                    lib_id = lib_name2id[lib_name]
                    recommend_list.append(lib_id)

            write_dict['app_id'] = id
            write_dict['recommended_tpl'] = recommend_list
            write_dict['removed_tpls'] = test_apk_info[id]['removed_tpls']
            write_str = json.dumps(obj=write_dict) + '\n'
            w_fp.write(write_str)
