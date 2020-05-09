#!/usr/bin/env python3
from owlready2 import *
from fuzzywuzzy import process, fuzz

class OntologyLookup(object):
    """
    Finds entities and relationships between entities in a pre-defined ontology model.
    """

    def __init__(self, chatbot, **kwargs):
        self.chatbot = chatbot

    def __str__(self):
        return "This is an instance of class OntologyLookup"

    def load_ontology(self):
        """
        Loads the ontology into memory.
        :return: an ontology object (owlready2)
        """
        onto_path.append("ontology_material")
        ontology = get_ontology("GoodRelationsBluefinch_v2.owl")
        ontology.load()
        return ontology

    def display_classes_and_individuals(self, ontology):
        """
        Reads classes and their individuals from the ontology. This functionality was introduced
        to enable a faster lookup of the items in an ontology as opposed to the resource-intensive
        search through the edges and nodes of the ontology itself.
        :return: two dictionary objects for all the classes and their respective individuals:
        the classes dictionary object provides the class label as a key, i.e. 'PaymentMethod' and
        the actual <class 'owlready2.entity.ThingClass'> as its value, while the individuals
        dictionary object provides the instance label, i.e. 'American Express (payment method)' as
        key and the uri and the name as values.
        """
        classes = defaultdict(list)
        for cl in ontology.classes():
            classes[cl.name] = cl

        individuals = defaultdict(list)
        for individual in ontology.individuals():
            individuals[individual.label.first()] = [individual.iri, individual.is_a.first().name]

        return classes, individuals

    def individual_lookup(self, nouns, sentence_type, input, individuals):
        """
        This is the first of two search methods applied to speed up matching entities discovered
        in a user's message to items in an ontology. It uses a fuzzy string comparison algorithm
        to detect overlaps between the nouns mentioned in the user input and the string representation
        of the individuals in an ontology. As long as a question is not an open question, an honest
        attempt can be made by comparing the whole user message against all individuals.
        :param sentence_type: a string classification of the sentence type, i.e. 'open question'.
        Introduced by applying method classify_sentence_type() in natural_language_processor.py
        :param input: a string containing the user message
        :param individuals: a dictionary of individuals to an ontology class, extracted through
        display_classes_and_individuals().
        :return: a list of detected matches.
        """
        if (len(input) < 50) and sentence_type != "open_question":
            match_list = process.extractBests(input, individuals.keys(), scorer=fuzz.UWRatio,
                                              score_cutoff=70, limit=len(individuals))
        else:
            match_list = process.extractBests(nouns, individuals.keys(), scorer=fuzz.UWRatio,
                                              score_cutoff=70, limit=len(individuals))
        match_list_cleaned = [[*x] for x in zip(*match_list)]
        return match_list_cleaned[0]

    def ontology_search_and_reason(self, recognized_individuals, prediction, ontology, classes, individuals):
        """
        This is the second of two search methods applied to speed up matching entities discovered
        in a user's message to items in an ontology. It retrieves knowledge from the ontology by
        comparing the individuals name to any of the pre-defined terms, i.e. "PaymentMethod" in order
        to set the context. Whenever a match to a term is established successfully, the context
        object is updated accordingly. The context object is passed on to the calling chatbot to
        steer the conversation and keep track of the subjects the conversation touched on.
        :param prediction:
        :return: a context object
        """
        context_class = []
        context_individual = []

        if 'product_availability' in str(prediction[0]):
            for ind in recognized_individuals:
                if individuals[ind][1] == 'Product':
                    context_individual.append(ontology.search(iri=individuals[ind][0]).first())
            context_class = classes['Product']
        return context_class, context_individual