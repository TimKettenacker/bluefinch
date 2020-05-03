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

    def test_returned_content_noun_extraction_example1(self):
        test_nlp_instance = NaturalLanguageProcessor("test")
        test_nlp_output = test_nlp_instance.parse_input("Habt ihr das Iphone 11 Pro?")
        test_nouns_output = test_nlp_instance.noun_extraction(test_nlp_output)
        self.assertIn(test_nouns_output.lower(), 'Iphone Pro'.lower())

    def test_returned_content_noun_extraction_example2(self):
        test_nlp_instance = NaturalLanguageProcessor("test")
        test_nlp_output = test_nlp_instance.parse_input("Habt ihr Apples Iphone 11?")
        test_nouns_output = test_nlp_instance.noun_extraction(test_nlp_output)
        self.assertIn(test_nouns_output.lower(), 'Apples Iphone 11'.lower())

    def test_returned_content_noun_extraction_example3(self):
        test_nlp_instance = NaturalLanguageProcessor("test")
        test_nlp_output = test_nlp_instance.parse_input("Habt ihr Apples Iphone X?")
        test_nouns_output = test_nlp_instance.noun_extraction(test_nlp_output)
        self.assertIn(test_nouns_output.lower(), 'Apples Iphone X'.lower())

    def test_returned_content_noun_extraction_example4(self):
        test_nlp_instance = NaturalLanguageProcessor("test")
        test_nlp_output = test_nlp_instance.parse_input("Was für apple produkte habt ihr?")
        test_nouns_output = test_nlp_instance.noun_extraction(test_nlp_output)
        self.assertIn(test_nouns_output.lower(), 'Apple Produkte'.lower())

    def test_returned_content_noun_extraction_example5(self):
        test_nlp_instance = NaturalLanguageProcessor("test")
        test_nlp_output = test_nlp_instance.parse_input("Was für iphones habt ihr?")
        test_nouns_output = test_nlp_instance.noun_extraction(test_nlp_output)
        self.assertIn(test_nouns_output.lower(), 'Iphones'.lower())


if __name__ == "__main__":
    unittest.main()
