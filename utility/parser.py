import argparse


def arg_parse():
    parser = argparse.ArgumentParser(description='crossRec run config')

    parser.add_argument('--dict_path', nargs='?', default='metadata/dict/', help='the dict file path')
    parser.add_argument('--graph_path', nargs='?', default='metadata/graph/', help='the graph file path')
    parser.add_argument('--ground_truth_path', nargs='?', default='metadata/groundtruth/')
    parser.add_argument('--similarities_path', nargs='?', default='metadata/similarity/', type=str)
    parser.add_argument('--numofneighbours', nargs='?', default=10, type=int)
    parser.add_argument('--recommendation_path', nargs='?', default='metadata/recommendation/')
    parser.add_argument('--recommend_top_n', nargs='?', type=int, default=10)

    return parser.parse_args()
