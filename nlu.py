# parse input from the user (Natural Language Understanding)
# https://explosion.ai/blog/german-model
# https://github.com/adbar/German-NLP#Text-corpora
from owlready2 import *
import fasttext
import de_core_news_sm
from collections import defaultdict
from fuzzywuzzy import process, fuzz


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


def noun_extraction(doc):
    # automatic entity recognition does not work well for German, hence, I go for pos rules
    doc_json = doc.to_json()
    poss = []
    for i in range(0, len(doc_json['tokens'])):
        pos = doc_json['tokens'][i]['pos']
        poss.append(pos)

    noun_combo = {
        0: ['PROPN', 'NOUN'],
        # a proper noun followed by a noun like "Apple Iphone" is most likely yielding the best match
        1: ['NOUN', 'X'],
        # a noun followed by a letter or digit like is most likely something like "Iphone X"
        2: ['NOUN', 'NUM'],
        # a noun followed by a letter or digit like is most likely something like "Iphone 11"
        3: ['PROPN'],
        # a proper noun like "Apple" is the least specific fallback
        4: ['NOUN']
        # a noun like "Iphone" is the least specific fallback
    }

    for a in noun_combo:
        ix = get_sequence_index(noun_combo[a], poss)
        if ix != -1:
            break

    # returns '?' if no noun is present
    if len(noun_combo[a]) > 1:
        return doc[ix].text + ' ' + doc[ix+1].text
    else:
        return doc[ix].text


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
# do some nlp extraction to feed noun to individuals
# further may extend to look for predicates
# fuzzy search keys in individuals for possible hits, i.e. 'AmericanExpress' in individuals.keys()
# pass lowercase to model prediction, because training data is also lowercase so prediction is allergic to upper case
prediction = model.predict(doc.text.lower())
if (prediction[1].item() > .7) == True:
    # if the predicted label meets the criteria, classify sentence type is called
    # to see whether the result from the model is off; if it is off, jump to "else", if it is not
    # trigger noun extraction and individual lookup to find the matching noun and choose suiting response
    sentence_type = classify_sentence_type(doc)
    if ((sentence_type in prediction[0].__str__() == True) or sentence_type == 'undefined') == True:
            noun = noun_extraction(doc)
            # in case no nouns are found, an empty list is returned from the lookup
            recognized_individuals = individual_lookup(noun)

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