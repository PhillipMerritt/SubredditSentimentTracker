from abc import ABC, abstractmethod

# add an instance of your model to this once you have defined it
models = []

# all added sentiment analysis models must be wrapped 
# in a class that inherits from this class to enforce 
# a common api between different models
class baseSentimentModel(ABC):
    def __init__(self, name, model):
        self.name = name
        self.model = model

    # this is the only required method
    # it should take the text and return the predicted
    # sentiment as a number between [-1, 1] where
    # 1 is maximally positive, 0 is nuetral, and -1 is maximally negative
    @abstractmethod
    def predict(self, text):
        pass

"""
example of this:

class myModel(baseSentimentModel):
    # this example is a categorical model
    # so the values must be converted to numbers
    def predict(self, text):
        pred = self.model.evaluateSentiment(text)

        if pred == 'positive':
            return 1.0
        elif pred == 'nuetral':
            return 0.0
        else:
            return -1.0

models.append(myModel('example model', somePackage.model))
"""