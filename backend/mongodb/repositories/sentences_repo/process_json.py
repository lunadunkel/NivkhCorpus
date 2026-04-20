import json
import os
from pathlib import Path
from typing import Optional


class Json2MongoProcessing:
    def __init__(self, path: Path, pos_tags: Optional[list] = None):
        """Класс для предобработки json перед загрузкой в БД
        Args:
            path (str): путь к данным json
            pos_tags (list, Optional): пос-теги текстов"""
        self.path = path
        self.pos_tags = pos_tags or ["NOUN", "VERB", "NUM", "CLASS", 
                         "Q", "ADV", "INTJ", "PROPN", "PRON", "X"]
        
    def process_json(self, filename):
        path = os.path.join(self.path, filename)
        with open(path, 'r', encoding='utf8') as file:
            file_data = json.load(file)
        if not isinstance(file_data, list):
            raise Exception("Error: JSON file did not contain a list of documents")
        
        for m in range(len(file_data)):
            tokens = file_data[m]['tokens']
            for pos, tok_set in enumerate(tokens):
                tok_set['idx'] = pos
                new_tagset = {}
                tagsets = tok_set['tagsets']
                if len(tagsets) == 1:
                    tagsets = tagsets[0]
                    for idx, tag in enumerate(tagsets):
                        if '=' in tag:
                            key, val = tag.split('=')
                            if key in ['Number', 'Person']:
                                key += '[subj]'
                            new_tagset[key] = val
                        elif tag in self.pos_tags or idx == 0: 
                            new_tagset['POS'] = tag
                        else:
                            print(tok_set)
                            print('чет другое')
                            print(tag)
                else:
                    print(filename)
                    print('длина не 1')
                    print(tagsets)
                    continue
                file_data[m]['tokens'][pos]['tagsets'] = new_tagset
        return file_data