from contextlib import contextmanager
import re
from nltk import word_tokenize
import time


@contextmanager
def rj():
    out = open("./rj.txt", 'r', encoding='utf-8')
    yield out
    out.close()


# if it's just the name, it's considered a designation that the
# character is speaking

# certain lines start with targets. They are surrounded by brackets,
# targets should be kept, but stripped of the match:
# [Aside] Villain and he be many miles asunder.--
TARGETS = [
    "aside",
    "within",
]

# capture the end, we don't care about the action.
TARGETS_RE_MAP = [
    re.compile(r"^\[{}.*]\s*(.*)$".format(target)) for target in TARGETS]


def is_target(line):
    # go down the list of targets until you find one.
    # a simpler implementation might be to ignore all targets, and
    # only match brackets.
    for reg in TARGETS_RE_MAP:
        maybe = reg.match(line)
        if maybe:
            return maybe


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


# any line starting with these indicates non-dialog. Ignore this line
# and any lines after it, until a character speaks.
HEADINGS = set([
    "PROLOGUE",
    "SCENE",
    "ACT",
])


def is_heading(line):
    first_word = word_tokenize(line)[0]
    return first_word in HEADINGS


ACTIONS = set([
    "enter",
    "re-enter",
    "retiring",
    "retires",
    "dies",  # :(
    "laying",
    "advances",
    "falls",
    "singing",  # mercutio does this once. Only occurence
    "exeunt",
    "exit",
    "drawing",  # twice, both actions.
])


def is_action(line):
    words = word_tokenize(line)
    # since there's a ton of these, we're going to just take the first
    # word, downcase it, and see if it's in ACTIONS.
    if words[0].lower() in ACTIONS:
        return True
    elif len(words) >= 2:
        return words[:2] == ["They", "fight"]
    # return words[0].lower() in ACTIONS or words[:2] == ["They", "fight"]


is_whitespace_reg = re.compile(r"^\s*$")


def is_whitespace(line):
    return is_whitespace_reg.match(line)


# ==================== DEMO STUFF ====================


def loop(skip=0):
    # is there a 'start the loop' construct in python?
    lines = _pull()
    for hop in range(skip):
        next(lines)
    count = skip
    for line in lines:
        out = _prompt()
        count += 1
        if out == 'q':
            break
        else:
            print(_result(_annotate(line), count, line))


def lazy_loop(skip=0):
    # unimport sleep when this is over
    lines = _pull()
    for hop in range(skip):
        next(lines)
    count = skip
    for line in lines:
        print(_result(_annotate(line), count, line))
        count += 1
        time.sleep(0.8)


def _result(annotate, count, line):
    return "{}: {} {}".format(annotate, count, line)


def _pull():
    with rj() as rjf:
        # initialize the loop
        line = rjf.readline()
        # while line isn't the empty string
        while line:
            # keep reading lines until we get visible text
            if not is_whitespace(line):
                yield line
            line = rjf.readline()



def _prompt():
    while True:
        out = input("Continue or quit? (c/q): ")
        if out in ['c', 'q']:
            return out


def _annotate(line):
    if is_heading(line):
        return "L"
    if is_action(line):
        return "A"
    if is_voice(line):
        return "V"
    else:
        return "S"
