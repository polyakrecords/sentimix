__author__ = 'polyakrecords'

import xml.etree.ElementTree as ET
import subprocess

class NotFoundException(Exception):
    def __init__(self, message):
        super(NotFoundException, self).__init__(message)

class XmlParser:
    def __init__(self, path):
        try:
            self.__tree = ET.parse(path)
            self.__tables = self.get_tables()
            self.__companies = self.get_columns_companies()
        except IOError:
            print "ERROR: There is no such file! Please check the path."
            raise SystemExit
        except ET.ParseError:
            print "ERROR: Cannot parse XML-file! It seems like you provide a damaged version..."
            raise SystemExit

    def get_tree(self):
        """return xml-tree"""
        return self.__tree

    def get_tables(self):
        """return tables from parsed xml

        :rtype list
        """
        tree = self.get_tree()
        root = tree.getroot()
        tables = []

        for database in root.findall('database'):
            for table in database.findall('table'):
                tables.append(table)
        return tables

    def __get_text(self, table_idx):
        """return text from table

        :rtype string
        """
        table = self.__tables[table_idx]
        for column in table.findall('column'):
            if column.get('name') == 'text':
                return column.text
        raise NotFoundException

    def get_text_list(self):
        """return union of all texts in xml

        :rtype list
        """
        tables_len = len(self.__tables)
        return [self.__get_text(idx) for idx in range(tables_len)]


    def get_label(self, table_idx):
        """return label if it present in table, otherwise return 0

        :rtype int
        """
        table = self.__tables[table_idx]
        for column in table.findall('column'):
            if column.get('name') in self.__companies and column.text != 'NULL':
                try:
                    return int(column.text)
                except ValueError:
                    return 0

    def get_columns_companies(self):
        """return companies names from xml

        :rtype list
        """
        #Here we take first table and parse all column names after column with text
        table = self.__tables[0]
        columns = [column for column in table.findall('column')]
        text_column_index = 0
        for column in columns:
            if column.get('name') == 'text':
                text_column_index = columns.index(column)
                break
        return [column.get('name') for column in columns[1 + text_column_index:]]

    def rewrite_columns_companies(self, labels, filename):
        """rewrite column companies labels from given labels list"""
        try:
            with open(labels) as f:
                labels_list = f.read().splitlines()
        except IOError:
            raise Exception('ERROR: Seems like you do not provide xml file!')

        for idx, label in enumerate(labels_list):
            table = self.__tables[idx]

            for column in table.findall('column'):
                if column.get('name') in self.__companies and column.text != 'NULL':
                    column.text = label

        with open(filename, 'w+') as f:
            self.__tree.write(f, encoding="utf-8")

    def tokenize(self, filename, new_filename=False):
        """tokenize text in file"""
        for idx, string in enumerate(self.get_text_list()):
            table = self.__tables[idx]

            for column in table.findall('column'):
                if column.get('name') == 'text':
                    output = subprocess.check_output("echo '" + column.text + "' | greeb", shell=True)
                    text_list = [s.decode("utf-8") for s in output.splitlines()]
                    column.text = " ".join(text_list)
        if new_filename:
            name = new_filename
        else:
            name = filename
        with open(name, 'w+') as f:
            self.__tree.write(f, encoding="utf-8")


