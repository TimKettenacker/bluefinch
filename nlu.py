# parse input from the user (Natural Language Understanding)
# https://explosion.ai/blog/german-model
# https://github.com/adbar/German-NLP#Text-corpora
from owlready2 import *
import fasttext
import de_core_news_sm
from collections import defaultdict
from fuzzywuzzy import process, fuzz


def classify_sentence_type(doc, nlp_output):
    # classifies sentence types according to shallow parsing results
    sentence_type = ''
    doc_json = doc.to_json()

    open_question_pointers = ['PWAT', 'PWAV', 'PWS'] # which, when, what, ...
    closed_question_pointers = ['VMFIN', 'VVFIN', 'VVIMP', 'VAFIN'] # könnt, habt, ...
    if nlp_output[0][2] in open_question_pointers:
        sentence_type = 'open_question'
    if nlp_output[0][2] in closed_question_pointers and doc_json['text'].endswith('?'):
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


def individual_lookup(noun):
    # compares detected nouns with instance data from the ontology
    match_list = process.extractBests(noun, individuals.keys(), scorer=fuzz.UWRatio,
                                      score_cutoff=75, limit=len(individuals))
    # depending on the prediction, the caller may filter on all that made the cut in the answer generation
    return match_list


# this section needs to be triggered before the user can converse with the chatbot
model = fasttext.load_model("ml_model/model_intent_detection.bin")
nlp = de_core_news_sm.load()
onto_path.append("ontology_material")
onto = get_ontology("GoodRelationsBluefinch_v2.owl")
onto.load()

# have a twofold search to perform faster and yield better results;
# first, collect all individuals to fuzzy search detected entities against them (i.e. with fuzzywuzzy)
individuals = defaultdict(list)
for individual in onto.individuals():
    individuals[individual.label.first()] = [individual.iri, individual.is_a.first().name]
# second, a detected matching iri goes into ontology to retrieve node connections

userText = "welche iphones hast du?"

# capitalize every first letter per word to increase noun detection
doc = nlp(userText.title())
nlp_output = defaultdict(list)
for token in doc:
    nlp_output[token.i] = [token.text, token.pos_, token.tag_, token.dep_, token.head.text]
# do some nlp extraction to feed noun to individuals
# further may extend to look for predicates
# fuzzy search keys in individuals for possible hits, i.e. 'AmericanExpress' in individuals.keys()
# pass lowercase to model prediction, because training data is also lowercase so prediction is allergic to upper case
prediction = model.predict(doc.text.lower())
if (prediction[1].item() > .7) == True:
    # if the predicted label meets the criteria, classify sentence type is called
    # to see whether the result from the model is off; if it is off, jump to "else", if it is not
    # trigger noun extraction and individual lookup to find the matching noun and choose suiting response
    sentence_type = classify_sentence_type(doc, nlp_output)
    if ((sentence_type in prediction[0].__str__() == True) or sentence_type == 'undefined') == True:
            nouns = noun_extraction(nlp_output)
            # in case no nouns are found, an empty list is returned from the lookup
            recognized_individuals = individual_lookup(nouns)

else:
    # return default response; write input + output to log
    print("Entschuldigung, das habe ich nicht ganz verstanden")


# first, classify what the user wants to do, even if the product is already mentioned. Classify into
# sentence_types = greeting(opening, closing, politeness), chitchat, action(question, user_wish, imperative), ordinary
# if there is a clear match between entity of interest and ontology after classifying the intent,
# it is easier to reply back
# entity_of_interest - in ontology > narrow down question

def ontology_search_and_reason(recognized_individuals, prediction):
    resultSet = []
    # retrieves knowledge from the ontology based on entities and predictions
    if 'product_availability_open_question' in prediction[0].__str__():
        for m, n in individuals.items():
            if 'Product' in n:
                resultSet.append(m)
    return resultSet

individuals[recognized_individuals[1][0]][1] == 'Product'
t = onto.search(iri = individuals[recognized_individuals[1][0]][0]) # 'http://webprotege.stanford.edu/AppleIPhone11'
t = t.first()
t.get_properties()