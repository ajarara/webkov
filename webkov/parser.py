from lxml.html import HTMLParser
from collections import defaultdict, deque
import re
from pkg_resources import resource_string
import os


def rj_tree():
    '''
    Parse html and return it, head and all
    '''
    rj = HTMLParser()
    # this call can actually be replaced entirely with some
    # call to requests.get, provided it returns html.
    # this means packaging with requests and depending on
    # mit hosting shakespeare. Not attractive.
    # this is awkward:
    rjtext = resource_string(__name__, os.path.join('data', 'full.html'))
    rj.feed(rjtext)
    return rj.close()


def rj_body_iter():
    tree = rj_tree().iterchildren()
    next(tree)  # head
    body = next(tree)  # body
    return body.iterchildren()


def filtered_pull():
    '''
    Iterator that filters all children found
    by rj_body_iter by this criteria:
    all blockquotes not immediately preceded by names are discarded
    for all blockquotes, filter all italics (handled by _filter_dequeify)
    blockquotes are provided as a deque of strings (handled by ibid)
    upcases all names.
    '''
    name_precedent = False
    iterchildren = rj_body_iter()
    for element in iterchildren:
        if name_precedent and element.tag == "blockquote":
            yield _filter_dequeify(element)
            name_precedent = False
        elif element.tag == 'a' and 'name' in element.attrib:
            # this is a voice. capture it, set name_precedent, yield it.
            name_precedent = True
            # here we uppercase it.
            yield next(element.itertext()).upper()
        else:
            name_precedent = False


def _filter_dequeify(element):
    # write this when you get back. iterate through the children,
    # filtering everything that isn't itself tagged as 'a'
    out = deque()
    for node in element.iterchildren():
        if node.tag == 'a':
            out.append(node.text)
    return out


# top level
def structured_pull():
    stream = filtered_pull()

    while True:
        try:
            name, words = next(stream), next(stream)
        except StopIteration:
            break
        yield name, words


# Targets are lines like these, with brackets in the front
# [Aside] Villain and he be many miles asunder.--
TARGET_REG = re.compile(r"^\s*\[.*]\s*(.*$)")


def is_target(line, target_reg=TARGET_REG):
    # go down the list of targets until you find one.
    # a simpler implementation might be to ignore all targets, and
    # only match brackets.
    return target_reg.match(line)


# person hath here writ. I must to the learned.--In good time.
GRATUITOUS_HYPHENS = re.compile(r"(.*)--(?=\S)(.*)")


def is_gratuitous(line, gratuitous_reg=GRATUITOUS_HYPHENS):
    return gratuitous_reg.match(line)


# If a line is followed by another
# Line and the sentence is capitalized
# For no reason like this comment
# Then don't that, it's annoying
SENTENCE_ENDINGS = {
    "!",
    "?",
    ".",
}


def lowercase(line):
    return "{}{}".format(line[0].lower(),
                         line[1:])


# this determines if a word after a period is not downcased. 
CHARACTERS = [
    "Romeo",
    "Sampson",
    "Juliet",
    "Lady",
    "Tybalt",
    "Capulet",
    "Lady",
    "Montague",
    "Benvolio",
    "Paris",
    "Mercutio"
    "Friar",
    "Laurence",
    "Abraham",
    "Page",
    "Prince",
    "John",
    "Balthasar",
    "Peter",
    "Gregory",
    # not really a character but regardless.
    "I",
]


def is_addressed(line, characters=CHARACTERS):
    return any(map(lambda name: line.startswith(name), CHARACTERS))


def sanitized(deq, sentence_endings=SENTENCE_ENDINGS):
    '''
    Take a deque of lines, and sanitize them.
    Would be split into an iterator and a sanitizer if it
    weren't for the implicit state between lines.
    '''
    sanitized = deque()
    sentenceStart = False
    for line in deq:
        targeted = is_target(line)
        if targeted:
            line = targeted.groups()[0]

        gratuitous = is_gratuitous(line)
        if gratuitous:
            before, after = gratuitous.groups()
            line = "{}-- {}".format(before, after)

        # if a line is uppercase and it shouldn't be, lowercase it.
        if line[0].isupper() and not(sentenceStart or
                                     is_addressed(line)):
            line = lowercase(line)

        sentenceStart = line[-1] in sentence_endings

        # okay, we made it past the gauntlet. Add it
        sanitized.append(line)

    return sanitized


def name_dialog_deques(_cache={}):
    ''' A map from names to a stream of dialog. COMMON is a special
    case, a complete stream of every word said by everyone in Romeo
    and Juliet '''
    # the caching mechanism is awkward.
    if not _cache:
        raw = defaultdict(deque)
        stream = structured_pull()

        for name, line in stream:
            raw['COMMON'].extend(line)
            raw[name].extend(line)

        # lowest overhead is to sanitize them here.
        # since we sanitize _after_ appending we
        # assume that every character starts dialog with
        # a capitalized word.

        view = iter(raw.items())
        # finalize, sanitize, tokenize
        out = {}
        for name, deq in view:
            cleaned = sanitized(deq)

            words = deque()
            while cleaned:
                line = cleaned.popleft()
                words.extend(
                    tokenize(line))

            out[name] = words

        _cache = out
        return out.copy()
    return _cache.copy()





TRAILING_PUNCT_LIST = [
    ";",
    # should apostrophes be included?
    # there are some scenarios where apostrophes
    # are actually punctuation
    # and some when it's shortening, like o'
    # "'"
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
