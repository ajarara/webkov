from contextlib import contextmanager
import re
from nltk import word_tokenize


@contextmanager
def rj():
    out = open("./rj.txt", 'r', encoding='utf-8')
    yield out
    out.close()


# any line starting with these indicates non-dialog. Ignore this line
# and any lines after it, until a character speaks.
HEADINGS = set([
    "PROLOGUE",
    "SCENE",
    "ACT",
])

# I wonder what's faster: introducing downcased
# any line starting with these is ignored.
ACTIONS = set([
    "Enter",
    "Re-enter",
    "Retiring",
    "Retires",
    "Dies",  # :(
    "Laying",
    "Advances",
    "Falls",
    "Singing",  # mercutio does this once. Only occurence
    "Exeunt",
    "Exit",
    "Drawing",  # twice, both actions.
    "They fight",
])


# if it's just the name, it's considered a designation that the
# character is speaking

# certain lines start with targets. They are surrounded by brackets,
# targets should be kept, but stripped of the match:
# [Aside] Villain and he be many miles asunder.--
TARGETS = [
    "aside",
    "within",
]

TARGETS_RE_MAP = [r"\[{}]?".format(target) for target in TARGETS]

# this happens twice. I could just ignore the two lines, but that's a
# little brittle, isn't it?
IS_NOISE_REG = re.compile("^[Nn]oise")

TITLES = set([
    "LADY",
    "Lady",
    "First",
    "Second",
    "Third",
    "FRIAR",
])
is_voice_reg = re.compile(r"\A[a-zA-Z]+\s*$")


def is_voice(line):
    words = word_tokenize(line)
    num_words = len(words)
    if num_words == 1:
        word = words[0]
        return word not in HEADINGS and is_voice_reg.match(word)
    elif num_words == 2:
        # maybe:
        title, name = words
        if title in TITLES:
            return is_voice_reg.match(name)
