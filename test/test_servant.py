import webkov.parser as wkp
import webkov.servant as wks
from collections import deque, defaultdict, Counter


def _splitter(cases):
    raw = [line.split()
           for line in cases]
    out = []
    for tokenized in raw:
        out.append([tok.rstrip(wkp.TRAILING_PUNCT) for tok in tokenized])
    return out


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
        match = wkp.is_target(target[0])
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
        assert wkp.maybe_split_token(token) == split


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
        assert wkp.tokenize(line) == tokenization



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
    return defaultdict(Counter)


def _chain_map_gen(string, chain_map, order=1):
    hard_coded = _dd_dd_int()
    hard_coded.update(chain_map)
    return [wks.chain_from_deq(deque(wkp.tokenize(string)), order=order),
            hard_coded]


def test_first_order_chain_map():
    maps = [
        # I assure you this is less verbose than before.
        _chain_map_gen("you and you need to.",
                       {
                           ("you",): {
                               "and": 1,
                               "need": 1,
                           },
                           ("and",): {
                               "you": 1,
                           },
                           ("need",): {
                               "to": 1,
                           },
                           ("to",): {
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
