#!/usr/bin/env python3
import uuid
from datetime import datetime
from collections import defaultdict
import csv
import random

class ConversationContext(object):

    """
    A conversation object holding the context of an ongoing conversation between a chatbot and a user.
    """

    def __init__(self, chatbot, **kwargs):
        self.chatbot = chatbot
        self.uuid = uuid.uuid4()
        self.created_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.last_modified = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.bidirectional_conversations = 0
        self.in_response_to = 'initial'
        self.detected_ners = None
        self.current_class = None
        self.current_individuals = None
        self.responded_with = None
        self.context_confirmed = None

    def __str__(self):
        return "This is an instance of class ConversationContext with a unique identifier {} " \
               "that was created on {}".format(self.uuid, self.created_at)

    def update_context(self, **kwargs):
        """
        This function updates the context of an ongoing conversation. It is called on an instance of object
        ConversationContext() from within a chatbot to update the context of the conversation based on the
        parameters below.
        :param input: a string input message from the user
        :param nouns: the nouns detected by an nlp operation using NaturalLanguageProcessor()
        :param context_class: the class the conversation currently revolves around
        :param context_individuals: the individuals the conversation currently revolves around
        :param context_confirmed: whether the (previous) context has been confirmed or rejected by the user
        :return: None, it updates the ConversationContext() object instead
        """
        if 'input' in kwargs:
            self.in_response_to = kwargs['input']
        if 'nouns' in kwargs:
            self.detected_ners = kwargs['nouns']
        if 'context_class' in kwargs:
            self.current_class = kwargs['context_class']
        if 'context_individuals' in kwargs:
            self.current_individuals = kwargs['context_individuals']
        if 'responded_with' in kwargs:
            self.responded_with = kwargs['responded_with']
        if 'context_confirmed' in kwargs:
            self.context_confirmed = kwargs['context_confirmed']
        self.last_modified = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        return None

    def load_response_options(self):
        """
        Reads in possible responses from a csv file.
        :return: a list containing all possible response options
        """
        possible_responses = defaultdict(list)
        with open("ml_model/responses.csv", 'r', newline='') as f:
            reader = csv.reader(f, delimiter=';')
            next(reader)  # toss headers
            for label, reply in reader:
                possible_responses[label].append(reply)
        return possible_responses

    def choose_response(self, context_class, context_individual, prediction):
        """
        For selecting the proper response, this function takes the context of the conversation, the prediction and
        the sentence types into decision. It processes the content with the help of its inbuilt logic and chooses
        the best possible outcome from the possible responses list.
        :param possible_responses: list of possible responses, invokes load_response_options() if not present
        :param context_class: the class found in an ontology search
        :param context_individual: the individuals found in an ontology search
        :param prediction: the prediction result for a sepcific user input
        :return: the selected string response
        """
        possible_responses = self.load_response_options()

        if (context_class.name == 'Product') and ("product_availability" in str(prediction[0])):
            if len(context_individual) == 1:
                response = random.choice(possible_responses['_product_availability_one']) % dict(
                    first=context_individual[0].label.first())
            elif len(context_individual) == 2:
                response = random.choice(possible_responses['_product_availability_two']) % dict(
                    first=context_individual[0].label.first(), last=context_individual[1].label.first())
            elif len(context_individual) > 2:
                many = ""
                for w in context_individual:
                    many += str(w.label.first()) + ", "
                response = random.choice(possible_responses['_product_availability_many']) % dict(many=many)

        return response
