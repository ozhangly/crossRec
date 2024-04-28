import argparse


def arg_parse():
    parser = argparse.ArgumentParser(description='crossRec run config')

    parser.add_argument('--dataset', nargs='?', default='CF_0_1')

    parser.add_argument('--config_path', nargs='?', default='metadata/config')

    parser.add_argument('--dict_path', nargs='?', default='dict')

    parser.add_argument('--graph_path', nargs='?', default='graph')

    parser.add_argument('--output_path', nargs='?', default='output')

    parser.add_argument('--ground_truth_path', nargs='?', default='ground_truth')

    parser.add_argument('--similarities_path', nargs='?', default='similarity')

    parser.add_argument('--recommendation_path', nargs='?', default='recommendation')

    parser.add_argument('--numofneighbours', nargs='?', default=20, type=int)

    parser.add_argument('--recommend_top_n', nargs='?', type=int, default=20)

    parser.add_argument('--remove_n', nargs='?', type=int, default=5)

    return parser.parse_args()
