# Webkov

What if Romeo and Juliet never died?

# servant.py

intermediary spec:

## take in rj.txt unmodified producing sanitized markov chains

What do I mean when I say sanitized?
Well, here is where I've downloaded Romeo and Juliet:
http://shakespeare.mit.edu/romeo_juliet/full.html

Initially I copied and pasted the text into emacs, thinking that would make it easier to parse (instead of going through some html parser).

However doing this loses an awful lot of metadata. For one, html blockquotes are preceded immediately by their text. All actions are italicized (previously I put them into a blacklist). Clearly the best way to go is through parsing html, as opposed to rewriting the sanitized code.

