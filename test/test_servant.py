from webkov.servant import is_voice, is_action, is_heading, is_target


def test_is_voice():
    voices = [
        "LADY MONTAGUE",
        "Nurse",
        "NURSE",
        "ROMEO   ",
        "Lady Capulet",
        "First Citizen",
        "Servant",
    ]
    for voice in voices:
        assert is_voice(voice + "\n")


def test_is_not_voice():
    trash = [
        "literal garbage",
        "He dies",
        "TIBALT you jerk",
        "ACT II",
        "PROLOGUE",
        "",
    ]
    for garbage in trash:
        assert not is_voice(garbage + "\n")


def test_is_action():
    actions = [
        "Enter ROMEO",
        "Dies",
        "dies",
        "They fight, with some extra text",
        "Laying, he calls out",
    ]
    for act in actions:
        assert is_action(act + "\n")


def test_is_not_action():
    inactions = [
        "Hey man!",
        "Sweet flower, with flowers thy bridal bed I strew,--",
        "Yeah, no thanks",
    ]
    for voice in inactions:
        assert not is_action(voice + "\n")


def test_is_heading():
    titles = [
        "SCENE I. Verona. A public place.",
        "PROLOGUE",
    ]
    for title in titles:
        assert is_heading(title + "\n")


def test_is_target():
    # we want to recognize them, and we want to pull out the
    # relevant text
    targets = [
        # the line
        ("[Aside to GREGORY] Is the law of our side, if I say",
         # the relevant text
         "Is the law of our side, if I say"),
    ]
    for target in targets:
        match = is_target(target[0])
        return match and match.groups(0) == target[1]
