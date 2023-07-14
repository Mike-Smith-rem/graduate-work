#! -*- coding: utf-8 -*-
# 用GlobalPointer做中文命名实体识别
import json
import sys

import numpy as np
from bert4keras.backend import keras, K
from bert4keras.backend import multilabel_categorical_crossentropy
from bert4keras.layers import GlobalPointer
from bert4keras.models import build_transformer_model
from bert4keras.tokenizers import Tokenizer
from bert4keras.optimizers import Adam
from bert4keras.snippets import sequence_padding, DataGenerator
from bert4keras.snippets import open, to_array
from keras.models import Model
from tqdm import tqdm
import os
script_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_path)

maxlen = 256
epochs = 2
batch_size = 4
learning_rate = 2e-5
# categories = set()

# bert配置
config_path = 'C:/Users/abb255/demo/books/graduate/util/model_hub/roberta_zh_l12/bert_config.json'
checkpoint_path = 'C:/Users/abb255/demo/books/graduate/util/model_hub/roberta_zh_l12/bert_model.ckpt'
dict_path = 'C:/Users/abb255/demo/books/graduate/util/model_hub/roberta_zh_l12/vocab.txt'


def load_data(filename):
    """加载数据
    单条格式：[text, (start, end, label), (start, end, label), ...]，
              意味着text[start:end + 1]是类型为label的实体。
    """
    D = []
    category = set()
    try:
        with open(filename, "r", encoding="utf8") as f:
            json_file = json.load(f)
            for item in json_file:
                d = [item["text"]]
                entities = item["entities"]
                for entity in entities:
                    d.append((entity["start_idx"], entity["end_idx"], entity["type"]))
                    category.add(entity["type"])
                D.append(d)
        return D
    except:
        return D


# 标注数据
# train_data = load_data("C:/Users/abb255/PycharmProjects/graduate/util/data_hub/CMeEE/CMeEE-V2_train.json")
# valid_data = load_data("C:/Users/abb255/PycharmProjects/graduate/util/data_hub/CMeEE/CMeEE-V2_dev.json")
# test_data = load_data("C:/Users/abb255/PycharmProjects/graduate/util/data_hub/CMeEE/CMeEE-V2_test.json")
train_data = load_data(os.path.join(script_path, "../../util/data_hub/CMeEE/CMeEE-V2_train.json"))
valid_data = load_data(os.path.join(script_path, "../../util/data_hub/CMeEE/CMeEE-V2_dev.json"))
test_data = load_data(os.path.join(script_path, "../../util/data_hub/CMeEE/CMeEE-V2_test.json"))

category_dict = {'bod': '身体', 'dep': '科室', 'dis': '疾病',
                 'dru': '药物', 'equ': '医疗设备', 'ite': '医学检验项目',
                 'mic': '微生物类', 'pro': '医疗程序', 'sym': '临床表现'}
categories = [v for v in category_dict.keys()]
# 建立分词器
tokenizer = Tokenizer(dict_path, do_lower_case=True)


def dump_category(filepath):
    with open(filepath, "w", encoding="utf8") as f:
        json.dump(category_dict, f, ensure_ascii=False, indent=1)


class data_generator(DataGenerator):
    """数据生成器
    """

    def __iter__(self, random=False):
        batch_token_ids, batch_segment_ids, batch_labels = [], [], []
        for is_end, d in self.sample(random):
            tokens = tokenizer.tokenize(d[0], maxlen=maxlen)
            mapping = tokenizer.rematch(d[0], tokens)
            start_mapping = {j[0]: i for i, j in enumerate(mapping) if j}
            end_mapping = {j[-1]: i for i, j in enumerate(mapping) if j}
            token_ids = tokenizer.tokens_to_ids(tokens)
            segment_ids = [0] * len(token_ids)
            labels = np.zeros((len(categories), maxlen, maxlen))  # 主要的是这里标签构建的不同
            for start, end, label in d[1:]:
                if start in start_mapping and end in end_mapping:
                    start = start_mapping[start]
                    end = end_mapping[end]
                    label = categories.index(label)
                    labels[label, start, end] = 1
            batch_token_ids.append(token_ids)
            batch_segment_ids.append(segment_ids)
            batch_labels.append(labels[:, :len(token_ids), :len(token_ids)])
            if len(batch_token_ids) == self.batch_size or is_end:
                batch_token_ids = sequence_padding(batch_token_ids)
                batch_segment_ids = sequence_padding(batch_segment_ids)
                batch_labels = sequence_padding(batch_labels, seq_dims=3)
                yield [batch_token_ids, batch_segment_ids], batch_labels
                batch_token_ids, batch_segment_ids, batch_labels = [], [], []


