#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
from lib.xml_parser import xml_parser
from lib.tools import tools
from lib.liblinear import classifier
doc = "For index table builduing you need\nto provide text file with stop words\nwhich name MUST be 'stop_words.txt'\n\n" \
      "This util generate index table\nby default, but you can provide\nyour own through option -ext-index"

def parse_args():
    """parse arguments"""
    parser = argparse.ArgumentParser(description=doc, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers()
    parser_vectors = subparsers.add_parser('vectors', help="Generate vectors file from index and xml")
    parser_train = subparsers.add_parser('train', help="Training classifier from vectors file; Output model file")
    parser_predict = subparsers.add_parser('predict', help="Predict")
    parser_tokenize = subparsers.add_parser('tokenize', help="Tokenization")

    #Vectors generating arguments
    parser_vectors.add_argument('-xml', help='Path to XML-file', metavar='PATH_TO_XML', required=True)
    parser_vectors.add_argument('-csv', help='Path to dictionary CSV-file', metavar='PATH_TO_CSV', required=True)
    parser_vectors.add_argument('-ext-index', help="Path to index-file", metavar="PATH_TO_INDEX")
    parser_vectors.add_argument('-sw', help="Path to stop-words-file", metavar="PATH_TO_STOP_WORDS_FILE", required=True)
    parser_vectors.add_argument('-i', help="Output index to file", metavar="FILENAME")
    parser_vectors.add_argument('-o', help='Output vectors to file', metavar='FILENAME')
    parser_vectors.set_defaults(func=generate_vectors)

    #Classifier training arguments
    parser_train.add_argument('-data', help="Path to data-file", metavar="PATH_TO_DATA_FILE", required=True)
    parser_train.add_argument('-params', help="Train params")
    parser_train.add_argument('-o', help="Output model to file", metavar="FILENAME")
    parser_train.set_defaults(func=train)

    #Classifier prediction arguments
    parser_predict.add_argument('-test-data', help="Path to test data-file", metavar="PATH_TO_DATA_FILE", required=True)
    parser_predict.add_argument('-model', help="Path to model file", metavar="PATH_TO_MODEL", required=True)
    parser_predict.add_argument('-params', help="Prediction params")
    parser_predict.add_argument('-o', help="Output result to file", metavar="FILENAME", required=True)
    parser_predict.add_argument('-ow', help="Overwrite xml-file with predicted labels", metavar="PATH_TO_XML")
    parser_predict.set_defaults(func=predict)

    #Tokenization arguments
    parser_tokenize.add_argument('-xml', help="Path to xml", metavar="PATH_TO_XML", required=True)
    parser_tokenize.add_argument('-o', help="Path to new file", metavar="FILENAME", required=False)
    parser_tokenize.set_defaults(func=tokenize)

    args = parser.parse_args()
    return args

def generate_vectors(args):
    """generate vectors

        :rtype list
    """
    t = tools.TextAnalyzer(args.csv, args.xml, args.sw)
    if args.i:
        t.write_index(args.i)

    return t.build_vectors(args.ext_index, args.o)

def train(args):
    """train classifier"""
    cls = classifier.Classifier()
    cls.train(args.data, args.o, args.params)

def predict(args):
    """get classifier prediction"""
    cls = classifier.Classifier()
    cls.predict(args.test_data, args.model, args.o, args.params)
    if args.ow:
        parser = xml_parser.XmlParser(args.ow,)
        parser.rewrite_columns_companies(args.o, args.ow)

def tokenize(args):
    """tokenize xml"""
    parser = xml_parser.XmlParser(args.xml)
    parser.tokenize(args.xml, args.o)


def main():
    args = parse_args()
    args.func(args)

main()


