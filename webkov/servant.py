from collections import deque, defaultdict, Counter
from random import choice

from webkov.parser import name_dialog_deques, TRAILING_PUNCT_SET


# bug--is not followed by space. Why?
# that's how it is in the text. Fix it? Or no.
def padded(tokens):
    '''
    for each token, prepend a space to them provided they aren't punctuation
    Special case the first token.
    '''
    out = [tokens[0]]
    for token in tokens[1:]:
        if token not in TRAILING_PUNCT_SET:
            out.append(" ")
        out.append(token)
    return out


# TIL you need the trailing comma to for (".") to be a tuple.
def generate_tokens(start=(".",), num_tokens=30, name='COMMON'):

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

    out = []
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
