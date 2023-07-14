import json
import os
import sys

script_path = os.path.dirname(os.path.abspath(__file__))
ie_path = os.path.join(script_path, "../ie")
ir_path = os.path.join(script_path, "../ir/knowledge_graph")
sys.path.append(ie_path)
sys.path.append(ir_path)
sys.path.append(script_path)

from globalpoint_re_io import MedicalSPO
from books.graduate.ir.knowledge_graph.kg import MedicalExtractor


class Interface:
    def __init__(self):
        self.medical = MedicalSPO()
        self.graph = MedicalExtractor()

    def transfer_text_to_triples(self, text, output_path):
        # 将text作为输入，输出triples
        spocs = []
        if isinstance(text, list):
            for item in text:
                spocs.extend(self.medical.extract_spoes(text=item))
        else:
            spocs = self.medical.extract_spoes(text=text)
        with open(output_path, "w", encoding="utf8") as f:
            L = []
            for tuples in spocs:
                D = {
                    "subject": tuples[0],
                    "predicate": tuples[1],
                    "object": tuples[2]
                }
                L.append(D)
            json.dump(L, f, ensure_ascii=False, indent=1)
        return L

    def save_triple(self, triples_path):
        # 将输出的triples存储在数据库中
        if isinstance(triples_path, str):
            self.graph.extract_triples(triples_path)

    def clear(self):
        self.graph.clear()

# inter = Interface()
# inter.transfer_text_to_triples("心脏病是由过度劳累导致的", "./local.json")
# i = 0