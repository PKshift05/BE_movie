from pymongo import MongoClient

class Database:
    def __init__(self, db_name):
        self.client = MongoClient('mongodb+srv://quang05:quang123@cluster0.j5oyhc4.mongodb.net/?retryWrites=true&w=majority')
        self.db = self.client["Movie_Web"]
        self.users_collection = self.db['Users']
        self.movies_collection = self.db['Movies']