from webkov.servant import is_voice, is_action, is_heading, TRAILING_PUNCT, is_target


def _test_splitter(cases):
    raw = [line.split()
           for line in cases]
    out = []
    for tokenized in raw:
        out.append([tok.rstrip(TRAILING_PUNCT) for tok in tokenized])
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
    for voice in _test_splitter(voices):
        assert is_voice(voice)


def test_is_not_voice():
    trash = [
        "literal garbage",
        "He dies",
        "TIBALT you jerk",
        "ACT II",
        "PROLOGUE",
        "",
    ]
    for garbage in _test_splitter(trash):
        assert not is_voice(garbage)


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
    for act in _test_splitter(actions):
        assert is_action(act)


def test_is_not_action():
    inactions = [
        "Hey man!",
        "Sweet flower, with flowers thy bridal bed I strew,--",
        "Yeah, no thanks",
    ]
    for inact in _test_splitter(inactions):
        assert not is_action(inact)


def test_is_heading():
    titles = [
        "SCENE I. Verona. A public place.",
        "PROLOGUE",
    ]
    for title in _test_splitter(titles):
        assert is_heading(title)


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
        match = is_target(target[0])
        return match and match.groups()[0] == target[1]
