import webkov.sentence as wks

def test_sentence_to_tokens():
    easy = "This sentence."
    tok_easy = [ "This" "sentence" "." ]
    assert tok_easy == wks.split_sentence_to_tokens(easy)
    
    # regular = "This sentence terminates in a period."
    # tok_regular = [ "This" "sentence" "terminates" "in" "a" "period" "." ]
    # assert tok_regular == wks.split_sentence_to_tokens(regular)

    # mlady = "This sentence pleases Mrs. Applebaum."
    # tok_mlady = [ "This" "sentence" "pleases" "Mrs." "Applebaum" "." ]
    # assert tok_mlady == wks.split_sentence_to_tokens(mlady)
"
