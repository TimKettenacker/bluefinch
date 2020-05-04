#!/usr/bin/env python3
from owlready2 import *
from fuzzywuzzy import process, fuzz

class OntologyLookup(object):
    """
    Finds entities and relationships between entities in a pre-defined ontology model.
    """

    def __init__(self, chatbot):
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
