import os
from backend.core.config import EXTRACTOR_DIR
from backend.dictionaries import MISC, QUERY2DB

class SubexampleItem:
    def __init__(self, json_data, literal, name, language):
            self.participant = chr(literal)
            self.slot_name = name
            self.order = next((json_data[key] for key in json_data if key.startswith('search-order')), None)
            input_word_slot = next(json_data[key] for key in json_data if key.startswith('input_word'))
            self.input_word = input_word_slot if input_word_slot != '' else None
            search_type_slot = next(json_data[key] for key in json_data if key.startswith('search-type'))
            self.search_type = (
                'LexNonHead' if language == 'nivkh' and search_type_slot == 'lemma' else
                'RussianLexNonHead' if language == 'russian' and search_type_slot == 'lemma' else
                'WordformNonHead' if language == 'nivkh' and search_type_slot == 'token' else
                'RussianWordform' if language == 'russian' and search_type_slot == 'token' else
                None
            )
            self.ConstituentType = None
            self.Morph = []
            self.load_item_yaml(json_data, language)


    def load_item_yaml(self, json_data, language):      
        print(json_data)  
        for key, db_key in QUERY2DB.items():
            # итерация по элементам грамматических признаков
            if value := json_data.get(key, None):
                if isinstance(value, str):
                    value = [value]

                match key:
                    case 'pos[]':
                        self.Morph += [('|').join(value)]
                    case 'misc[]' | 'verb[]':
                        if dictionary := MISC.get(key, None):
                            self.Morph += [('|').join([dictionary[x] for x in value])]
                    case _:
                        if isinstance(db_key, list):
                            query = []
                            for k in db_key:
                                query.extend([f'{k}={x}' for x in value])
                            self.Morph += [('|').join(query)]
                        else:
                            self.Morph += [('|').join([f'{db_key}={x}' for x in value])]

class JsonToYaml:
    def __init__(self, json_data):
        self.language = None
        self.Morph = None
        self.output = self.print_items(json_data)

    def __str__(self):
        return self.output
  
    def print_items(self, json_data):
        id = 1
        literal_code = 65
        language = json_data[0]['language-select']

        items = '        Items:\n'
        header = '''ExampleName: SampleExample
        
Priority: 1
        
SubExamples:
        
    - SubExample:            
        Name: SoleSubExample\n'''

        participants = []
        orders = []

        for frame in json_data:
            item = SubexampleItem(frame, literal_code, f"Element{id}", language)
            participants += [item.slot_name]
            items = items + f'''          - {item.participant}: {item.slot_name}\n'''
            items = items + (f'''            Morph: {", ".join(item.Morph)}\n''' if item.Morph else "")
            if item.search_type and item.input_word:
                items = items + f'''            {item.search_type}: {item.input_word}\n'''
                        
            if item.order is not None:
              if item.order == 'after':
                orders.append((chr(literal_code-1), chr(literal_code)))
              else:
                orders.append((chr(literal_code), chr(literal_code-1)))

            id += 1
            literal_code += 1

        printed_participants = f'''\n        Participants:
          - Obligatory: {", ".join(participants)}\n\n'''

        orders_str = "\n\n".join([f'- Order: {x[0]}, {x[1]}' for x in orders])
        printed_orders = f'''\n        Constraints:
          {orders_str}''' if orders else ""

        output_yaml = header + printed_participants + items + printed_orders
        temp_file_path = os.path.join(EXTRACTOR_DIR, 'Rules', '24')
        temp_file_path = os.path.normpath(temp_file_path)

        os.makedirs(temp_file_path, exist_ok=True)
        dir_to_write = os.path.join(temp_file_path, 'temp.yaml')
        with open(dir_to_write, 'w', encoding='utf-8') as f:
            f.write(output_yaml)
        
        return output_yaml

