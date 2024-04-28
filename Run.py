"""
二、运行程序
"""
import os
import time

from RecommendationEngine import *
from MultiSimilarityComputation import *
from Validation import save_recommend_and_result
from utility.GenerateData import create_data

training_dataset = './training dataset/'
args = arg_parse()
if __name__ == '__main__':
    # 创建数据, 加上进度条
    start_time = time.time()
    create_data(training_dataset + args.dataset)
    cos_similarity(training_dataset + args.dataset)         # 调用的多线程计算相似度
    Recommendation().user_based_recommendation(training_dataset + args.dataset)     # 这里可能会出现除零错误
    save_recommend_and_result(args.output_path, args.dataset, training_dataset)

    # similarity 这个文件目录占用存储太大了，计算完就删除
    print('正在删除使用完的文件')
    os.system('rmdir /Q /S .\\training dataset\\' + args.dataset + '\\dict')
    os.system('rmdir /Q /S .\\training dataset\\' + args.dataset + '\\graph')
    os.system('rmdir /Q /S .\\training dataset\\' + args.dataset + '\\similarity')
    print('删除完成')
