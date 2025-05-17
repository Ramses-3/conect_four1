import random
import json

random.seed(42)

try:
    with open("id3_tree_mcts_v2.json") as f:
        id3_test_tree = json.load(f)
except FileNotFoundError:
    print("⚠️ Árvore não encontrada. Usando ID3 aleatório.")
    id3_test_tree = {}

def predict_with_tree(tree, example):
    while isinstance(tree, dict):
        if not tree:
            return None
        attr = next(iter(tree))
        if attr not in example:
            return None
        branches = tree[attr]
        val = example.get(attr)
        if val not in branches:
            return None
        tree = branches[val]
    return tree