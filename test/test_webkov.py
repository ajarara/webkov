import webkov.sentence as wks

def test_tokenize_chunk():

    # scrub context sensitive crap
    closeParen = "(This sentence will be treated} the same"
    tok_closeParen = [ "This", "sentence", "will", "be", "treated", "the", "same" ]

    assert tok_closeParen == list(wks.tokenize_chunk(closeParen))
    
    # easy = "This sentence."
    # tok_easy = [ "This" "sentence" "." ]
    # assert tok_easy == wks.split_sentence_to_tokens(easy)
    
    # regular = "This sentence terminates in a period."
    # tok_regular = [ "This" "sentence" "terminates" "in" "a" "period" "." ]
    # assert tok_regular == wks.split_sentence_to_tokens(regular)

    # mlady = "This sentence pleases Mrs. Applebaum."
    # tok_mlady = [ "This" "sentence" "pleases" "Mrs." "Applebaum" "." ]
    # assert tok_mlady == wks.split_sentence_to_tokens(mlady)


def test_parse_token():
    parens = "(Ambulance)"
    cleanParens = "Ambulance"
    assert cleanParens == wks.clean_token(parens)

    empty = ""
    assert wks.clean_token(empty) == None

    happy = "Hello!"
    assert wks.clean_token(happy) == [ "Hello", "!" ]
