from contextlib import contextmanager
import re
from collections import deque, defaultdict, Counter


@contextmanager
def rj():
    out = open("./rj.txt", 'r', encoding='utf-8')
    yield out
    out.close()


# Targets are lines like these, with brackets in the front
# [Aside] Villain and he be many miles asunder.--
IS_TARGET_REG = re.compile(r"^\s*\[.*]\s*(.*$)")

TRAILING_PUNCT_LIST = [
    ";",
    "'",
    ".",
    '"',
    ",",
    ":",
    "-",
    "?",
    "!",
]

TRAILING_PUNCT = "".join(TRAILING_PUNCT_LIST)

# we don't consider "'" punctuation
TRAILING_PUNCT_SET = set(TRAILING_PUNCT_LIST)



def is_target(line):
    # go down the list of targets until you find one.
    # a simpler implementation might be to ignore all targets, and
    # only match brackets.
    return IS_TARGET_REG.match(line)


# this happens twice. I could just ignore the two lines, but that's a
# little brittle, isn't it?
IS_NOISE_REG = re.compile("^[Nn]oise")


def is_noisy(tokens):
    return IS_NOISE_REG.match(tokens[0])


TITLES = set([
    "LADY",
    "Lady",
    "First",
    "Second",
    "Third",
    "FRIAR",
])
is_voice_reg = re.compile(r"\A[a-zA-Z]+\s*$")


def is_voice(tokens):
    num_words = len(tokens)
    if num_words == 1:
        word = tokens[0]
        return word not in HEADINGS and is_voice_reg.match(word)
    elif num_words == 2:
        # maybe:
        title, name = tokens
        if title in TITLES:
            return is_voice_reg.match(name)


# any line starting with these indicates non-dialog. Ignore this line
# and any lines after it, until a character speaks.
HEADINGS = set([
    "PROLOGUE",
    "SCENE",
    "ACT",
])


def is_heading(tokens):
    return tokens[0] in HEADINGS


ACTIONS = set([
    "enter",
    "beats",
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
    "Draws",
    "Knocking",
    "Sings",
    "Drinks",
    "Reads",
])


def is_action(tokens):
    # since there's a ton of these, we're going to just take the first
    # word, downcase it, and see if it's in ACTIONS.
    if tokens[0].lower() in ACTIONS:
        return True
    return len(tokens) >= 2 and tokens[:2] == ["They", "fight"]


def _python_lambdas_make_me_sad():
    return defaultdict(int)


def first_order_chain_map(deq):
    # don't want to destroy the original
    deq = deq.copy()

    out = defaultdict(_python_lambdas_make_me_sad)
    prev = deq.popleft()
    # consume the deq!
    while deq:
        after = deq.popleft()
        out[prev][after] += 1
        prev = after
    return out


def name_dialog_deques():
    ''' A map from names to a stream of dialog. COMMON is a special
    case, a complete stream of every word said by everyone in Romeo
    and Juliet '''
    out = defaultdict(deque)
    stream = soliloquy_pull()
    # special case the first stream of text
    out['COMMON'].extend(next(stream)[1])

    for name, words in stream:
        out['COMMON'].extend(words)
        out[name].extend(words)
    return out


def soliloquy_pull():
    '''Generator that pulls in names and the dialog after them,
    yielding tuples mapping names to dialog. The only non-dialog
    portion is the prologue of the first act, so we tag it here to be
    imported as common.'''
    out = ['COMMON', deque()]
    stream = sanitized_pull()

    for line in stream:
        toks = tokenize(line)
        if is_voice(toks):
            yield out
            # reinitialize with new name
            out = [" ".join(toks), deque()]
        # okay, it's text. Good idea to tokenize here and extend
        # the list.
        else:
            out[1].extend(toks)


def sanitized_pull():
    with rj() as rjf:
        line = rjf.readline()
        while line:
            # keep reading lines until we get visible text.
            # if we encounter any junk, remove it here.
            targeted = is_target(line)
            if targeted:
                yield targeted.groups()[0]
            # if I were to redo this class based, I would wrap lines
            # in some class that had this metadata constructed at init
            else:
                # we're not interested in punctuation right now.
                # rstrip it.
                tokens = [tok.rstrip(TRAILING_PUNCT)
                          for tok in line.split()]
                if tokens and not (
                        is_noisy(tokens) or
                        is_action(tokens) or
                        is_heading(tokens)):
                    yield line

            # read the next line
            line = rjf.readline()


def tokenize(line):
    whitesep = line.split()
    out = []
    for token in whitesep:
        # expecting a singleton out of maybe_split_token
        # otherwise we'll get garbage characters
        out.extend(maybe_split_token(token))
    return out


def maybe_split_token(token):
    '''Always return a list. Returning a string is gonna be messy'''
    # we're only interested in trailing punctuation. Everything else
    # we'll consider a word.
    # oh, and an apostrophe is not punctuation.
    out = []
    chars = reversed(token)
    for char in chars:
        if char in TRAILING_PUNCT_SET:
            out.append(char)
        else:
            break

    # if there's any punctuation, take the rest of the token and add
    # it to out otherwise this token should just be returned in a
    # singleton
    if out:
        out.append(token[:-len(out)])
        return list(reversed(out))
    return [token]
