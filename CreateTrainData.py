"""
一、生成训练数据
"""
import shutil
import json
import os.path

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

rmv_num = [1, 5, 10]
fold_num = [0, 1, 2, 3, 4]

for rmv in rmv_num:
    for fold in fold_num:
        apk_lib_dict = {}
        training_data = open(file=f'./training data/train_CF_{fold}_{rmv}.json', mode='r')
        ensure_dir(f'./training dataset/CF_{fold}_{rmv}')
        apk_lib_file = open(file=f'./training dataset/CF_{fold}_{rmv}/apk_lib_info.json', mode='w')
        train_CF = open(file=f'./training dataset/CF_{fold}_{rmv}/train_CF_{fold}_{rmv}.csv', mode='w')


        # 把test数据复制到指定文件夹下
        shutil.copyfile(src=f'./testing data/testing_{fold}_{rmv}.json', dst=f'./training dataset/CF_{fold}_{rmv}/testing_{fold}_{rmv}.json')

        for lines in training_data.readlines():
            obj = json.loads(lines.strip())
            app_id = obj['app_id']
            tpl_list = obj['tpl_list']

            apk_lib_dict[app_id] = tpl_list

            pair = [app_id] + tpl_list
            line = ','.join(str(i) for i in pair)
            train_CF.write(line + '\n')

        json.dump(obj=apk_lib_dict, fp=apk_lib_file)
        training_data.close()
        apk_lib_file.close()
        train_CF.close()
