morphdict = {
  # Падежи
      "GEN" : "Case=Gen", 
      "ACC" : "Case=Acc",   
      "ABL" : "Case=Abl",
      "LOC" : "Case=Loc",
      "DAT" : "Case=Dat",
      "O"   : "Case=Obl",
      "INSTR" : "Case=Ins",
      "ABE" : "Case=Abe",       # abessive, caritive, privative
      "COMP" : "Degree=Cmp",

      "VRB" : "VerbType=Denom|POS=Verb",
      "ABSTR" : "NounType=AbstrNoun|POS=Noun",
      "ACTOR" : 'SemanticLabel=Agent',

  # Лицо и число
      "SG" : "Number=Sing",
      "PL" : "Number=Plur",

      "1" : "Person=1",
      "2" : "Person=2",
      "3" : "Person=3",

  # Прилагательное
      'DIM' : "Degree=Dim",
      "ATR" : "POS=Adj",
      "ADV" : "POS=Adv",

  # Числительные
      "ORD" : "NumType=Ord",
      "COL" : "NumType=Sets",
      "DISTR" : "NumType=Dist",

  # Аспект
      "ANT"  : "Aspect=Ant",   # антериор
      "SIM"  : "Aspect=Sim",   # симултанеус
      "IPFV" : "Aspect=Imp",
      "HAB"  : "Aspect=Hab",   

  # Время
      "PRS"   : "Tense=Pres",    
      "PST"   : "Tense=Past",
      "FUT"   : "Tense=Fut",

  # Форма глагола
      "INF"  : "VerbForm=Inf",
      "CONV" : "VerbForm=Conv",    
      "PTCP"  : "VerbForm=Part", 
      "ST" : 'VerbForm=Stat',
      "NMN" : "VerbForm=Vnoun|POS=Noun",

  # Залог
      "REFL" : "Reflex=Yes",     # рефлексив
      "REC"  : "Reciprocal=Yes", # реципрок
      "CAUS" : "Voice=Caus",     # каузатив
      "PASS" : "Voice=Pass",     # пассив
      "NEG" : "Polarity=Neg",

  # Наклонение
      "OPT"  : "Mood=Opt",       # оптатив
      "HORT" : "Mood=Hort",      # гортатив
      "COND" : "Mood=Cnd",
      "IMP"   : "Mood=Imp",
      "POT" : "Mood=Pot",

      "FOC"   : "Focus=Yes",
      "Q" : "PartType=Int|POS=Part",
      "EP" : "Morph=Epenthetic",
      }

# Дополнительная конфигурация (опциональная).
# Если параметры ниже отсутствуют в файле конфигурации,
# они получают значения, подходящие для нивхского языка.

# True, если в языке есть прилагательные.
# Если значение этого признака False или он отсутствует в файле конфигурации,
# все прилагательные считаются глаголами.
adjectives = True

# True, если в языке есть префиксы.
# Если значение этого признака False или он отсутствует в файле конфигурации,
# все префиксы считаются проклитиками (точнее, инкорпорированными местоимениями).
prefixes = True

# Список дефолтных значений морфосинтаксических признаков
# для каждой из тех частей речи, для которых они необходимы.
defaults = {
  'NOUN': ['Case=Nom','Number=Sing'],
  'VERB': ['VerbForm=Fin', (['VerbForm=Fin', 'Mood!=Imp'], 'Tense=Pres')]
}

# Если дефолтное значение - tuple из двух элементов, значит,
# первый элемент - это список условий, при которых нужно
# использовать данное дефолтное значение.

# Условия имеют вид Feature=Value или Feature!=Value
# и означают, что значение по умолчанию должно быть приписано при
# наличии или отсутствии определенного значения
# некоторого другого признака, соответственно.

# Порядок приписывания дефолтных значений достаточно важен,
# поскольку автоматически приписанное значение может использоваться
# в условиях для приписывания дефолтных значений последующим признакам.
# Значения приписываются в том порядке, в котором они указаны
# в списке дефолтных значений для данной части речи.

# Например:

# defaults = {
#  'NOUN': ['Case=Nom'],
#  'VERB': ['VerbForm=Fin', (['VerbForm=Fin', 'Mood!=Imp'], 'Tense=Pres')]
# }

# В данном случае время по умолчанию подставляется только
# для финитных словоформ, у которых наклонение не является
# императивом (или совсем не указано).

# Заметим, что финитность приписывается автоматически
# и поэтому должна идти в списке перед временем.
