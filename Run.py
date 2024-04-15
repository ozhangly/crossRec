from RecommendationEngine import *
from MultiSimilarityComputation import *
from Validation import save_recommend_and_result
from utility.GenerateData import create_data


# 这个代码改起来还是费点事, 得大改动，而且这个实验项目后期会非常大
training_dataset = './training dataset/'
args = arg_parse()
if __name__ == '__main__':
    # 创建数据, 加上进度条
    create_data(training_dataset + args.dataset)
    cos_similarity(training_dataset + args.dataset)         # 这步耗时是大哥
    Recommendation().user_based_recommendation(training_dataset + args.dataset)
    save_recommend_and_result(args.output_path, args.dataset, training_dataset)
