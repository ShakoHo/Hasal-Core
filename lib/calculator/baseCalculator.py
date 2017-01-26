class BaseCalculator(object):
    def __init__(self, **kwargs):
        print kwargs
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def run(self):
        pass
