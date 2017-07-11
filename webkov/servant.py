from collections import deque, defaultdict, Counter, namedtuple
from random import choice
import termcolor

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


# hmm.. how am I going to map this to html?
# am I going to even care?
ORDER_COLOR_MAP = {
    0: 'white',
    1: 'magenta',
    2: 'red',
    3: 'yellow',
    4: 'green',
    5: 'cyan',
}


# TODO, splice it into pretty
def colored_transform(maybe_token, order_color_map=ORDER_COLOR_MAP):
    '''
    Take a token, and if it's just a string, return it as is.
    If it's tagged, return the colored version of it using termcolor
    '''
    if isinstance(maybe_token, Colored_Token):
        return termcolor.colored(maybe_token.token,
                                 order_color_map[maybe_token.order])
    else:
        return maybe_token

def pretty(tokens, line_min_chars=35, shakespeare=True,
           min_lines_before_break=(2, 4),
           sentence_endings=SENTENCE_ENDINGS,
           trailing_punct_set=TRAILING_PUNCT_SET):
    '''
    Super messy function.

    Returns a string of lines obtained from concatenating tokens until
    length is above line_min_chars. There is no guarantee returned
    strings don't exceed line_min_chars by an insane amount.  If we
    run out of tokens, join whatever, even if it's under
    line_min_chars. If when adding a line, we notice the length
    of our output is greater than min_lines_before_break, append a newline.

    Yeah, this function doesn't do what you want. ☠
    I'm assuming ascii here.
    '''
    prettified_lines = deque()

    lines_before_break = 0
    charcount = 0
    words = deque()

    toks = truncate(tokens.copy())
    while toks:
        # uses peekin!
        continue_line_predicate = (charcount < line_min_chars or
                                   toks[0] in sentence_endings or
                                   toks[0] in trailing_punct_set)
        if continue_line_predicate:
            # here is a good place to add colored_transform
            tok = toks.popleft()
            charcount += len(tok)
            words.append(tok)
        else:
            # how could a function named pretty be so ugly?
            maybe_break = ((lines_before_break >
                           choice(range(*min_lines_before_break))) and
                           (prettified_lines[-1][-1] in sentence_endings or
                            prettified_lines[-1][-1] in trailing_punct_set))
            if maybe_break:
                prettified_lines.append("")
                lines_before_break = lines_before_break - maybe_break
            # now we add another line
            lines_before_break += 1
            line = "".join(padded(words))
            if len(line) > 1 and shakespeare:
                line = uppercase(line)
            prettified_lines.append(line)

            # reinitialize
            charcount = 0
            words = deque()
    if words:
        # don't worry about breaking anymore, this is the last one.
        line = "".join(padded(words))
        if len(line) > 1 and shakespeare:
            line = uppercase(line)
        prettified_lines.append(line)

    return "\n".join(prettified_lines)


def padded(tokens):
    '''
    for each token, prepend a space to them provided they aren't punctuation
    Special case the first token.
    '''
    tokens = tokens.copy()
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

    # eh since we're top levelish, we might as well start doing assertions
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


# ==================== TAGGED ====================
def gen_models(order=5, name='COMMON', _cache={}):
    stream = name_dialog_deques()[name]
    for i in range(1, order + 1):
        if i not in _cache:
            _cache[i] = chain_from_deq(stream, order=i)
    return _cache.copy()


# can you use namedtuples for lightweight classes?
Colored_Token = namedtuple("Colored_Token", ['token', 'order'])


# okay I have NO idea what is going on in this code
def legible(start=(".",), order=5, name='COMMON', num_tokens=75):
    assert len(start) <= order

    init = (Colored_Token(tok, 0) for tok in start)
    out = deque(init)
    curr = deque(start)
    between = curr
    models = gen_models(order=order, name=name)

    while len(out) <= num_tokens:
        curr = between  # reinitialize curr
        while len(curr) > order:
            curr.popleft()
        # tackles the case where curr is greater than order
        descending_orders = reversed(range(1, min(len(curr), order) + 1))
        for i in descending_orders:
            if len(curr) > i:
                curr.popleft()

            # check that the sky hasn't fallen
            assert len(curr) == i
            model = models[i]
            # infinite loop somewhere...
            tup = tuple(curr)
            if tup in model and not _is_predetermined(tup, model):
                # our tup has generated a legible token
                print(curr)
                got = choice(list(
                    model[tup].elements()))
                
                out.append(Colored_Token(got, i))
                between.append(got)
                between.popleft()
                # break out of the for loop
                break

    return out


def _is_predetermined(token, model):
    ''' This maximizes the order while introducing an element of chance '''
    return len(model[token].keys()) <= 1
