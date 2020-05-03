#!/usr/bin/env python3
import de_core_news_sm
from collections import defaultdict
import chatbot

class NaturalLanguageProcessor(object):
    """
    Parses statements of the user into entities.
    """
    def __init__(self, chatbot):
        self.chatbot = chatbot

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

    def noun_extraction(self, nlp_output):
        """
        Attempts to extract entities from a user's message in order to grasp the products and product
        features a user mentions in his text. It is the first step in sharpening the context of a
        conversation and keeping it alive throughout the chat.

        The entity extraction confines to the typical setup of the domain data and thus is very specialized.
        I.e., it tries to pay attention to the naming conventions of Apple products where the brand
        name is followed by a version number or roman letter, i.e. iPhone 11 or iPhone X.
        Hence, this function first looks for a noun or proper noun which is the sentence root at the same
        time, and writes this to variable root_noun. It then looks for other (proper) nouns, x or nums,
        which are marked as nk or pnc dependencies and carry the root noun as its head.

        The returned nouns are then used for lookups in the ontology.

        :param nlp_output: a dictionary containing the 'shallow parsing' results from parse_input()
        :return: a string containing the entities instrumental to the key content of a message
        """
        found_nouns = []
        root_noun = ''

        for key, value in nlp_output.items():
            if value[1] in ['NOUN', 'PROPN'] and value[3] in ['ROOT', 'pnc']:
                root_noun = value[0]
                found_nouns.append(value[0])
            if root_noun in value[4] and value[1] in ['PROPN', 'NOUN', 'X', 'NUM'] and value[3] in ['nk', 'pnc']:
                found_nouns.append(value[0])

        nouns = ' '.join(found_nouns)
        return nouns