def global_pointer_crossentropy(y_true, y_pred):
    """给GlobalPointer设计的交叉熵
    y_pred:[b c l l]，批大小， 类别数目， 句子长度， 句子长度
    """
    bh = K.prod(K.shape(y_pred)[:2])  # 计算张量间的乘积，这里是 批大小×类别数目
    y_true = K.reshape(y_true, (bh, -1))  # 展开
    y_pred = K.reshape(y_pred, (bh, -1))
    return K.mean(multilabel_categorical_crossentropy(y_true, y_pred))  # 这里可参考苏剑林的博客


def global_pointer_f1_score(y_true, y_pred):
    """给GlobalPointer设计的F1
    """
    y_pred = K.cast(K.greater(y_pred, 0), K.floatx())
    return 2 * K.sum(y_true * y_pred) / K.sum(y_true + y_pred)


model = build_transformer_model(config_path, checkpoint_path)
output = GlobalPointer(len(categories), 64)(model.output)

model = Model(model.input, output)
# model.summary()

model.compile(
    loss=global_pointer_crossentropy,
    optimizer=Adam(learning_rate),
    metrics=[global_pointer_f1_score]
)


class NamedEntityRecognizer(object):
    """命名实体识别器
    """

    def recognize(self, text, threshold=0):
        tokens = tokenizer.tokenize(text, maxlen=512)
        mapping = tokenizer.rematch(text, tokens)
        token_ids = tokenizer.tokens_to_ids(tokens)
        segment_ids = [0] * len(token_ids)
        token_ids, segment_ids = to_array([token_ids], [segment_ids])
        scores = model.predict([token_ids, segment_ids])[0]
        scores[:, [0, -1]] -= np.inf
        scores[:, :, [0, -1]] -= np.inf
        entities = []
        for l, start, end in zip(*np.where(scores > threshold)):
            entities.append(
                (mapping[start][0], mapping[end][-1], categories[l])
            )
        return entities


NER = NamedEntityRecognizer()


def evaluate(data):
    """
        :param
        :return
        评测函数
    """
    X, Y, Z = 1e-10, 1e-10, 1e-10
    for d in tqdm(data, ncols=100):
        R = set(NER.recognize(d[0]))
        T = set([tuple(i) for i in d[1:]])
        X += len(R & T)
        Y += len(R)
        Z += len(T)
    f1, precision, recall = 2 * X / (Y + Z), X / Y, X / Z
    return f1, precision, recall


def predict(data):
    """预测函数
    """
    for i, d in enumerate(data):
        R = set(NER.recognize(d[0]))
        print(d[0])
        print(R)
        if i == 10:
            break


dict = []


class Evaluator(keras.callbacks.Callback):
    """评估与保存
    """

    def __init__(self):
        super(Evaluator, self).__init__()
        self.best_val_f1 = 0

    def on_epoch_end(self, epoch, logs=None):
        f1, precision, recall = evaluate(valid_data)
        # 保存最优
        if f1 >= self.best_val_f1:
            self.best_val_f1 = f1
            model.save_weights('robert_model_cmedee_globalpointer.weights')
        print(
            'valid:  f1: %.5f, precision: %.5f, recall: %.5f, best f1: %.5f\n' %
            (f1, precision, recall, self.best_val_f1)
        )
        f1, precision, recall = evaluate(valid_data)
        t = {
            "f1": f1,
            "precision": precision,
            "recall": recall
        }
        print(
            'test:  f1: %.5f, precision: %.5f, recall: %.5f\n' %
            (f1, precision, recall)
        )
        dict.append(t)


if __name__ == '__main__':
    do_train = False
    do_predict = True
    print(categories)
    # dump_category(os.path.join("../data/category.json"))
    if do_train:
        evaluator = Evaluator()
        train_generator = data_generator(train_data, batch_size)

        model.fit(
            train_generator.forfit(),
            steps_per_epoch=len(train_generator),
            epochs=epochs,
            callbacks=[evaluator]
        )
        with open("k.json", "w", encoding="utf8") as f:
            json.dump(dict, f)

    if do_predict:
        # model.load_weights(os.path.join('../../util/checkpoint/ner/best_model_cmed_globalpointer.weights'))
        model.load_weights("robert_model_cmedee_globalpointer.weights")
        f1, precision, recall = evaluate(valid_data)
        t = {
            "f1": f1,
            "precision": precision,
            "recall": recall
        }
        print(
            'test:  f1: %.5f, precision: %.5f, recall: %.5f\n' %
            (f1, precision, recall)
        )
        # predict(test_data)
        # print(NER.recognize("心脏病如何治疗？"))
        # {(start, end, type), ...}
