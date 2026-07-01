import json

with open("words_aggregated.json", "r", encoding="utf-8") as f:
    dictionary = json.load(f)

new_dict = []
for x, y in dictionary.items():
    new_dict.append({'lemma': x, 'translation': y})

with open("words_aggregated.json", "w", encoding="utf-8") as f:
    json.dump(new_dict, f, ensure_ascii=False, indent=4)