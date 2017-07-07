import webkov.servant as wks
from collections import deque, defaultdict


def _splitter(cases):
    raw = [line.split()
           for line in cases]
    out = []
    for tokenized in raw:
        out.append([tok.rstrip(wks.TRAILING_PUNCT) for tok in tokenized])
    return out


def test_is_voice():
    voices = [
        "LADY MONTAGUE",
        "Nurse",
        "NURSE",
        "Lady Capulet",
        "First Citizen",
        "Servant",
    ]
    for voice in _splitter(voices):
        assert wks.is_voice(voice)


def test_is_not_voice():
    trash = [
        "literal garbage",
        "He dies",
        "TIBALT you jerk",
        "ACT II",
        "PROLOGUE",
        "",
    ]
    for garbage in _splitter(trash):
        assert not wks.is_voice(garbage)


def test_is_action():
    actions = [
        "Enter ROMEO",
        "Dies",
        "dies",
        "They fight, with some extra text",
        "Laying, he calls out",
    ]
    # the alternative to this double nested list comprehension
    # is a massive amount of pain each time I want to add some new
    # test case
    for act in _splitter(actions):
        assert wks.is_action(act)


def test_is_not_action():
    inactions = [
        "Hey man!",
        "Sweet flower, with flowers thy bridal bed I strew,--",
        "Yeah, no thanks",
    ]
    for inact in _splitter(inactions):
        assert not wks.is_action(inact)


def test_is_heading():
    titles = [
        "SCENE I. Verona. A public place.",
        "PROLOGUE",
    ]
    for title in _splitter(titles):
        assert wks.is_heading(title)


def test_is_not_heading():
    pass


def test_is_target():
    # we want to recognize them, and we want to pull out the
    # relevant text. This occurs before tokenization
    targets = [
        # the line
        ("[Aside to GREGORY] Is the law of our side, if I say",
         # the relevant text
         "Is the law of our side, if I say"),
        # the line
        ("    [Aside to GREGORY] Is the law of our side, if I say",
         # the relevant text
         "Is the law of our side, if I say"),
    ]
    for target in targets:
        match = wks.is_target(target[0])
        assert match and match.groups()[0] == target[1]


def test_maybe_split_token():
    tokens = [
        ["neighbour-stained", ["neighbour-stained"]],
        ['steel,--', ["steel", ",",  "-", "-"]],
        ['tyrant:', ["tyrant", ":"]],
        ['them', ['them']],
        ['Gregory,', ['Gregory', ',']],
        ['comes?', ['comes', '?']],
    ]
    for token, split in tokens:
        assert wks.maybe_split_token(token) == split


def test_tokenize():
    # lines mapped to their tokenizations
    lines = [
        ["To move is to stir; and to be valiant is to stand:",
         ["To", "move", "is", "to", "stir", ";", "and", "to", "be",
          "valiant", "is", "to", "stand", ":"]],
        ["'Tis all one, I will show myself a tyrant: when I",
         ["'Tis", "all", "one", ",", "I", "will", "show", "myself",
          "a", "tyrant", ":", "when", "I"]],
        ["Profaners of this neighbour-stained steel,--",
         ["Profaners", "of", "this", "neighbour-stained",
          "steel", ",", "-", "-"]]]
    for line, tokenization in lines:
        assert wks.tokenize(line) == tokenization



def test_sanity_check():
    '''
    This is surprising behavior that may or may not change.
    Thankfully it's documented as of 3.5.3
    '''
    a = defaultdict(int)
    a["words!"] += 1
    b = {"words!": 1}
    assert a == b


def _dd_dd_int():
    "Why do defaultdicts make me feel so gross?"
    return defaultdict(wks._python_lambdas_make_me_sad)


def _chain_map_gen(string, chain_map, order=1):
    mapper = {
        1: wks.first_order_chain_map,
        2: wks.second_order_chain_map,
        }[order]
    hard_coded = _dd_dd_int()
    hard_coded.update(chain_map)
    return [mapper(deque(wks.tokenize(string))),
            hard_coded]


def test_first_order_chain_map():
    maps = [
        # I assure you this is less verbose than before.
        _chain_map_gen("you and you need to.",
                       {
                           "you": {
                               "and": 1,
                               "need": 1,
                           },
                           "and": {
                               "you": 1,
                           },
                           "need": {
                               "to": 1,
                           },
                           "to": {
                               ".": 1,
                           },
                       })
        ]
    for chain_map, hard_coded in maps:
        assert chain_map == hard_coded


def test_second_order_chain_map():
    maps = [
        _chain_map_gen(
            "this morning it would be great if this morning be great.",
            {
                ("this", "morning"): {
                    "it": 1,
                    "be": 1,
                },
                ("be", "great"): {
                    "if": 1,
                    ".": 1,
                }
            },
            order=2)
        ]
    for chain_map, hard_coded in maps:
        assert hard_coded
