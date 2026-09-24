"""Словари грамматических категорий языка"""

POS = {
    "PROPN", "NOUN", "VERB", "ADP", "PRON", "ADJ", 
    "NUM", "CLASS", "DET", "ADV", "INTJ", 
    "AUX", "CCONJ", "PART", "SCONJ"}

CASES = {
    "GEN": "Case=Gen", 
    "ACC": "Case=Acc",   
    "ABL": "Case=Abl",
    "LOC": "Case=Loc",
    "DAT": "Case=Dat",
    "O": "Case=Obl",
    "INSTR": "Case=Ins",
    "ABE": "Case=Abe",
    "COMP": "Degree=Cmp"
}

    # "VRB": "VerbType=Denom|POS=Verb",
    # "ABSTR": "NounType=AbstrNoun|POS=Noun",
    # "ACTOR": 'SemanticLabel=Agent'

PSOR = {
    
}

NUMBER = {
    "SG": "Number=Sing",
    "PL": "Number=Plur",
}

PERSON = {
    "1": "Person=1",
    "2": "Person=2",
    "3": "Person=3",
}

ADJ = {
    'DIM': "Degree=Dim",
    "ATR": "POS=Adj",
    "ADV": "POS=Adv",
}

NUM = {
    "ORD": "NumType=Ord",
    "COL": "NumType=Sets",
    "DISTR": "NumType=Dist",
}

ASPECT = {
    "ANT": "Aspect=Ant",   # антериор
    "SIM": "Aspect=Sim",   # симултанеус
    "IPFV": "Aspect=Imp",
    "HAB": "Aspect=Hab"
}

TENSE = {
    "PRS": "Tense=Pres",    
    "PST": "Tense=Past",
    "FUT": "Tense=Fut",
}

VERBFORM = {
    "INF": "VerbForm=Inf",
    "CONV": "VerbForm=Conv",    
    "PTCP": "VerbForm=Part", 
    "ST": 'VerbForm=Stat',
    "NMN": "VerbForm=Vnoun|POS=Noun",
}

VOICE = {
    "REFL": "Reflex=Yes",     # рефлексив
    "REC": "Reciprocal=Yes", # реципрок
    "CAUS": "Voice=Caus",     # каузатив
    "PASS": "Voice=Pass",     # пассив
    "NEG": "Polarity=Neg",
}

MOOD = {
    "OPT": "Mood=Opt",       # оптатив
    "HORT": "Mood=Hort",      # гортатив
    "COND": "Mood=Cnd",
    "IMP": "Mood=Imp",
    "POT": "Mood=Pot",

    "FOC": "Focus=Yes",
    "Q": "PartType=Int|POS=Part",
    "EP": "Morph=Epenthetic",
}