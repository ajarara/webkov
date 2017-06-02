#!/usr/bin/env python3

# given a chunk, tokenize it. Consume all but the last token.
from nltk import word_tokenize
from collections import deque

def tokenize_chunk(chunk):
    words = word_tokenize(chunk)
    
    return deque(words[:-1]), words[-1]

# given a generator of chunks, construct a generator of deque words
# preserving the last word of the chunk in case words get broken up
def deqwords(chunk_gen):
" given a generator of chunks, construct a generator of deque words
  preserving the last word of the chunk in case words get broken up.
  Preserve StopIteration."
    last = ""
    
    while True:
        # add last to the next part of the input stream
        # if it was indeed a seperate word, there should be a space
        # or punctuation following it which would preserve it being
        # a seperate word. If it wasn't, concatenation will bring out
        # the original.
        try:
            chunk = last + next(chunk_gen)
        except StopIteration:
            chunk = last
            raise StopIteration
            
        words, maybe_word = tokenize_chunk(chunk)
        
        last = maybe_word
        yield words

def example_chunk_get():
    CHUNK_SIZE = 20
    
    for _ in range(100):
        

