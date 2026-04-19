import os
import re
import csv
import json
import pandas as pd
from backend.core.config import OUTPUT_DIR

import os
import re
import csv
import json
import pandas as pd
from backend.core.config import OUTPUT_DIR


class CSVConverter:
    def __init__(self):
        self.path = os.path.join(OUTPUT_DIR, 'search_result.csv')

    def _safe_int(self, value):
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def convert(self):
        if not os.path.exists(self.path):
            print(f'Файл не найден: {self.path}')
            return []


        
        rows = []
        with open(self.path, 'r', encoding='utf8') as file:
            reader = csv.reader(file, delimiter="\t")
            for row in reader:
                rows.append(row)

        if not rows:
            return []

        # выравниваем строки по длине
        max_len = max(len(r) for r in rows)
        cleaned = [r + [''] * (max_len - len(r)) for r in rows]

        # создаём DataFrame
        df = pd.DataFrame(cleaned[1:], columns=cleaned[0])

        required_cols = ['text', 'rus']
        for col in required_cols:
            if col not in df.columns:
                return []

        texts = df['text'].fillna('')
        translations = df['rus'].fillna('')

        # определяем, где начинаются "индексы"
        start_idx = None
        if 'sent_len' in df.columns:
            start_idx = df.columns.get_loc('sent_len')
        if isinstance(start_idx, int):
            start_idx += 1
        else:
            # fallback — считаем, что первые 8 колонок служебные
            start_idx = 8 if len(df.columns) > 8 else len(df.columns)

        indices_df = df.iloc[:, start_idx:]

        sentences = []

        for row_idx, txt in enumerate(texts):
            try:
                # чистим текст
                txt = re.sub(r'\[.*?-\]\s*', '', txt).strip().capitalize()
                words = txt.split()

                # собираем индексы
                raw_indices = indices_df.iloc[row_idx].tolist()
                selected_words = set()

                for val in raw_indices:
                    num = self._safe_int(val)
                    if num is not None:
                        selected_words.add(num)

                # подсветка слов
                processed = []
                for i, word in enumerate(words, start=1):
                    if i in selected_words:
                        processed.append(f'<strong>{word}</strong>')
                    else:
                        processed.append(word)

                sentences.append(' '.join(processed))

            except Exception as e:
                print(f'Ошибка в строке {row_idx}: {e}')
                sentences.append(txt)

        final_data = []
        for i, (sent, trans) in enumerate(zip(sentences, translations)):
            final_data.append({
                "id": i + 1,
                "title": "Неизвестный текст",
                "author": "Неизвестный автор",
                "text": sent,
                "russian_text": trans
            })

        return final_data