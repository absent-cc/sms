import pickle
def writeToPickle(object, path):
    with open(path, 'wb') as f:
        pickle.dump(object, f)