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
        self.bidirectional_conversations_count = 0
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
        parameters below. Mind that the parameters have to be explicitly passed to this function to avoid
        any inconsistencies in the context.
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
        if "bidirectional_conversations_count" in kwargs:
            self.bidirectional_conversations_count += 1
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

    def traverse_graph(self, context_individuals):
        """
        This function retrieves all outgoing relationships and the attached objects from a single
        individual based on its class.
        :param context_individuals: the individual of interest, as per display_classes_and_individuals()
        :return: a dictionary with the relationship as the key and the referenced nodes as its values
        """
        attached = defaultdict(list)
        if context_individuals.is_a[0].name == 'Product':
            attached['Variants'] = context_individuals.hat_Produktvariante
        return attached

    def choose_response(self, context_class, context_individuals, prediction):
        """
        For selecting the proper response, this function takes the context of the conversation, the prediction and
        the sentence types into decision. It processes the content with the help of its inbuilt logic and chooses
        the best possible outcome from the possible responses list.
        :param possible_responses: list of possible responses, invokes load_response_options() if not present
        :param context_class: the class found in an ontology search
        :param context_individual: the individuals found in an ontology search
        :param prediction: the prediction result for a specific user input
        :return: the selected string response
        """
        possible_responses = self.load_response_options()

        if (context_class.name == 'Product') and ("product_availability" in str(prediction[0])):
            if len(context_individuals) == 1:
                response = random.choice(possible_responses['_product_availability_one']) % dict(
                    first=context_individuals[0].label.first())
            elif len(context_individuals) == 2:
                response = random.choice(possible_responses['_product_availability_two']) % dict(
                    first=context_individuals[0].label.first(), last=context_individuals[1].label.first())
            elif len(context_individuals) > 2:
                many = ""
                for w in context_individuals:
                    many += str(w.label.first()) + ", "
                response = random.choice(possible_responses['_product_availability_many']) % dict(many=many)

        if context_class.name in ['Product', 'Individual'] and ("confirmation" in str(prediction[0])) \
                or ("product_variant" in str(prediction[0])):
            if context_individuals[0].is_instance_of.first().name == 'Product':
                attached = []
                for individual in context_individuals:
                    attached.append(self.traverse_graph(individual))
                many = ""
                for e in range(0, len(attached)):
                    for variant in attached[e]['Variants']:
                        many += str(variant.label.first() + ", ")
                    response = random.choice(possible_responses['_product_variants']) % dict(many=many)
            else:
                response = random.choice(possible_responses['_variants_finegrain']) % dict(first=
                                                            context_individuals[0].label.first())

        # if (context_class.name == 'Individual') and ("product_variant" in str(prediction[0])):
        #     if context_individuals[0].is_instance_of.first().name == 'Product':
        #         response = "ficken"
        #     else:
        #         response = random.choice(possible_responses['_variants_finegrain']) % dict(
        #             first=context_individuals[0].label.first())

        return response
