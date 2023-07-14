import sys
import os

# 获取当前脚本所在的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))

ner_dir = os.path.join(script_dir, 'ner')
intent_dir = os.path.join(script_dir, 'intent')
config_dir = os.path.join(script_dir)

globalpointer_ner_dir = os.path.join(script_dir, '../ie/ner')
# 将当前脚本所在的目录添加到系统路径中
sys.path.append(ner_dir)
sys.path.append(intent_dir)
sys.path.append(config_dir)
sys.path.append(globalpointer_ner_dir)

from ner.globalpointer_ner import MedicalNER
from intent.intent_bert_recg import BertIntentModel
from config import CONFIG
from py2neo import Graph


class IR:
    def __init__(self):
        self.graph = Graph("bolt://localhost:7687")
        self.intent_classifier = BertIntentModel()
        self.ner = MedicalNER()
        self.config = CONFIG()

    def intent_classify(self, text):
        # print(text)
        result = self.intent_classifier.predict(text)
        print(result)
        return result

    def ner_recognizer(self, text):
        result = self.ner.recognize(text=text)
        print(result)
        return result

    def entity_link(self, mention, type):
        #TODO 实体链接(缺乏数据集)
        return mention

    def semantic_parser(self, text):
        """
        对用户输入文本进行解析,然后填槽，确定回复策略
        :param text:
        :param user:
        :return:
                填充slot_info中的["slot_values"]
                填充slot_info中的["intent_strategy"]
        """
        # 对医疗意图进行二次分类
        intent_receive = self.intent_classify(text)  # {'confidence': 0.8997645974159241, 'intent': '治疗方法'}
        # print("intent_receive:", intent_receive)
        # 实体识别
        slot_receive = self.ner_recognizer(text)
        # print("slot_receive:", slot_receive)

        if intent_receive == -1 or slot_receive == -1 or intent_receive.get("intent") == "其他":
            return self.config.semantic_slot.get("unrecognized")

        # print("intent:", intent_receive.get("intent"))
        slot_info = self.config.semantic_slot.get(intent_receive.get("intent"))
        # print("slot_info:", slot_info)
        # 根据意图的置信度来确认回复策略
        # TODO 使用强化学习进行策略选择
        conf = intent_receive.get("confidence")
        if conf >= self.config.intent_threshold_config["accept"]:  # >0.8
            slot_info["intent_strategy"] = "accept"
        elif conf >= self.config.intent_threshold_config["deny"]:  # >0.4
            slot_info["intent_strategy"] = "clarify"
        else:
            slot_info["intent_strategy"] = "deny"

        disease_entity = slot_receive["entities"][0]["word"]
        slot_info["slot_values"] = {
            "relation": intent_receive.get("intent"),
            "Disease": disease_entity
        }
        return slot_info

    def neo4j_search(self, cql_list):
        ress = ""
        if isinstance(cql_list, list):
            for cql in cql_list:
                data = self.graph.run(cql).data()
                if not data:
                    continue
                p_name = data[0]["p.name"]
                r_role = data[0]["r.role"]
                q_list = []
                for item in data:
                    q_list.append(item["q.name"])
                answer_type = p_name + "的" + r_role + "包括: " + "、".join(q_list)
                ress += answer_type + "\n"
            if ress == "":
                ress = "None"
        else:
            data = self.graph.run(cql_list).data()
            # 这里要分情况：1、查到了，且不为空；2、查到了，但是结果是None([{'p.desc': None}] )；3、直接连不上数据库
            # 三种情况都要有对应的兜底处理
            if not data:
                return ress
            # rst = []
            # for item in data:
            #     item_values = list(item.values())
            #     if isinstance(item_values[0], list):
            #         rst.extend(item_values[0])
            #     else:
            #         rst.extend(item_values)
            # data = "、".join([str(i) for i in rst])
            # ress += data
        return ress

    def get_answer(self, slot_info):
        cql_L = slot_info["cql_L"]
        cql_M = slot_info["cql_M"]
        cql_R = slot_info["cql_R"]
        reply_template = slot_info["reply_template"]
        slot_values = slot_info["slot_values"]
        strategy = slot_info["intent_strategy"]

        # if not slot_values:
        #     return slot_info
        if strategy == "accept" or strategy == "clarify":
            cql_list = []
            cql_L = cql_L.format(**slot_values)
            cql_R = cql_R
            if isinstance(cql_M, list):
                for cql in cql_M:
                    # print(cql.format(**slot_values))
                    cql = cql_L + cql + cql_R
                    cql_list.append(cql)  # 通过字典设置参数
            else:
                cql_list = cql_L + cql_M + cql_R

            answer = self.neo4j_search(cql_list)
            # print("answer :")
            # print(answer)
            # print("neo4j result for accept:", answer)
            if not answer:
                slot_info["replay_answer"] = "似乎并没有理解您的意思呢~"

            elif answer == "None":
                slot_info["replay_answer"] = "数据库中没有查到相关内容哦~"
            else:
                # pattern = reply_template.format(**slot_values)
                slot_info["replay_answer"] = answer

            # print(slot_info)
        # elif strategy == "clarify":
        #     # 0.4 < 意图置信度 < 0.8时，进行问题澄清
        #     pattern = ask_template.format(**slot_values)
        #     # print("pattern for clarity:", pattern)
        #
        #     slot_info["replay_answer"] = pattern
        #     # 得到肯定意图之后，需要给出用户回复的答案
        #     cql_list = []
        #     if isinstance(cql_template, list):
        #         for cql in cql_template:
        #             cql_list.append(cql.format(**slot_values))
        #     else:
        #         cql_list = cql_template.format(**slot_values)
        #
        #     answer = self.neo4j_search(cql_list)
        #     # print("neo4j result for clarify:", answer)
        #
        #     if not answer:
        #         slot_info["replay_answer"] = "似乎并没有理解您的意思呢~"
        #
        #     elif answer == "None":
        #         slot_info["choice_answer"] = "数据库中没有查到相关内容哦~"
        #
        #     else:
        #         pattern = reply_template.format(**slot_values)
        #         slot_info["choice_answer"] = pattern + answer

        elif strategy == "deny":
            slot_info["replay_answer"] = slot_info.get("deny_response")

        return slot_info

    def read(self, text):
        slot = self.semantic_parser(text)
        answer = self.get_answer(slot)
        return answer["replay_answer"]

    def clear(self):
        pass

# ir = IR()
# text = "心脏病是由什么导致的"
# # print("Query: " + text)
# # answer = ir.read("血友病的疾病表述?")
# # print("NER Process:")
# ner = ir.ner_recognizer(text)
# print(ner)
# print("Intent Recognition Process:")
# intent = ir.intent_classify(text)
# print(intent)



