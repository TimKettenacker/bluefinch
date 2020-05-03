import de_core_news_sm
from collections import defaultdict

class NaturalLanguageProcessor(object):
    """
    Parses statements of the user into entities.
    """
    def __init__(self, trainer):
        self.trainer = trainer

    def __str__(self):
        return "This is an instance of class NaturalLanguageProcessor"

    def load_model(self):
        nlp = de_core_news_sm.load()
        return nlp

    def parse_user_input(self, user_input):
        nlp = self.load_model()
        doc = nlp(user_input.title())
        nlp_output = defaultdict(list)
        for token in doc:
            nlp_output[token.i] = [token.text, token.pos_, token.tag_, token.dep_, token.head.text]
        return nlp_output

