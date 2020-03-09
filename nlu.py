# parse input from the user (Natural Language Understanding)
# https://explosion.ai/blog/german-model
# https://github.com/adbar/German-NLP#Text-corpora
import spacy
import de_core_news_sm

userText = "welche iphones hast du?" # welche iphones gibt es? habt ihr iphone 11?
# wie groß ist der speicher? wie viel speicher hat es?
# was ist der vorteil von pro? warum ist pro besser?
# was kostet das? wie teuer ist das? was ist der preis?
# kann ich mit mastercard bezahlen?

nlp = de_core_news_sm.load()
# capitalize every first letter per word to increase noun detection
doc = nlp(userText.title())

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

import fasttext
help(fasttext.FastText)
model = fasttext.train_supervised(input="cooking.train", epoch = 25)
model.predict("Which baking dish is best to bake a banana bread ?")
model.predict("Why not put knives in the dishwasher?")