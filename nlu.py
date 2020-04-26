# classify what the user wants to do, even if the product is already mentioned. Classify into
# sentence_types = greeting(opening, closing, politeness), chitchat, action(question, user_wish, imperative), ordinary
# if there is a clear match between entity of interest and ontology after classifying the intent,
# it is easier to reply back; if entity of interest is in ontology, the conversation can be navigated more easily

from owlready2 import *
import fasttext
import de_core_news_sm
from collections import defaultdict
import csv
from fuzzywuzzy import process, fuzz
import random


def classify_sentence_type(nlp_output):
    # classifies sentence types according to shallow parsing results
    open_question_pointers = ['PWAT', 'PWAV', 'PWS'] # which, when, what, ...
    closed_question_pointers = ['VMFIN', 'VVFIN', 'VVIMP', 'VAFIN'] # könnt, habt, ...
    if nlp_output[0][2] in open_question_pointers:
        sentence_type = 'open_question'
    elif nlp_output[0][2] in closed_question_pointers and nlp_output[len(nlp_output.keys())-1][0] == '?':
        sentence_type = 'closed_question'
    else:
        sentence_type = "undefined"
    # user wishes and imperatives cannot be derived by formal pos logic just like that and remain "undefined"
    return sentence_type


def get_sequence_index(subseq, seq):
    # returns the index start of a pattern, uses in noun_extraction()
    i, n, m = -1, len(seq), len(subseq)
    try:
        while True:
            i = seq.index(subseq[0], i + 1, n - m + 1)
            if subseq == seq[i:i + m]:
                return i
    except ValueError:
        return -1


def noun_extraction(nlp_output):
    # looks for a noun or proper noun which is root at the same time, and writes it to root_noun
    # looks for other (proper) nouns, x or nums, which are marked as nk or pnc dependencies and carry
    # the root_noun as head
    found_nouns = []
    root_noun = ''

    for key, value in nlp_output.items():
        if value[1] in ['NOUN', 'PROPN'] and value[3] in ['ROOT', 'pnc']:
            root_noun = value[0]
            found_nouns.append(value[0])
        if root_noun in value[4] and value[1] in ['PROPN', 'NOUN', 'X', 'NUM'] and value[3] in ['nk', 'pnc']:
            found_nouns.append(value[0])

    nouns = ' '.join(found_nouns)
    # this should be made test cases:
    # "Habt ihr das Iphone 11 Pro?" # finds iphone, pro
    # "Habt ihr Apples Iphone 11?" # finds apples, iphone, 11
    # "Habt ihr Apples Iphone X?" # finds apples, iphone, x
    # "Was für apple produkte habt ihr?" # finds apples, produkte
    # "Was für iphones habt ihr?" # finds iphones
    # "Welche iphones habt ihr?" # finds iphones, habt
    return nouns

# have a twofold search to perform faster and yield better results;
# first, collect all individuals to fuzzy search detected entities against them (i.e. with fuzzywuzzy)
# second, a detected matching iri goes into ontology to retrieve node connections
def individual_lookup(nouns, sentence_type, userText):
    # compares detected nouns with instance data from the ontology
    # if a question is closed and short, an honest attempt can be made by throwing in the whole user message
    if (len(userText) < 50) and sentence_type != "open_question":
        match_list = process.extractBests(userText, individuals.keys(), scorer=fuzz.UWRatio,
                                          score_cutoff=70, limit=len(individuals))
    else:
        match_list = process.extractBests(nouns, individuals.keys(), scorer=fuzz.UWRatio,
                                          score_cutoff=70, limit=len(individuals))
    match_list_cleaned = [[*x] for x in zip(*match_list)]
    # depending on the prediction, the caller may filter on all that made the cut in the answer generation
    return match_list_cleaned[0]


def ontology_search_and_reason(recognized_individuals, prediction):
    # retrieves knowledge from the ontology based on recognized individuals and predictions
    # if "product_availability" is detected, check if any of the recognized individuals map to "product"
    if 'product_availability' in prediction[0].__str__():
        for ind in recognized_individuals:
            if individuals[ind][1] == 'Product':
                context_individual.append(onto.search(iri=individuals[ind][0]).first())
                # context_individual[0].label to display names along NLG module
                # context_individual[0].hat_Produktvariante to display next node leaves
        context_class = classes['Product']
    # need to distinguish between open and closed?
    return context_class, context_individual


