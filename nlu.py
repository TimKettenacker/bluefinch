# parse input from the user (Natural Language Understanding)
# https://explosion.ai/blog/german-model
# https://github.com/adbar/German-NLP#Text-corpora
from owlready2 import *
import fasttext
import spacy
import de_core_news_sm
from collections import defaultdict

# this section needs to be triggered before the user can converse with the chatbot
model = fasttext.train_supervised(input="training_set_intents", epoch = 25)
nlp = de_core_news_sm.load()
onto_path.append("ontology_material")
onto = get_ontology("GoodRelationsBluefinch_v1.owl")
onto.load()

# create a dict for individuals
individuals = defaultdict(list)
for individual in onto.individuals():
    individuals[individual.name] = [individual.iri, individual.is_a.first(), individual.is_instance_of.first()]

userText = "welche iphones hast du?" # welche iphones gibt es? habt ihr iphone 11?
# wie groß ist der speicher? wie viel speicher hat es?
# was ist der vorteil von pro? warum ist pro besser?
# was kostet das? wie teuer ist das? was ist der preis?
# kann ich mit mastercard bezahlen?

# capitalize every first letter per word to increase noun detection
doc = nlp(userText.title())
# do some nlp extraction to feed noun to individuals
# further may extend to look for predicates
# fuzzy search keys in individuals for possible hits, i.e. 'AmericanExpress' in individuals.keys()
model.predict(doc.text)

print(' '.join('{word}/{tag}'.format(word.orth_, tag.tag_) for t in doc))

print('\n'.join('{child:<8} <{label:-^7} {head}'.format(child=t.orth_, label=t.dep_, head=t.head.orth_) for t in doc))

for chunk in doc.noun_chunks:
    print(chunk.text)

# first, classify what the user wants to do, even if the product is already mentioned. Classify into
# sentence_types = greeting(opening, closing, politeness), chitchat, action(question, user_wish, imperative), ordinary
# if there is a clear match between entity of interest and ontology after classifying the intent,
# it is easier to reply back
# entity_of_interest - in ontology > narrow down question

# The German dependency labels use the TIGER Treebank annotation scheme.
# OntoNotes 5 corpus to train NERs#
