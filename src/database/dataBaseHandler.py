from dataStructs import Student, Teacher
import pickle

class DatabaseHandler:
    directory: dict[Teacher: list[Student]]
    
    def __init__(self, directory_path):
        self.directory_path = directory_path
        # self.directory = self.readSavedDirectory(directory_path)
        # print(self.directory)
    
    def readSavedDirectory(self, path):
        if path.lower().endswith(('.pkl')):
            with open(path, 'rb') as f:
                return pickle.load(f)
        else:
            raise Exception('Directory Path is not a pickle file')
    
    def writeDirectory(self, directory, path='data/directory.pkl'):
        with open(path, 'wb') as f:
            pickle.dump(directory, f)