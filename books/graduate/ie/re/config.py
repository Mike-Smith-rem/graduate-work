import os
import json


def dump_spo(path, output_path):
    data = []
    with open(path, "r", encoding="utf8") as f:
        for line in f.readlines():
            data_json = json.loads(line)
            data_json = data_json["spo_list"]
            for item in data_json:
                S = item["subject"]
                P = item["predicate"]
                O = item["object"]["@value"]
                data.append({"subject": S, "predicate": P, "object": O})
    with open(output_path, "w", encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        

# dump_spo("../../util/data_hub/CMeIE/CMeIE_train.jsonl", "../../util/data_hub/CMeIE/filter_CMeIE_train.jsonl")
