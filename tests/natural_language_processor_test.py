#!/usr/bin/env python3

from natural_language_processor import *
import unittest

class TestNLP(unittest.TestCase):

    def test_return_of_nlp_output(self):
        test_nlp_instance = NaturalLanguageProcessor("test")
        test_nlp_output = test_nlp_instance.parse_input("Habt ihr Iphones?")
        self.assertEqual(len(test_nlp_output), 4)

    def test_return_classify_sentence_type_closed(self):
        test_nlp_instance = NaturalLanguageProcessor("test")
        test_nlp_output = test_nlp_instance.parse_input("Habt ihr Iphones?")
        test_sentence_classification = test_nlp_instance.classify_sentence_type(test_nlp_output)
        self.assertEqual(test_sentence_classification, 'closed_question')

    def test_return_classify_sentence_type_open(self):
        test_nlp_instance = NaturalLanguageProcessor("test")
        test_nlp_output = test_nlp_instance.parse_input("Welche Iphones habt ihr?")
        test_sentence_classification = test_nlp_instance.classify_sentence_type(test_nlp_output)
        self.assertEqual(test_sentence_classification, 'open_question')

if __name__ == "__main__":
    unittest.main()
