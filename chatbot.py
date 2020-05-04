#!/usr/bin/env python3
import uuid
from datetime import datetime
import trainer
import natural_language_processor
import ontology_lookup

class Chatbot(object):

    """
    A conversational chatbot.
    """

    def __init__(self, **kwargs):
        self.uuid = uuid.uuid4()
        self.created_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.exchanged_conversational_units = 0
        self.trainer = trainer.Trainer(chatbot=self)
        self.model = self.trainer.load_model()
        self.ontology_lookup = ontology_lookup.OntologyLookup(chatbot=self)
        self.ontology = self.ontology_lookup.load_ontology()

    def __str__(self):
        return "This is an instance of class chatbot with a unique identifier {} " \
               "that was created on {}".format(self.uuid, self.created_at)

    def update_conversation(self, input=None, **kwargs):
        """
        Updates the ongoing conversation with a user. First, it increases the count of conversational
        exchanges by 1, then it passes the user input on to the natural language understanding module.
        The natural language understanding module predicts the user intent utilizing the trainer module
        and validates the plausibility of the trainer's predicted intent.

        If the intermediate results fall into the confidence interval, they are then cross-checked with
        the ontology search and reasoning module which compares the findings to the current and historical
        context.

        Any findings are then passed back to this calling function to steer the conversation. If one of
        the functions called returns an empty result, default_response() is invoked.

        :param input: input of the user (in response to the latest context)
        :param kwargs:
        :return: response to the user input
        """

        self.exchanged_conversational_units += 1

        if input is None:
            return self.default_response()

        self.prediction = self.trainer.predict_intent(model=self.model, input=input)

        if self.prediction[1].item() > 0.7:

            self.nlu = natural_language_processor.NaturalLanguageProcessor(chatbot=self)
            self.nlp_output = self.nlu.parse_input(input=input)
            self.sentence_type = self.nlu.classify_sentence_type(self.nlp_output)

            if self.sentence_type in str(self.prediction[0]) or self.sentence_type == 'undefined':
                self.nouns = self.nlu.noun_extraction(self.nlp_output)
                if not self.nouns:
                    return self.default_response()
                else:
                    print(1)
                    # think about how to include individuals_lookup (should nlp call or chatbot?)

        else:
            return self.default_response()

        return None

    def default_response(self):
        return "Entschuldigung, das habe ich nicht ganz verstanden."

