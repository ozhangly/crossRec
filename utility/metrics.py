import numpy as np
from typing import Dict, Sequence


def accuracy_list(recommend_list: Sequence[int], pos_list: Sequence[int]) -> Sequence[int]:
    acc = []
    for i in recommend_list:
        if i in pos_list:
            acc.append(1)
        else:
            acc.append(0)
    return acc


def precision_at_k(acc_list: Sequence[int], k: int):
    acc = np.array(acc_list)[:k]
    return np.mean(acc)


def mrr_at_k(acc_list: Sequence[int], k: int) -> float:
    r = acc_list[:k]
    res = 0.
    for i in range(k):
        if r[i] == 1:
            res = 1 / (i + 1)
            break
    return res


def recall_at_k(acc_list: Sequence[int], ground_truth_len: int, k:int):
    r = np.asfarray(acc_list)[:k]
    return np.sum(r) / ground_truth_len


def average_precision(rs: Sequence[int], k: int) -> float:
    r = np.asarray(rs)[:k]
    out = [precision_at_k(r, k+1) for k in range(k) if r[k]]
    if not out:
        return 0.
    return np.sum(out) / float(np.sum(r))


def f_one_score(precision_at_k_score: float, recall_at_k_score: float) -> float:
    if precision_at_k_score + recall_at_k_score > 0:
        return (2.0 * precision_at_k_score * recall_at_k_score) / (precision_at_k_score + recall_at_k_score)
    else:
        return 0.


def test_one_app(recommend_list: Sequence[int], pos_list: Sequence[int], k_max: Sequence[int]) -> Dict:
    precision_list, mrr_list, recall_list, map_list, fone_list = [], [], [], [], []
    # 该怎么进行
    # 需要查看recommend_list是否在pos_list中
    acc_list = accuracy_list(recommend_list=recommend_list, pos_list=pos_list)
    # 需要根据acc_list计算metric
    for k in k_max:
        precision_list += [precision_at_k(acc_list, k)]
        mrr_list += [mrr_at_k(acc_list, k)]
        recall_list += [recall_at_k(acc_list, len(pos_list), k)]
        map_list += [average_precision(recommend_list, k)]
        fone_list += [f_one_score(precision_at_k(acc_list, k), recall_at_k(acc_list, k, len(pos_list)))]

    return {'precision': np.array(precision_list), 'mrr': np.array(mrr_list), 'recall': recall_list,
            'map': np.array(map_list), 'fone': np.array(fone_list)}
