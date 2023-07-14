from bert4keras.tokenizers import Tokenizer
import os
import sys

# 获取当前脚本所在的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
bert_model_dir = os.path.join(script_dir)
# 将当前脚本所在的目录添加到系统路径中
sys.path.append(bert_model_dir)

from bert_model import build_bert_model


class BertIntentModel(object):
    def __init__(self):
        self.dict_path = os.path.join(script_dir, "../../util/model_hub/chinese_L-12_H-768_A-12/vocab.txt")
        self.config_path = os.path.join(script_dir, "../../util/model_hub/chinese_L-12_H-768_A-12/bert_config.json")
        self.checkpoint_path = os.path.join(script_dir, "../../util/model_hub/chinese_L-12_H-768_A-12/checkpoint")

        self.label_list = [line.strip() for line in open(os.path.join(script_dir, "labeling"), "r", encoding="utf8")]
        self.id2label = {idx: label for idx, label in enumerate(self.label_list)}
        self.tokenizer = Tokenizer(self.dict_path)
        self.model = build_bert_model(self.config_path, self.checkpoint_path, 11)
        self.model.load_weights(os.path.join(script_dir, "../../util/checkpoint/intent/kua_qic_best_model_weights"))

    def predict(self, text):
        token_ids, segment_ids = self.tokenizer.encode(text, maxlen=60)
        predict = self.model.predict([[token_ids], [segment_ids]])
        rst = {l: p for l, p in zip(self.label_list, predict[0])}
        rst = sorted(rst.items(), key=lambda kv: kv[1], reverse=True)
        # print(rst[0])
        intent, confidence = rst[0]
        return {"intent": intent, "confidence": float(confidence)}

