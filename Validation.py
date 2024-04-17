import os
import re
import json

from tqdm import tqdm
from utility.metrics import *
from utility.parser import arg_parse
from typing import Sequence, Dict
from utility.DataReader import create_libname2id, create_apk_name2id, get_test_apk_info

args = arg_parse()
DONT_EXIST_TPL: int = 800
ks = [1, 3, 5, 10, 20]

def test_one_app(recommend_list: Sequence[int], pos_list: Sequence[int], k_max: Sequence[int]) -> Dict:
    precision_list, mrr_list, recall_list, map_list, fone_list = [], [], [], [], []

    # 需要查看recommend_list是否在pos_list中
    acc_list = accuracy_list(recommend_list=recommend_list, pos_list=pos_list)

    # 需要根据acc_list计算metric
    for k in k_max:
        precision_list += [precision_at_k(acc_list, k)]
        mrr_list += [mrr_at_k(acc_list, k)]
        recall_list += [recall_at_k(acc_list, len(pos_list), k)]
        map_list += [average_precision(acc_list, k)]
        fone_list += [f_one_score(precision_at_k(acc_list, k), recall_at_k(acc_list, k, len(pos_list)))]

    return {'precision': np.array(precision_list), 'mrr': np.array(mrr_list), 'recall': np.array(recall_list),
            'map': np.array(map_list), 'fone': np.array(fone_list)}


def save_recommend_and_result(base_output_path: str, dataset_name: str, training_dataset: str) -> None:
    lib_name2id = create_libname2id(args.config_path)
    apk_name2id = create_apk_name2id(training_dataset, dataset_name)
    test_apk_info = get_test_apk_info(training_dataset + '/' + dataset_name)

    result = {'precision': np.zeros(len(ks)), 'recall': np.zeros(len(ks)), 'map': np.zeros(len(ks)),
              'fone': np.zeros(len(ks)), 'mrr': np.zeros(len(ks))}
    app_num = len(apk_name2id)

    rmv_fold = re.findall(r'\d+', dataset_name)
    testing_output_path = '%s/%s/test_crossRec_%s_%s.json' % (base_output_path, dataset_name, rmv_fold[0], rmv_fold[1])
    result_output_path = '%s/%s/result.csv' % (base_output_path, dataset_name)
    recommend_path = '%s%s/%s' % (training_dataset, dataset_name, args.recommendation_path)

    if not os.path.exists('%s/%s' % (base_output_path, dataset_name)):
        os.mkdir('%s/%s' % (base_output_path, dataset_name))

    w_recom_fp = open(file=testing_output_path, mode='w')
    w_res_fp = open(file=result_output_path, mode='w')

    validation_bar = tqdm(desc='the validation process...', total=len(apk_name2id), leave=True)

    for apk_name, id in apk_name2id.items():
        write_dict = {}
        recommend_list = []

        with open(file=f'{recommend_path}/{apk_name}.txt', mode='r') as fp:
            for lib in fp.readlines():
                lib = lib.strip('\n').replace('#DEP#', '')
                lib_name = lib.split('\t')[0]
                lib_id = lib_name2id[lib_name]
                recommend_list += [lib_id]

        # 这里找完了所有的推荐的lib, 需要计算metric
        res = test_one_app(recommend_list, test_apk_info[id]['removed_tpls'], k_max=ks)
        result['precision'] += (res['precision'] / app_num)
        result['recall'] += (res['recall'] / app_num)
        result['map'] += (res['map'] / app_num)
        result['fone'] += (res['fone'] / app_num)
        result['mrr'] += (res['mrr'] / app_num)

        write_dict['app_id'] = id
        tpl_list = test_apk_info[id]['tpl_list']
        if len(tpl_list) == 0:
            write_dict['recommend_tpls'] = [DONT_EXIST_TPL] * max(ks)
        else:
            write_dict['recommend_tpls'] = recommend_list
        write_dict['tpl_list'] = test_apk_info[id]['tpl_list']
        write_dict['removed_tpls'] = test_apk_info[id]['removed_tpls']
        write_str = json.dumps(obj=write_dict) + '\n'
        w_recom_fp.write(write_str)
        validation_bar.update()
    w_recom_fp.close()
    validation_bar.close()

    pref_res = '%s\n%s\n%s\n%s\n%s\n' % (
        ','.join(['%.5f' % i for i in result['recall']]),
        ','.join(['%.5f' % i for i in result['precision']]),
        ','.join(['%.5f' % i for i in result['map']]),
        ','.join(['%.5f' % i for i in result['mrr']]),
        ','.join(['%.5f' % i for i in result['fone']]),
    )
    w_res_fp.write(pref_res)
    w_res_fp.close()


if __name__ == '__main__':
    save_recommend_and_result('output', 'CF_0_1', './training dataset/')
