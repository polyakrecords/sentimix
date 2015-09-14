# -*- coding: UTF-8 -*-

__author__ = 'polyakrecords'
import numpy as np
from lib.xml_parser import xml_parser
import re

class TextAnalyzer:
    def __init__(self, csv_path, xml_path, stop_words_path):
        self.csv_path = csv_path
        self.xml_path = xml_path
        self.parser = xml_parser.XmlParser(self.xml_path)
        self.index = self.build_index(stop_words_path)

    def write_index(self, path):
        """write index to file """
        i = [word for idx, word in enumerate(self.index)]
        data = "\n".join(i)
        file = open(path, 'w+')
        file.write(data.encode("utf-8"))

    def output_data(self, data, output):
        """output data to file """
        if output:
            file = open(output, 'w+')
            file.write(data)
        return

    def parse_csv(self):
        """parse csv-file

        :rtype list
        """

        try:
            self.dict = np.genfromtxt(self.csv_path, skip_header=1, delimiter=" ", dtype="str", comments=None)
        except IOError:
            print "ERROR: There is no such file! Please check the path."

        regex = re.compile(
            "^(?P<index>.*?);(?P<word>.*?);(?P<weight>\d+?),(?P<weight_dec>\d+?)$"
        )
        return [[regex.match(string).group("index"), regex.match(string).group("word").decode("utf-8"), \
                       float(regex.match(string).group("weight") + '.' + regex.match(string).group("weight_dec"))] \
                      for string in self.dict]

    def build_index(self, stop_words_path, output=False):
        """build index

        :rtype list
        """
        parser = self.parser
        stop_words = []
        try:
            with open(stop_words_path) as f:
                stop_words = [string.decode("utf-8").lower() for string in f.read().splitlines()]
        except IOError:
            raise Exception('ERROR: There is no stop-words file! Did you forget to add it?')

        index = []
        for string in parser.get_text_list():
            for idx, word in enumerate(string.split()):
                lword = word.lower()
                #TODO: get this shit outta here!!!!
                if lword not in stop_words and lword + ' 1' not in index:
                    #default weight == 1
                    index.append(lword + ' 1')
        index = [str(idx + 1) + ' ' + word for idx, word in enumerate(index)]
        if output:
            data = "\n".join(index)
            self.output_data(data.encode("utf-8"), output)
        return index

    def build_vectors(self, ext_index_path=False, output=False):
        """build vectors

        :rtype list
        """
        parser = self.parser
        dictionary = self.parse_csv()
        if ext_index_path:
            try:
                with open(ext_index_path) as f:
                    regex = re.compile("^(?P<num>.*?) (?P<word>.*?) (?P<weight>\d+?)$")
                    index = [str(idx + 1) + ' ' + regex.match(string).group("word").lower().decode("utf-8") + " " +
                             regex.match(string).group("weight") for idx, string in enumerate(f.read().splitlines())]
            except IOError:
                raise Exception("ERROR: Can't find index file! Did you provide the right name?")
        else:
            index = self.index
        index_words = [string.split(" ")[1] for string in index]
        vectors = []
        for string in parser.get_text_list():
            string_list = string.split()
            index_vector = []

            for word in string_list:
                try:
                    word_idx = index_words.index(word.lower())
                    weight = index[word_idx].split(" ")[2]
                    index_vector.append(str(word_idx + 1) + ":" + str(weight))
                except ValueError:
                    continue
            # removing dupes in list
            index_vector = list(set(index_vector))
            index_vector = [str(num) for num in self.sort(index_vector)]
            
            if len(index_vector) and int(self.dict_match_words(string_list, dictionary)):
                index_vector.extend([str(len(index) + 1) + ':' + self.dict_match_words(string_list, dictionary), \
                                     str(len(index) + 2) + ':' + self.sum_weights(string_list, dictionary), \
                                     str(len(index) + 3) + ':' + self.max_weight(string_list, dictionary)])

            vectors.append(index_vector)

        vectors = [[str(parser.get_label(idx))] + vector for idx, vector in enumerate(vectors)]

        if output:
            data = ''
            for vector in vectors:
                data += " ".join(vector) + "\n"
            self.output_data(data, output)
        return vectors

    def sort(self, vector):
        """sort vectors list by vectors coordinates

        :rtype list
        """
        n = 1
        while n < len(vector):
            for i in range(len(vector) - n):
                if int(vector[i].split(":")[0]) > int(vector[i+1].split(":")[0]):
                    vector[i], vector[i+1] = vector[i+1], vector[i]
            n += 1
        return vector


    def dict_match_words(self, text_list, dictionary_list):
        """return amount of values from list which matches dictionary words

        :rtype string
        """
        return str(len(([float(dictionary[2]) for dictionary in dictionary_list if dictionary[1] in text_list])))

    def sum_weights(self, text_list, dictionary_list):
        """return weight sum of values from list

        :rtype string
        """
        return str(np.sum([float(dictionary[2]) for dictionary in dictionary_list if dictionary[1] in text_list]))

    def max_weight(self, text_list, dictionary_list):
        """return max weight of values in list

        :rtype string
        """
        try:
            return str(max([float(dictionary[2]) for dictionary in dictionary_list if dictionary[1] in text_list]))
        except ValueError:
            return str(0)

