"""Словари грамматических категорий языка"""

POS = {
    "NOUN", "VERB", "NUM", "CLASS",
    "Q", "ADV", "PROPN", "PRON", "DISC"}

CASES = {
    "ABS": "Case=Abs",
    "ABL": "Case=Abl",
    "PERL": "Case=Per",
    "LOC": "Case=Loc",
    "DAT": "Case=Dat",
    "INST": "Case=Ins",
    "VOC": "Case=Voc",
    "CAUSEE": "Case=Cau",
    "COM": "Case=Com",
    "COMP": "Case=Cmp",
    "LIM": "Case=Lim",
    "REP": "Case=Rep"
}

VERBFORM = {
    "CONV": "VerbForm=Conv",
    "NMN": "VerbForm=Vnoun",
    "ATR": "VerbForm=Part",
}

NUMBER = {
    "SG": "Number=Sing",
    "DU": "Number=Dual",
    "PL": "Number=Plur",
}

PERSON = {
    "1": "Person=1",
    "2": "Person=2",
    "3": "Person=3",
}

MOOD = {
    "IND": "Mood=Ind",
    "DES": "Mood=Des",
    "IMP": "Mood=Imp",
    "COND": "Mood=Cnd",
    "HORT": "Mood=Hort",
    "JUSS": "Mood=Jus",
    "PROB": "Mood=Prob",
    "PROH": "Mood=Proh",
    "ISP": "Mood=Indir",
    "SUBJ": "Mood=Subj",
}

EVIDENT = {
    "EVID": "Evident=Nfh",
}

CLUSIVITY = {
    "INCL": "Clusivity=In",
    "EXCL" : "Clusivity=Ex"
}

VOICE = {
    "CAUS": "Voice=Caus"
}

DEFINITE = {
    "INDEF": "Definite=Ind",
    "ANY": "Definite=Ind"
}

ASPECT = {
    "PROG": "Aspect=Prog",
    "ANT": "Aspect=Ant",
    "ITER": "Aspect=Iter",
    "USIT": "Aspect=Usit",
    "RES": "Aspect=Res",
    "COMPL": "Aspect=Compl",
    "SIM": "Aspect=Sim",
    "AVERT": "Aspect=Avert",
    "HAB": "Aspect=Hab",
    "MULT": "Aspect=Mult"
}

POLARITY = {
    "NEG": "Polarity=Neg"
}

TENSE = {
    "FUT": "Tense=Fut",
    "Pres_Aor": "Tense=Pres_Aor"
}

DEGREE = {
    "DIM": "Degree=Dim"
}

MISC_VALUES = {
    "CL": "Classifier=Yes",
    "PRED": "Predicative=Yes",
    "FOC": "Focus=Yes",
    "EMPH": "Emphatic=Yes",
    "QU": "Question=Yes",
    "COORD": "Coordinating=Yes",
    "REFL": "Reflex=Yes",
    "REC": "Reciprocal=Yes",
    "CONC": "Conces=Yes",
    "ADD": "Add=Yes",

    "A" : "NounType=Agent",
    "L" : "NounType=Locat",
    "P" : "NounType=Proc",
    "I" : "NounType=Ing",
    "VRB" : "NounType=Deverb",
    "COLL" : "NumType=Collective",
    
    "AUX" : "VerbType=Aux",

}
