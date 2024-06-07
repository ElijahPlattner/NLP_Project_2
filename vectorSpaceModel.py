import csv
import re
import copy
from collections import Counter
import math

FILENAME = "anti-lgbt-cyberbullying.csv"


def get_data_from_CSV(negative):
    with open(FILENAME, encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        data = {}
        ids = []
        text = ""
        indicator = '1'
        if (negative == False):
            indicator = '0'
        for row in reader:
            if (row[2] == indicator):
                ids.append(row[0])
                text = row[1]
                text = re.sub(r'\b\'s\b', '', text)
                text = re.sub(r'\b\’s\b', '', text)
                text = re.sub( r'[^\w\s\']', '', text)
                text = text.lower()
                text = text.split(" ")
                data[row[0]] = text
    return(data, ids)

def create_dict(data):
    dict_nlp = {}

    for key, element in data.items():
        for word in element:
            if len(word) > 0 and word in dict_nlp.keys():
                dict_nlp[word].append(key)
            else:
                dict_nlp[word] = [key]
        
    dict_nlp = dict(sorted(dict_nlp.items()))

    for key, value in dict_nlp.items():
        dict_nlp[key] = [len(value), value]
    return dict_nlp

class VectorSpaceModel:

    def __init__(self, dict_nlp, ids,) -> None:
        self.dict_nlp_og = dict_nlp
        self.ids_og = ids
        self.dict_nlp = {}
        self.ids = []

    def prepare_query(self, query):
        query = re.sub(r'\b\'s\b', '', query)
        query = re.sub(r'\b\’s\b', '', query)
        query = re.sub( r'[^\w\s\']', '', query)
        query = query.lower()
        return query.split(" ")
    
    def append_query_to_dict(self, query):
        self.dict_nlp = copy.deepcopy(self.dict_nlp_og)
        self.ids = copy.deepcopy(self.ids_og)
        for word in query:
            if len(word) > 0 and word in self.dict_nlp.keys():
                self.dict_nlp[word][1].append("query")
                self.dict_nlp[word][0] = self.dict_nlp[word][0] + 1
            else:
                self.dict_nlp[word] = [1, ["query"]]
        self.ids.append("query")

    def create_weights_matrix(self):
        weights_matrix = {}
        max_f = 1
        nb_entries = len(self.ids)
        for key, value in self.dict_nlp.items():
            if value[0] > max_f:
                max_f = value[0]
        for key, value in self.dict_nlp.items():
            tmp = []
            counter = Counter(value[1])
            for id in self.ids:
                if id in counter.keys():
                    tf = counter[id] / max_f
                    df = value[0]
                    idf = math.log2(nb_entries / df)
                    tmp.append(tf * idf)
                else:
                    tmp.append(0.0)
            weights_matrix[key] = tmp
        return weights_matrix
    
    def create_vector_space(self, matrix):
        res = []
        for i in range(0, len(self.ids)):
            tmp = []
            for key, value in matrix.items():
                tmp.append(value[i])
            res.append(tmp)
        return res
    
    def cosine_similarity(self, v1, v2):
        sumxx, sumxy, sumyy = 0, 0, 0
        for i in range(len(v1)):
            x = v1[i]; y = v2[i]
            sumxx += x*x
            sumyy += y*y
            sumxy += x*y
        return sumxy/math.sqrt(sumxx*sumyy)
    
    def ranked_search(self, vector_space):
        res = []
        ranked = []
        query = vector_space[-1]
        for i in range(0, len(self.ids_og)):
            res.append(self.cosine_similarity(vector_space[i], query))
        for i in range(0, len(res)):
            if res[i] != 0:
                ranked.append([self.ids_og[i], res[i]])
        ranked = sorted(ranked, key=lambda x: x[1], reverse=True)
        return ranked
    
    def mean_cosine_similarity(self, ranked):
        mean = -1
        max = 5
        if (len(ranked) < max):
            max = len(ranked)
        else:
            mean = 0
        for i in range (0, max):
            mean = mean + ranked[i][1]
        mean = mean / max
        return mean

    def evaluate(self, query_text):
        query = self.prepare_query(query_text)
        self.append_query_to_dict(query)
        matrix = self.create_weights_matrix()
        vspace = self.create_vector_space(matrix)
        ranked = self.ranked_search(vspace)
        mean = self.mean_cosine_similarity(ranked)
        return mean

def get_mean_cosine_similarity(text, dict_nlp={}, ids=[]):
        if (len(dict_nlp) == 0 or len(ids) == 0):
            data, ids = get_data_from_CSV(True)
            dict_nlp = create_dict(data)
        test = VectorSpaceModel(dict_nlp, ids)
        #above mean = 0.3, it can be considered as against the LGBT cause
        mean = test.evaluate(text)
        return mean