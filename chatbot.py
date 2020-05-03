#!/usr/bin/env python3

import uuid
from datetime import datetime

class Chatbot(object):

    """
    A conversational chatbot.
    """

    def __init__(self, **kwargs):
        self.uuid = uuid.uuid4()
        self.created_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.exchanged_conversational_units = 0

    def __str__(self):
        return "This is an instance of class chatbot with a unique identifier {} " \
               "that was created on {}".format(self.uuid, self.created_at)

    def update_conversation(self, user_input=None, **kwargs):
        """
        Updates the ongoing conversation with a user. First, it increases the count of conversational
        exchanges by 1, then it passes the user input on to the natural language understanding module.
        The natural language understanding module predicts the user intent utilizing the trainer module
        and validates the plausibility of the trainer's predicted intent.

        The intermediate results are then cross-checked with the ontology search and reasoning module
        which compares the findings to the current and historical context.

        Any findings are then passed back to this calling function to steer the conversation.

        :param user_input: input of the user (in response to the latest context)
        :param kwargs:
        :return: response to the user input
        """

        self.exchanged_conversational_units += 1

        return None

