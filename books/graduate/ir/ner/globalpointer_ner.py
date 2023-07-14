import numpy as np
from bert4keras.snippets import to_array
import sys
import os

# 获取当前脚本所在的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
globalpointer_ner_dir = os.path.join(script_dir, '../../ie/ner')
# 将当前脚本所在的目录添加到系统路径中
sys.path.append(globalpointer_ner_dir)

from books.graduate.ie.ner.globalpointer_ner import model, tokenizer, categories


class MedicalNER(object):
    """
        命名实体识别
    """
    def __init__(self):
        self.model = model.load_weights(os.path.join(script_dir, "../../util/checkpoint/ner/best_model_cmed_globalpointer"
                                                                 ".weights"))
        self.tokenizer = tokenizer
        self.categories = categories

    def recognize(self, text, threshold=0):
        tokens = self.tokenizer.tokenize(text, maxlen=512)
        mapping = self.tokenizer.rematch(text, tokens)
        token_ids = self.tokenizer.tokens_to_ids(tokens)
        segment_ids = [0] * len(token_ids)
        token_ids, segment_ids = to_array([token_ids], [segment_ids])
        scores = model.predict([token_ids, segment_ids])[0]
        scores[:, [0, -1]] -= np.inf
        scores[:, :, [0, -1]] -= np.inf
        entities = []
        for l, start, end in zip(*np.where(scores > threshold)):
            entities.append(
                (mapping[start][0], mapping[end][-1], self.categories[l])
            )
        # print("entities: ")
        # print(entities)
        # return entities
        target_answer = {"string": text, "entities": []}
        target_entities = []
        for (start, end, type) in entities:
            item = {"word": text[start:end + 1], "type": type}
            target_entities.append(item)
        target_answer["entities"] = target_entities
        return target_answer


