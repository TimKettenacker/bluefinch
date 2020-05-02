import chatbot
import fasttext

class Trainer(object):
    """
    Trains the model used for predicting the intent of a user's input.

    """
    def __init__(self, chatbot, **kwargs):
        self.chatbot = chatbot

    def __str__(self):
        return "This is an instance of class trainer"


    def train_model(self):
        """
        Trains the model used for predicting bot response's using the data defined
        in "training_set_intents".
        This methods needs to be triggered prior to a conversation.
        :return: model object
        """
        model = fasttext.train_supervised(input="ml_model/training_set_intents", lr=0.9,
                                          epoch=25, wordNgrams=2)
        model.save_model("ml_model/model_intent_detection.bin")
        return model

    def predict_intent(self, model, input):
        """
        Takes a model and an input string and returns a prediction of the latter based on the
        former.
        :param model: A model object, pre-trained by train_model()
        :param input: a string, passed on from the user input on the UI, either pre-processed
        or directly. A lower-cased version is used to predict the outcome.
        :return: a tuple; the first tuple value contains the predicted output label, the second
        tuple value contains an array with only element (float), stating the probability of the
        correct prediction of the output label.
        """
        return model.predict(input.lower())
