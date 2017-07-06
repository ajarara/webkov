from webkov.servant import is_voice

def test_is_voice():
    voices = [
        "LADY MONTAGUE",
        "Nurse",
        "NURSE",
        "ROMEO   ",
        "Lady Capulet",
        "First Citizen",
        "Servant",
        ""
    ]
    for voice in voices:
        assert is_voice(voice)

def test_is_not_voice():
    trash = [
        "LITERAL GARBAGE",
        "He dies",
        "TIBALT you jerk",
        "ACT II",
        "PROLOGUE",
    ]
    for garbage in trash:
        assert not is_voice(garbage)
