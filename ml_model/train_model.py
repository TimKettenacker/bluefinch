import fasttext
model = fasttext.train_supervised(input="training_set_intents", lr=0.9, epoch = 25, wordNgrams=2)
model.save_model("model_intent_detection.bin")