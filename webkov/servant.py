from collections import deque, defaultdict, Counter
from random import choice

from webkov.parser import name_dialog_deques, TRAILING_PUNCT_SET
from webkov.parser import SENTENCE_ENDINGS


# woohoo! pretty looking shakespeare!
def prose(start=(".",), name='JULIET', num_tokens=75):
    print(pretty(
        generate_tokens(start=start, name=name, num_tokens=num_tokens)))


def uppercase(line):
    ''' Takes a line and uppercases the first letter '''
    return "{}{}".format(line[0].upper(),
                         line[1:])


def pretty(tokens, line_min_chars=35, shakespeare=True,
           sentence_endings=SENTENCE_ENDINGS,
           trailing_punct_set=TRAILING_PUNCT_SET):
    '''
    Returns a string of lines obtained from concatenating tokens until
    length is above line_min_chars. There is no guarantee returned
    strings don't exceed line_min_chars by an insane amount.  If we
    run out of tokens, join whatever, even if it's under
    line_min_chars.

    Yeah, this function doesn't do what you want. ☠
    I'm assuming ascii here.
    '''
    prettified_lines = deque()

    charcount = 0
    words = deque()

    toks = truncate(tokens.copy())
    while toks:
        # uses peekin!
        continue_line_predicate = (charcount < line_min_chars or
                                   toks[0] in sentence_endings or
                                   toks[0] in trailing_punct_set)
        if continue_line_predicate:
            tok = toks.popleft()
            charcount += len(tok)
            words.append(tok)
        else:
            line = "".join(padded(words))
            if len(line) > 1 and shakespeare:
                line = uppercase(line)
            prettified_lines.append(line)
            # reinitialize
            charcount = 0
            words = deque()
    if words:
        line = "".join(padded(words))
        if len(line) > 1 and shakespeare:
            line = uppercase(line)
        prettified_lines.append(line)

    return "\n ".join(prettified_lines)


def padded(tokens):
    '''
    for each token, prepend a space to them provided they aren't punctuation
    Special case the first token.
    '''
    out = deque([tokens.popleft()])
    while tokens:
        token = tokens.popleft()
        if token not in TRAILING_PUNCT_SET:
            out.append(" ")
        out.append(token)
    return out


def truncate(tokens, sentence_endings=SENTENCE_ENDINGS):
    '''
    Truncate on a complete sentence, identified by sentence_endings
    '''
    # iterate backwards
    while tokens:
        maybe_punct = tokens.pop()
        if maybe_punct in sentence_endings:
            tokens.append(maybe_punct)
            break
    return tokens


# TIL you need the trailing comma to for (".") to be a tuple.
def generate_tokens(start=(".",), num_tokens=75, name='COMMON'):
    " Return a deque. "

    # eh since we're top level, we might as well start doing assertions
    assert start
    # wrap the string in a tuple so we don't have to do it for order 1 chains.
    if isinstance(start, str):
        start = tuple(start)
    assert isinstance(start, tuple)
    order = len(start)

    words = name_dialog_deques()[name]
    chains = chain_from_deq(words, order=order)

    if start not in chains:
        raise KeyError("{} is not in the dialog of {}".format(
            repr(start),
            name))

    out = deque()
    # special case the start token if it starts with a "."
    if start[0] in [".", "!", "?"]:
        out.extend(start[1:])
    else:
        out.extend(start)

    # to facilitate quick appends and left sided pops,
    # we'll just use a deque here.
    deq = deque(start)

    for _ in range(num_tokens):
        # if we wanted to choose between determinism, we'd do
        # it here.
        after = choice(list(
            chains[tuple(deq)].elements()))
        out.append(after)

        deq.popleft()  # drop off the stale element
        deq.append(after)  # use the new one

    return out


# one function > two
def chain_from_deq(deq, order=1):
    deq = deq.copy()

    out = defaultdict(Counter)
    assert len(deq) > order
    keys = []
    # initialize keys
    for _ in range(order):
        keys.append(deq.popleft())
    # consume the tokens!
    while deq:
        after = deq.popleft()
        out[tuple(keys)][after] += 1
        # splice out the first key.
        keys = keys[1:]
        # and append what we just got
        keys.append(after)
    return out
