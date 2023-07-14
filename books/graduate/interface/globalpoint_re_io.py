import numpy as np
from bert4keras.snippets import to_array
import sys
import os

# 获取当前脚本所在的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
globalpointer_re_dir = os.path.join(script_dir, '../ie/re')
# 将当前脚本所在的目录添加到系统路径中
sys.path.append(script_dir)
sys.path.append(globalpointer_re_dir)

from books.graduate.ie.re.globalpointer_re import model, tokenizer, predicate2id, id2predicate


class MedicalSPO(object):
    """
        关系抽取
    """
    def __init__(self):
        self.model = model.load_weights(os.path.join(script_dir, "../util/checkpoint/re/best_model_cmedee_globalpointer.weights"))
        self.tokenizer = tokenizer
        self.maxlen = 128
        self.id2predicate = id2predicate

    def extract_spoes(self, text, threshold=0):
        """抽取输入text所包含的三元组
            :return [(subject, predicate, object)]
        """
        tokens = tokenizer.tokenize(text, maxlen=self.maxlen)
        mapping = tokenizer.rematch(text, tokens)
        token_ids, segment_ids = tokenizer.encode(text, maxlen=self.maxlen)
        token_ids, segment_ids = to_array([token_ids], [segment_ids])
        outputs = model.predict([token_ids, segment_ids])
        outputs = [o[0] for o in outputs]
        # 抽取subject和object
        subjects, objects = set(), set()
        outputs[0][:, [0, -1]] -= np.inf
        outputs[0][:, :, [0, -1]] -= np.inf
        for l, h, t in zip(*np.where(outputs[0] > threshold)):
            if l == 0:
                subjects.add((h, t))
            else:
                objects.add((h, t))
        # 识别对应的predicate
        spoes = set()
        for sh, st in subjects:
            for oh, ot in objects:
                p1s = np.where(outputs[1][:, sh, oh] > threshold)[0]
                p2s = np.where(outputs[2][:, st, ot] > threshold)[0]
                ps = set(p1s) & set(p2s)
                for p in ps:
                    spoes.add((
                        text[mapping[sh][0]:mapping[st][-1] + 1], self.id2predicate[p],
                        text[mapping[oh][0]:mapping[ot][-1] + 1]
                    ))
        return list(spoes)


p = MedicalSPO()
answer = p.extract_spoes("心脏病是由过度劳累导致的, 艾滋病又称HIV")
print(answer)