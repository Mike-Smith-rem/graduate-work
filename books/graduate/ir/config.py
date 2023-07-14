import os
import json
import sys
script_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_path)


def load_intent2pre(output_path):
    load_path = os.path.join(script_path, "knowledge_graph/intent2pre.json")
    pre2intent = {}
    intent2pre = {}
    with open(load_path, "r", encoding="utf8") as f:
        pre2intent = json.load(f)
        for k, v in pre2intent.items():
            if v in intent2pre.keys():
                intent2pre[v].append(k)
            else:
                intent2pre[v] = []
                intent2pre[v].append(k)
    with open(output_path, "w", encoding="utf8") as f:
        json.dump(intent2pre, f, ensure_ascii=False, indent=1)


def get_template():
    template = {
        "slot_list": ["Disease"],
        "slot_values": None,
        # "cql_template": [],
        "cql_L": "",
        "cql_M": [],
        "cql_R": "",
        "reply_template": "'{disease}'的'{role}'包括:",
        "ask_template": "您问的是 '{Disease}' 的定义吗？",
        "intent_strategy": "",
        "deny_response": "很抱歉没有理解你的意思呢~"
    }
    return template


def load_semantic_slot(intent2pre_path):
    S = {}
    with open(intent2pre_path, "r", encoding="utf8") as f:
        intent2pre = json.load(f)
        for k in intent2pre.keys():
            template = get_template()
            L = "MATCH(p:疾病)-[r:{relation}]->(q) WHERE p.name='{Disease}' "
            M = ["and r.role='{roles}'".format(roles=role) for role in intent2pre[k]]
            R = " RETURN p.name, r.role, q.name"
            # cql_list = [L + M.format(roles=role) + R for role in intent2pre[k]]

            # print(cql_list)
            template["cql_L"] = L
            template["cql_M"] = M
            template["cql_R"] = R
            S[k] = template
    return S


# load_semantic_slot(intent2pre_path="./knowledge_graph/intent2pre.jsonl")
# load_intent2pre("./knowledge_graph/intent2pre.jsonl")
class CONFIG:
    def __init__(self):
        self.semantic_slot = load_semantic_slot(os.path.join(script_path, "./knowledge_graph/intent2pre.jsonl"))
        self.semantic_slot["unrecognized"] = {
            "slot_values": None,
            "replay_answer": "非常抱歉，我还不知道如何回答您，我正在努力学习中~",
        }
        self.intent_threshold_config = {
            "accept":0.4,
            "deny":0.2
        }
        self.default_answer = """抱歉我还不知道回答你这个问题\n
                    你可以问我一些有关疾病的\n
                    注意事项、疾病描述、治疗方法、病因分析、病情诊断\n
                    就医建议等相关问题哦~
                    """