def generate_answer(context_class, context_individual, prediction, possible_responses):
    # merges the ontology discoveries with replies
    if (context_class.name == 'Product') and ("product_availability" in prediction[0].__str__()):
        if len(context_individual) == 1:
            bot_reply = random.choice(possible_responses['_product_availability_one']) % dict(first = context[1][0].label.first())
        elif len(context_individual) == 2:
            bot_reply = random.choice(possible_responses['_product_availability_two']) % dict(first = context[1][0].label.first(), last=context[1][1].label.first())
        elif len(context_individual) > 2:
            many = ""
            for w in context[1]:
                many += str(w.label.first()) + ", "
            bot_reply = random.choice(possible_responses['_product_availability_many']) % dict(many=many)

    return bot_reply


# this section needs to be triggered before the user can converse with the chatbot
model = fasttext.load_model("ml_model/model_intent_detection.bin")
nlp = de_core_news_sm.load()
onto_path.append("ontology_material")
onto = get_ontology("GoodRelationsBluefinch_v2.owl")
onto.load()

possible_responses = defaultdict(list)
with open("ml_model/responses.csv", 'r', newline='') as f:
    reader = csv.reader(f, delimiter=';')
    next(reader) # toss headers
    for label, reply in reader:
        possible_responses[label].append(reply)

# load ontology classes and instances to enable better and faster searchability
classes = defaultdict(list)
for cl in onto.classes():
    classes[cl.name] = cl

individuals = defaultdict(list)
for individual in onto.individuals():
    individuals[individual.label.first()] = [individual.iri, individual.is_a.first().name]

context_class = []
context_individual = []

userText = "welche iphones hast du?"

# capitalize every first letter per word to increase noun detection
doc = nlp(userText.title())
nlp_output = defaultdict(list)
for token in doc:
    nlp_output[token.i] = [token.text, token.pos_, token.tag_, token.dep_, token.head.text]
# fuzzy search keys in individuals for possible hits, i.e. 'AmericanExpress' in individuals.keys()
# pass lowercase to model prediction, because training data is also lowercase so prediction is allergic to upper case
prediction = model.predict(doc.text.lower())
if (prediction[1].item() > .7) == True:
    # if the predicted label meets the criteria, classify sentence type is called
    # to see whether the result from the model is off; if it is off, jump to "else", if it is not
    # trigger noun extraction and individual lookup to find the matching noun and choose suiting response
    sentence_type = classify_sentence_type(nlp_output)
    if ((sentence_type in prediction[0].__str__()) or sentence_type == 'undefined') == True:
            nouns = noun_extraction(nlp_output)
            # in case no nouns are found, an empty list is returned from the lookup
            recognized_individuals = individual_lookup(nouns, sentence_type, userText)
            context = ontology_search_and_reason(recognized_individuals, prediction)
            context_class = context[0]
            context_individual = context[1]
            generate_answer(context_class, context_individual, prediction, possible_responses)

else:
    # return default response; write input + output to log
    print("Entschuldigung, das habe ich nicht ganz verstanden.")


# things to do:
# rewrite to various classes
# while you are at it, write unit tests for it
# delete chatterbot remnants

# to be written classes, inspired by the chatterbot code:
#
# class chatbot
#
# constructor (self, kwargs**) --> https://github.com/gunthercox/ChatterBot/blob/master/chatterbot/chatterbot.py
# search algorithms --> imported from search class
# logic adapter --> imported from logic adapter
#
# def
# get_response (self, statement, kwargs**) --> returns bots response
# statement --> imported from conversation class
# stores strings for responses and incoming statements and updates any response data (context?)
# generate_response (self, input_statement, kwargs**) --> replies to user
# calls process() in logic adapter class and combines results of multiple adapters
# learn_response (self, statement, previous_response) --> learn if statement provided is a valid response
# get_latest_response (self, conversation) --> returns latest response in a conversation
# we need to add nlp stuff somewhere


# class search
#
# constructor (self, chatbot, kwargs**)
# Levensthein and so on
# def
# search (self, input_statement, kwargs**)
# search for close matches to the input (instance search? ontology?)


# class logic adapter
#
# constructor (self, chatbot, kwargs**)
# search algorithm name
# maximum_similarity_threshold
# response_selection_method
#
# def
# process (self, statement, kwargs**) --> to be overwritten, logic to return a response to statement
# default_response


# class conversation
# statement contains 'in_response_to', 'search_in_response_to', 'created_at',
# 'conversation', pretty good stuff to think about!

