import json
dict = [
    {
        "f1": 1,
        "pre": 1,
        "re": 1
    }
]

with open("file.json", "w", encoding="utf8") as f:
    json.dump(dict, f)