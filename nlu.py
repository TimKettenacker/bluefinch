# parse input from the user (Natural Language Understanding)
# https://explosion.ai/blog/german-model
# https://github.com/adbar/German-NLP#Text-corpora
from owlready2 import *
import fasttext
import spacy
import de_core_news_sm
from collections import defaultdict


def classify_sentence_type(doc):
    # classifies sentence types according to shallow parsing results
    sentence_type = ''
    doc_json = doc.to_json()

    open_question_pointers = ['PWAT', 'PWAV', 'PWS'] # which, when, what, ...
    closed_question_pointers = ['VMFIN', 'VVFIN', 'VVIMP'] # könnt, habt, ...
    if (doc_json['tokens'][0]['tag'] in open_question_pointers) == True:
        sentence_type = 'open_question'
    if (doc_json['tokens'][0]['tag'] in closed_question_pointers) == True and doc_json['text'].endswith('?'):
        sentence_type = 'closed_question'

    return sentence_type


# this section needs to be triggered before the user can converse with the chatbot
model = fasttext.load_model("ml_model/model_intent_detection.bin")
nlp = de_core_news_sm.load()
onto_path.append("ontology_material")
onto = get_ontology("GoodRelationsBluefinch_v1.owl")
onto.load()

# have a twofold search to perform faster and yield better results;
# first, collect all individuals to fuzzy search detected entities against them (i.e. with fuzzywuzzy)
individuals = defaultdict(list)
for individual in onto.individuals():
    individuals[individual.name] = [individual.iri, individual.is_a.first(), individual.is_instance_of.first()]
# second, a detected matching iri goes into ontology to retrieve node connections

userText = "welche iphones hast du?"

# capitalize every first letter per word to increase noun detection
doc = nlp(userText.title())
# do some nlp extraction to feed noun to individuals
# further may extend to look for predicates
# fuzzy search keys in individuals for possible hits, i.e. 'AmericanExpress' in individuals.keys()
# pass lowercase to model prediction, because training data is also lowercase so prediction is allergic to upper case
prediction = model.predict(doc.text.lower())
if (prediction[1].item() > .7) == True:
    # if the predicted label meets the criteria, classify sentence type is called
    # to see whether the result from the model is off; if it is off, jump to "else", if it is not
    sentence_type = classify_sentence_type(doc)
    if (sentence_type in prediction[0].__str__()) == True:
    # trigger noun extraction and ontology lookup to find the matching noun and choose suiting response
        entity_extraction(doc)

else:
    # return default response; write input + output to log
    print("Entschuldigung, das habe ich nicht ganz verstanden")


# first, classify what the user wants to do, even if the product is already mentioned. Classify into
# sentence_types = greeting(opening, closing, politeness), chitchat, action(question, user_wish, imperative), ordinary
# if there is a clear match between entity of interest and ontology after classifying the intent,
# it is easier to reply back
# entity_of_interest - in ontology > narrow down question

def entity_extraction(doc):
    # automatic entity recognition does not work well for German, hence, I go for the pos and tags
    doc_json = doc.to_json()
    poss = []
    tags = []
    for i in range(0, len(doc_json['tokens'])):
        tag = doc_json['tokens'][i]['tag']
        pos = doc_json['tokens'][i]['pos']
        tags.append(tag)
        poss.append(pos)
    # Apple Iphone - tags: NE, NN; poss: PROPN
    # Iphone X - tags: NN, XY; poss: NOUN, X
    # Iphone 11 - tags: NN, CARD; poss: NOUN, NUM
    return tags, poss

def ontology_lookup():
    return
