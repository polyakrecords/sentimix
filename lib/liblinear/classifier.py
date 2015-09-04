__author__ = "polyakrecords"
from subprocess import call
import os

class Classifier:
    def __init__(self):
        self.__labels = [-1, 0 , 1]

    def train(self, vector, model, params = ''):
        """run classifiers train script"""
        cwd = os.getcwd()
        path_to_vector =  vector if os.path.isabs(vector) else os.path.join(cwd, vector)
        if model == None:
            model = ''
        path_to_model = model if os.path.isabs(model) else os.path.join(cwd, model)
        path_to_script = os.path.join(cwd, 'lib/liblinear/train')

        if not params == None:
            command = path_to_script + ' ' + params + ' ' + path_to_vector + ' ' + path_to_model
        else:
            command = path_to_script + ' ' + path_to_vector + ' ' + path_to_model
        call([command], shell=True)

    def predict(self,vector,model,result, params = ''):
        """run classifiers predict script"""
        cwd = os.getcwd()
        path_to_model = model if os.path.isabs(model) else os.path.join(cwd, model)
        path_to_vector = vector if os.path.isabs(vector) else os.path.join(cwd, vector)
        path_to_result = result if os.path.isabs(result) else os.path.join(cwd, result)
        path_to_script = os.path.join(cwd, 'lib/liblinear/predict')

        if not params == None:
            command = path_to_script + ' ' + params + ' ' + path_to_vector + ' ' + path_to_model + ' ' + path_to_result
        else:
            command = path_to_script + ' ' + path_to_vector + ' ' + path_to_model + ' ' + path_to_result
        call([command], shell=True)