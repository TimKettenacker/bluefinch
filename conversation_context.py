#!/usr/bin/env python3
import uuid
from datetime import datetime

class ConversationContext(object):

    """
    A conversation object holding the context of an ongoing conversation between a chatbot and a user.
    """

    def __init__(self, chatbot, **kwargs):
        self.chatbot = chatbot
        self.uuid = uuid.uuid4()
        self.created_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.last_modified = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.exchanged_conversational_units = 0
        self.in_response_to = 'initial'
        self.detected_ners = ''
        self.current_class = ''
        self.current_individuals = []
        self.responded_with = 'initial'

    def __str__(self):
        return "This is an instance of class ConversationContext with a unique identifier {} " \
               "that was created on {}".format(self.uuid, self.created_at)

    def update_context(self, input=None, nouns=None, context_class=None, context_individuals=None, responded_with=None,  **kwargs):
        """
        This function updates the context of an ongoing conversation. It is called on an instance of object
        ConversationContext() from within a chatbot to update the context of the conversation based on the
        parameters below.
        :param input: a string input message from the user
        :param nouns: the nouns detected by an nlp operation using NaturalLanguageProcessor()
        :param context_class: the class the conversation currently revolves around
        :param context_individuals: the individuals the conversation currently revolves around
        :param kwargs:
        :return: None, it updates the ConversationContext() object instead
        """
        self.in_response_to = input
        self.detected_ners = nouns
        self.current_class = context_class
        self.current_individuals = context_individuals
        self.responded_with = responded_with
        self.last_modified = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        return None

