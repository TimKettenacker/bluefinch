#!/usr/bin/env python3

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
        """
        Imports the German language model.
        :return:
        """
        nlp = de_core_news_sm.load()
        return nlp

    def parse_input(self, input):
        """
        Parses input statements utilizing NLP. The input string is passed on to the NLP pipeline
        in camel case, because leading capital letters have proven to be advantageous in detecting
        entities over lower case input (underlying assumption is that the user does not deliberately
        pay attention to correct spelling or letter capitalization).
        :param input: a statement from the user (string)
        :return: a dictionary containing a list for each token in the original message. The list
        contains the output of applying 'shallow parsing' through the nlp pipeline on a given input.
        More specific, the list contains the original input token, the detected part-of-speech,
        a clearer tag, dependency of the token to the other tokens in the sentence and a reference
        to the leading token (see more on https://spacy.io/usage/spacy-101#annotations-pos-deps)
        :rtype dictionary
        """
        nlp = self.load_model()
        doc = nlp(input.title())
        nlp_output = defaultdict(list)
        for token in doc:
            nlp_output[token.i] = [token.text, token.pos_, token.tag_, token.dep_, token.head.text]
        return nlp_output

    def classify_sentence_type(self, nlp_output):
        """
        Classifies the parsed input from parse_input() into sentence types. It does this by
        comparing the 'shallow parsing' results returned from parse_input() as a dictionary
        to pre-defined patterns. This is to validate the prediction output of predict_intent()
        of trainer.py against typical syntactical patterns and formal part-of-speech-logic
        that can be observed for open and closed questions.
        :param nlp_output: a dictionary containing 'shallow parsing' results, obtained by passing
        user input messages to parse_input()
        :return: a string classification of the text, either 'open_question', 'closed_question' or
        'undefined' (user wishes and imperatives cannot be derived easily and remain "undefined")
        """
        open_question_pointers = ['PWAT', 'PWAV', 'PWS']  # which, when, what, ...
        closed_question_pointers = ['VMFIN', 'VVFIN', 'VVIMP', 'VAFIN']  # könnt, habt, ...
        if nlp_output[0][2] in open_question_pointers:
            sentence_type = 'open_question'
        elif nlp_output[0][2] in closed_question_pointers and nlp_output[len(nlp_output.keys()) - 1][0] == '?':
            sentence_type = 'closed_question'
        else:
            sentence_type = "undefined"
        return sentence_type

    