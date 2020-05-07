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
        self.classes, self.individuals = self.ontology_lookup.display_classes_and_individuals(self.ontology)

    def __str__(self):
        return "This is an instance of class chatbot with a unique identifier {} " \
               "that was created on {}".format(self.uuid, self.created_at)

    def grasp_intent(self, input=None, **kwargs):
        """
        This function aims at grasping the intent the user implies or conveys in his messages. It applies
        various methods to get closer to the user's intentions: first, it passes the input to the natural
        language understanding module, which in turn predicts the user intent utilizing the trainer module
        and validates the plausibility of the trainer's predicted intent.

        If the intermediate results fall into the confidence interval, they are then cross-checked with
        the ontology search and reasoning module which tries to establish a match between the recognized
        entities and the classes and individuals in the ontology.

        Any findings are then passed back to this calling function to update the context node and further
        steer the conversation. If one of the functions called returns an empty result, default_response()
        is invoked.

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
                    self.recognized_individuals = self.ontology_lookup.individual_lookup(self.nouns, self.sentence_type,
                                                                                         input, self.individuals)
                    if not self.recognized_individuals:
                        return self.default_response()
                    else:
                        context_class, context_individual = self.ontology_lookup.ontology_search_and_reason(self.recognized_individuals,
                                                                        self.prediction, self.ontology, self.classes, self.individuals)
                        return context_class, context_individual

        else:
            return self.default_response()

        return None

    def default_response(self):
        return "Entschuldigung, das habe ich nicht ganz verstanden."
