import json
import os
import sys

script_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_path)
from py2neo import Graph
import pandas as pd
import numpy as np
from tqdm import tqdm


class MedicalExtractor(object):
    def __init__(self):
        super(MedicalExtractor, self).__init__()
        self.graph = Graph(
            "bolt://localhost:7687",
        )

        self.disease_infos = []  # 疾病
        self.symptoms = [] # 临床表现
        self.bodies = [] # 身体部位
        self.departments = [] # 科室
        self.drugs = [] # 药物
        self.equipments = [] # 医疗设备 #基本无用
        self.items = [] # 医学检验项目 # 基本无用
        self.micos = [] # 微生物类 # 基本无用
        self.procedures = [] # 医疗程序
        self.reason = [] # 新增-社会学-病因分析
        self.illustration = [] # 新增-流行病学-疾病表述
        self.other = [] # 新增-其他

        # 构建节点实体关系
        self.rels_cure_methods = [] # 治疗方案
        self.rels_outcome_illustrations = [] # 后果表述
        self.rels_pay_attentions = [] # 注意事项
        self.rels_medical_advices = [] # 就医建议
        self.rels_target_analysis = [] # 指标解读
        self.rels_medical_fees = [] # 医疗费用
        self.rels_drug_functions = [] # 功效作用
        self.rels_medical_illustrations = [] # 疾病描述
        self.rels_medical_analysis = [] # 病情诊断
        self.rels_medical_reasons = [] # 病因分析
        with open(os.path.join(script_path, "schema.json"), "r", encoding="utf8") as f:
            self.voc = json.load(f)
        with open(os.path.join(script_path, "intent2pre.json"), "r", encoding="utf8") as f:
            self.voc2rel = json.load(f)

    def extract_triples(self, data_path, is_save=False):
        with open(data_path, "r", encoding="utf8") as f:
            data = json.load(f)
            for line in tqdm(data, ncols=80):
                data_json = line
                S = data_json["subject"]
                predicate = data_json["predicate"]
                O = data_json["object"]
                subject_type = self.voc[predicate]["subject_type"]
                object_type = self.voc[predicate]["object_type"]
                if subject_type == "疾病":
                    self.disease_infos.append(S)
                    self.other.append(O)
                    rel_type = self.voc2rel[predicate]
                    tuples = {
                        "head": S,
                        "head_type": subject_type,
                        "predicate": predicate,
                        "relation": rel_type,
                        "tail": O,
                        "tail_type": object_type
                    }
                    if rel_type == "疾病表述":
                        self.rels_medical_illustrations.append(tuples)
                    elif rel_type == "注意事项":
                        self.rels_pay_attentions.append(tuples)
                    elif rel_type == "治疗方案":
                        self.rels_cure_methods.append(tuples)
                    elif rel_type == "后果表述":
                        self.rels_outcome_illustrations.append(tuples)
                    elif rel_type == "就医建议":
                        self.rels_medical_advices.append(tuples)
                    elif rel_type == "指标解读":
                        self.rels_target_analysis.append(tuples)
                    elif rel_type == "医疗费用":
                        self.rels_medical_fees.append(tuples)
                    elif rel_type == "功效作用":
                        self.rels_drug_functions.append(tuples)
                    elif rel_type == "病情诊断":
                        self.rels_medical_analysis.append(tuples)
                    elif rel_type == "病因分析":
                        self.rels_medical_reasons.append(tuples)
                else:
                    print("The type is " + subject_type + ", and will be ignored")
                    pass

        self.create_entitys()
        self.create_relations()
        self.clear()

    def write_nodes(self, entitys, entity_type):
        """
        写入节点
        :param entitys:
        :param entity_type:
        :return:
        """
        print("写入 {0} 实体".format(entity_type))
        for node in tqdm(set(entitys), ncols=80):
            cql = """MERGE(n:{label}{{name:'{entity_name}'}})""".format(
                label=entity_type, entity_name=node.replace("'", ""))
            try:
                self.graph.run(cql)
            except Exception as e:
                print(e)
                print(cql)

    def write_edges(self, triples, head_type="", tail_type=""):
        """
        写入边
        :param triples:
        :param head_type:
        :param tail_type:
        :return:
        """
        # print("写入关系:" + str(triples[0][1]))
        for item in tqdm(triples, ncols=80):
            # print(item)
            head_type = item["head_type"]
            tail_type = item["tail_type"]
            head = item["head"]
            tail = item["tail"]
            relation = item["relation"]
            predicate = item["predicate"]
            cql = """MATCH(p:{head_type}),(q:{tail_type}) WHERE p.name='{head}' AND q.name='{tail}'
                    MERGE (p)-[r:{relation}{{role: '{predicate}'}}]->(q)""".format(
                head_type=head_type, tail_type="其他", head=head.replace("'", ""),
                tail=tail.replace("'", ""), relation=relation, predicate=predicate.replace("'", ""))
            try:
                self.graph.run(cql)
                print(cql)
            except Exception as e:
                print(e)
                print(cql)

    def create_entitys(self):
        """
        创建实体
        :return:
        """
        self.write_nodes(self.disease_infos, "疾病")
        self.write_nodes(self.symptoms, "临床表现")
        self.write_nodes(self.bodies, "身体部位")
        self.write_nodes(self.departments, "科室")
        self.write_nodes(self.drugs, "药物")
        self.write_nodes(self.equipments, "医疗设备")
        self.write_nodes(self.items, "医学检验项目")
        self.write_nodes(self.micos, "微生物类")
        self.write_nodes(self.procedures, "医疗程序")
        self.write_nodes(self.reason, "社会学病因分析")
        self.write_nodes(self.illustration, "流行病学疾病表述")
        self.write_nodes(self.other, "其他")

    def create_relations(self):
        """
        创建关系
        :return:
        """
        self.write_edges(self.rels_cure_methods, "疾病", "其他")
        self.write_edges(self.rels_outcome_illustrations, "疾病", "其他")
        self.write_edges(self.rels_pay_attentions, "疾病", "其他")
        self.write_edges(self.rels_medical_advices, "疾病", "其他")
        self.write_edges(self.rels_target_analysis, "疾病", "其他")
        self.write_edges(self.rels_medical_fees, "疾病", "其他")
        self.write_edges(self.rels_drug_functions, "疾病", "其他")
        self.write_edges(self.rels_medical_illustrations, "疾病", "其他")
        self.write_edges(self.rels_medical_analysis, "疾病", "其他")
        self.write_edges(self.rels_medical_reasons, "疾病", "其他")

    def clear(self):
        self.__init__()


if __name__ == '__main__':
    # path = "medical.json"
    # path = os.path.join(script_path, "../../util/data_hub/CMeIE/filter_CMeIE_train.jsonl")
    extractor = MedicalExtractor()
    # extractor.extract_triples(path)
    # extractor.create_entitys()
    # extractor.create_relations()
    extractor.write_nodes(entitys=["心脏病"],entity_type="疾病")
    extractor.write_nodes(entitys=["过度劳累"], entity_type="其他")
    extractor.write_edges(triples=[
        {
            "head": "心脏病",
            "head_type": "疾病",
            "predicate": "病因",
            "relation": "病因分析",
            "tail": "过度劳累",
            "tail_type": "其他"
        }
    ])
