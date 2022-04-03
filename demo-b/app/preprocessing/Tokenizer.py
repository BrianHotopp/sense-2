import re


def tokenize_words(text, min_length=0):
    """
    text: List[str] representing a sentence
    """
    r = re.compile(r"[a-zA-Z\.]+")
    r_html = re.compile(r"<\.*?>")  # Match HTML tags
    r_acronym = re.compile(r"\.") # match periods "."

    text = r_html.sub("", text)
    text = r_acronym.sub("", text)
    tokens = r.findall(text) # strip everything that doesn't look like a word (a-z)
    tokens = [t for t in tokens if len(t) >= min_length]
    return tokens


class WordTokenizer:

    def __init__(self):
        self.re_word = re.compile("[a-zA-z\.]+")  # Captures words, including acronyms (e.g.: U.S.)
        self.re_alphanum = re.compile("\w+")
        self.re_acronym = re.compile("\.")  # Used to remove punctuation from acronyms (U.S. -> US)
        self.re_digit = re.compile("[0-9]+")
        self.re_html = re.compile("<.*?>")  # Match HTML tags

    def tokenize(self, text, remove_html=True, exclude_digits=True):
        """
        Tokenize `text` by matching words.
        Args:
            text - Input text as a string.
            remove_html - Use HTML parser to remove HTML tags.
            exclude_digits - Do not include numbers and digits in final sentence.
        Returns:
            tokens - list(str) Tokenize sentences.
        """
        if remove_html:
            text = self.re_html.sub("", text)
        if exclude_digits:
            tokens = self.re_word.findall(text)
        else:
            tokens = self.re_alphanum.findall(text)

        return tokens
