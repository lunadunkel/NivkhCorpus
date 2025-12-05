import os
import re
import csv
import json
import pandas as pd

class CSVConverter():
    def __init__(self, path):
        self.path = path
        self.convert_to_json()
    
    def convert_to_json(self):
        rows = []
        with open(self.path, 'r') as file:
            reader = csv.reader(file, delimiter="\t")
            for row in reader:
                rows.append(row)
            max_len = max(len(r) for r in rows)
        cleaned = [r + [str(n) for n in range(max_len - len(r))] for r in rows]
        df = pd.DataFrame(cleaned[1:], columns=cleaned[0])
        final_data = []
        if len(df) != 0:
            texts = df['text']
            translations = list(df['rus'])
            sentences = []
            indices = df.loc[:, '1'::3]
            for num, txt in enumerate(texts):
                selected_words = [int(x) for x in list(indices.loc[num])]
                txt = re.sub(r'\[.*\] ', '', txt).capitalize()
                sent = [(lambda num, x: '<strong>' + x + '</strong>' if num in selected_words else x)(num+1, x) 
                                for num, x in enumerate(txt.split(' '))]
                sent = ' '.join(sent)
                sentences.append(sent)
            final_data = [{"id": num+1,
                            "name": "Неизвестный текст",
                            "author": "Неизвестный автор",
                            "text": sent,
                            "translation": trans} for num, (sent, trans) in enumerate(zip(sentences, translations))]
        with open("output.json", 'w') as file:
            file.write(json.dumps(final_data, ensure_ascii=False))