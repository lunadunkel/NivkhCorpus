import re

from backend.models.corpus import CorpusConfig

# Поле, Поле=Значение или Поле=(a|b)
_PAIR = re.compile(r"([^\s()|&=]+)(?:\s*=\s*(?:\(([^()]*)\)|([^\s()|&=]+)))?")
# то, что может стоять между парами
_GLUE = re.compile(r"[\s()|&]*")


def _checkbox_values(corpus: CorpusConfig) -> dict[str, list[str]]:
    """name чекбокса -> его значения, в порядке YAML."""
    out: dict[str, list[str]] = {}
    for block in corpus.grammar:
        for value in block.values:
            out.setdefault(value.name(block.id), []).append(value.value)
    return out


def _pick(name: str, options, what: str) -> str:
    """Точное совпадение, иначе единственное без учёта регистра: dat -> Dat."""
    if name in options:
        return name
    found = [option for option in options if option.lower() == name.lower()]
    if len(found) == 1:
        return found[0]
    raise ValueError(f"{what} «{name}»")


def text_to_checkboxes(text: str, corpus: CorpusConfig) -> dict[str, list[str]]:
    """Строка -> {name чекбокса: значения}. Пустая строка -> ничего не отмечено."""
    boxes = _checkbox_values(corpus)
    person = corpus.search.person_object
    toggle_by_path = {path: toggle for toggle, path in person.paths.items()} if person else {}

    checked: dict[str, list[str]] = {}

    def tick(name: str, raw: str) -> None:
        value = _pick(raw, boxes[name], f"у {name} нет значения")
        if value not in checked.setdefault(name, []):
            checked[name].append(value)

    pos = 0
    while True:
        matchText = _GLUE.match(text, pos)
        if matchText is not None:
            pos = matchText.end()
        if pos == len(text):
            # значения в порядке YAML, как их отдаёт форма: Case=(Dat|Loc) -> Case=(Loc|Dat)
            return {name: [v for v in boxes[name] if v in values] for name, values in checked.items()}

        pair = _PAIR.match(text, pos)
        if pair is None:
            raise ValueError(f"Неправильный regex «{text[pos:pos + 20]}»; признак пишется как Поле=Значение")
        pos = pair.end()

        name = _pick(pair.group(1), boxes.keys() | toggle_by_path.keys(), "нет признака")
        if pair.group(2) is not None:
            values = [v.strip() for v in pair.group(2).split("|") if v.strip()]
        elif pair.group(3) is not None:
            values = [pair.group(3)]
        else:
            values = []

        if name in toggle_by_path:
            # Person[clobj]=1: переключатель Obj, а цифра идёт в лицо объекта
            toggle = toggle_by_path[name]
            tick(toggle, boxes[toggle][0])
            for value in values:
                if person is not None:
                    tick(person.field, value)
            continue

        if not values:
            if len(boxes[name]) != 1:
                # Пользователь видит: «у Case нужно указать значение: Case=…»
                raise ValueError(f"Для {name} нужно указать значение: {name}=…")
            values = boxes[name]
        for value in values:
            tick(name, value)