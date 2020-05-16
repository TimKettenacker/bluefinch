#!/usr/bin/env python3
import uuid
from datetime import datetime
import conversation_context
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
        self.context = conversation_context.ConversationContext(chatbot=self)
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
        :return: None, function updates the instance of class ConversationContext()
        """

        if input is None:
            return self.context.update_context(responded_with='default')

        self.prediction = self.trainer.predict_intent(model=self.model, input=input)

        if self.prediction[1].item() > 0.6:

            self.nlu = natural_language_processor.NaturalLanguageProcessor(chatbot=self)
            self.nlp_output = self.nlu.parse_input(input=input)
            self.sentence_type = self.nlu.classify_sentence_type(self.nlp_output)

            if "confirmation" in str(self.prediction[0]) and self.sentence_type == 'confirmation/rejection':
                self.context.update_context(context_confirmed=True, input=input)
            elif "rejection" in str(self.prediction[0]) and self.sentence_type == 'confirmation/rejection':
                self.context.update_context(context_confirmed=False, input=input)
            elif self.sentence_type in str(self.prediction[0]) or self.sentence_type == 'undefined':
                self.context.update_context(input=input)
            else:
                return self.context.update_context(responded_with="default")

            self.nouns = self.nlu.noun_extraction(self.nlp_output)
            self.recognized_individuals = self.ontology_lookup.individual_lookup(self.nouns, self.sentence_type,
                                                                                         input, self.individuals)
            if self.recognized_individuals:
                self.context_class, self.context_individuals = self.ontology_lookup.ontology_search_and_reason(self.recognized_individuals[0],
                                             self.prediction, self.ontology, self.classes, self.individuals)
                self.context.update_context(input=input, nouns=self.nouns, context_class=self.context_class,
                                                    context_individuals=self.context_individuals)

            return None

        else:
            return self.context.update_context(responded_with='default')


    def respond_user(self, input=None):
        """
        Generates a respond to the user input. The reply is based on the processed intent of a users' message (which
        is estimated by invoking grasp_intent()) and the context objects that are in place during runtime.
        :param input: input of the user (in response to the latest context)
        :return: a string bot_reply
        """
        self.grasp_intent(input)
        if self.context.responded_with == 'default':
            bot_reply = self.default_response()
        else:
            bot_reply = self.context.choose_response(context_class=self.context_class, context_individuals=self.context_individuals,
                                     prediction=self.prediction)
        self.context.update_context(responded_with=bot_reply, bidirectional_conversations_count =+ 1)
        return bot_reply

    def default_response(self):
        return "Entschuldigung, das habe ich nicht ganz verstanden."
