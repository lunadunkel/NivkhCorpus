import os

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
                'WordformNonHead' if language == 'nivkh' and search_type_slot == 'wordform' else
                'RussianWordform' if language == 'russian' and search_type_slot == 'wordform' else
                None
            )
            self.ConstituentType = None
            self.Morph = []
            self.load_item_yaml(json_data, language)

    def load_item_yaml(self, json_data, language):

        ### ConstituentType ###
        # if 'categoies[]' in json_data:
        #     self.ConstituentType = [('|').join(json_data['categoies[]'])] if type(json_data['categoies[]']) == list else json_data['categoies[]']
        # elif 'categoies' in json_data:
        #     self.ConstituentType = 'NP|VP|NumP|QP|ADVP'
        
        if 'pos[]' in json_data:
            self.Morph += [('|').join(json_data['pos[]'])] if type(json_data['pos[]']) == list else [json_data['pos[]']]
        elif 'pos' in json_data:
            self.Morph += ['NOUN|VERB|NUM|CLASS|Q|ADV|PROPN|PRON|DISC|NONE']

        if 'case[]' in json_data:
            self.Morph += [('|').join([f'Case={x}' for x in json_data['case[]']])] if type(json_data['case[]']) == list else [f"Case={json_data['case[]']}"]
        elif 'case' in json_data:
            self.Morph += ['Case=Abl|Case=Per|Case=Loc|Case=Dat|Case=Ins|Case=Voc|Case=Cau|Case=Com|Case=Cmp|Case=Lim|Case=Rep']

        if 'number[]' in json_data:
            self.Morph += [('|').join([f'Number={x}' for x in json_data['number[]']])] if type(json_data['number[]']) == list else [f"Number={json_data['number[]']}"]
        elif 'number' in json_data:
            self.Morph += ['Number=Sing|Number=Dual|Number=Plur']

        if 'person[]' in json_data:
            self.Morph += [('|').join([f'Person={x}' for x in json_data['person[]']])] if type(json_data['person[]']) == list else [f"Person={json_data['person[]']}"]
        elif 'person' in json_data:
            self.Morph += ['Person=1|Person=2|Person=3']

        if 'mood[]' in json_data:
            self.Morph += [('|').join([f'Mood={x}' for x in json_data['mood[]']])] if type(json_data['mood[]']) == list else [f"Mood={json_data['mood[]']}"]
        elif 'mood' in json_data:
            self.Morph += ['Mood=Ind|Mood=Des|Mood=Imp|Mood=Cnd|Mood=Hort|Mood=Jus|Mood=Prob|Mood=Proh|Mood=Indir|Mood=Subj']

        if 'aspect[]' in json_data:
            self.Morph += [('|').join([f'Aspect={x}' for x in json_data['aspect[]']])] if type(json_data['aspect[]']) == list else [f"Aspect={json_data['aspect[]']}"]
        elif 'aspect' in json_data:
            self.Morph += ['Aspect=Prog|Aspect=Ant|Aspect=Iter|Aspect=Usit|Aspect=Res|Aspect=Compl|Aspect=Sim|Aspect=Avert|Aspect=Hab|Aspect=Mult']

        if 'verbform[]' in json_data:
            self.Morph += [('|').join([f'VerbForm={x}' for x in json_data['verbform[]']])] if type(json_data['verbform[]']) == list else [f"VerbForm={json_data['verbform[]']}"]
        elif 'verbform' in json_data:
            self.Morph += ['VerbForm=Conv|VerbForm=Vnoun|VerbForm=Part']

        if 'clusivity[]' in json_data:
            self.Morph += [('|').join([f'Clusivity={x}' for x in json_data['clusivity[]']])] if type(json_data['clusivity[]']) == list else [f"Clusivity={json_data['clusivity[]']}"]
        elif 'clusivity' in json_data:
            self.clusivity += ['Clusivity=In|Clusivity=Ex']

        if 'nountype[]' in json_data:
            self.Morph += [('|').join([f'NounType={x}' for x in json_data['nountype[]']])] if type(json_data['nountype[]']) == list else [f"NounType={json_data['nountype[]']}"]
        elif 'nountype' in json_data:
            self.Morph += ['NounType=Agent|NounType=Locat|NounType=Proc|NounType=Ing|NounType=Deverb|NumType=Collective']

        additional_grammar_dict = {
                            "nfh": "Evident=Nfh",
                            "caus": "Voice=Caus",
                            "ind": "Definite=Ind",
                            "neg": "Polarity=Neg",
                            "fut": "Tense=Fut",
                            "dim": "Degree=Dim",
                            "class": "Classifier=Yes",
                            "pred": "Predicative=Yes",
                            "foc": "Focus=Yes",
                            "emph": "Emphatic=Yes",
                            "qu": "Question=Yes",
                            "coord": "Coordinating=Yes",
                            "refl": "Reflex=Yes",
                            "rec": "Reciprocal=Yes",
                            "conces": "Conces=Yes",
                            "add": "Add=Yes",
                            "coll": "NumType=Collective",
                            "aux": "VerbType=Aux"
                          }

        if 'additional[]' in json_data:
            self.Morph += [(', ').join([additional_grammar_dict[x] for x in json_data['additional[]']])] if type(json_data['additional[]']) == list else [additional_grammar_dict[json_data['additional[]']]]

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
                orders.append((chr(literal_code), chr(literal_code-1)))
              else:
                orders.append((chr(literal_code-1), chr(literal_code)))

            id += 1
            literal_code += 1

        printed_participants = f'''\n        Participants:
          - Obligatory: {", ".join(participants)}\n\n'''

        orders_str = "\n\n".join([f'- Order: {x[0]}, {x[1]}' for x in orders])
        printed_orders = f'''\n        Constraints:
          {orders_str}''' if orders else ""

        output_yaml = header + printed_participants + items + printed_orders
        script_dir = os.path.dirname(os.path.abspath(__file__))
        temp_file_path = os.path.join(script_dir, '..', 'extractor', 'Rules', '24')
        temp_file_path = os.path.normpath(temp_file_path)

        os.makedirs(temp_file_path, exist_ok=True)
        dir_to_write = os.path.join(temp_file_path, 'temp.yaml')
        with open(dir_to_write, 'w', encoding='utf-8') as f:
            f.write(output_yaml)
        
        return output_yaml

