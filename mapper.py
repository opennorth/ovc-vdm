import json
import csv
import time
import random
import re
import urllib2
import sys


def field_mapper_fonc(row):
    my_release = json.load(open('templates/release.json'))

    my_release["ocid"] = row[1] + str(random.randrange(1, 100000))
    my_release["buyer"]["id"]["name"] = row[4]
    my_release["formation"]["notice"]["id"] = row[5]
    my_release["formation"]["itemsToBeProcured"][0]["description"] = row[3]
    my_release["formation"]["itemsToBeProcured"][0]["classificationDescription"] = row[5]
    
    

    my_release["formation"]["totalValue"] = float(row[6].replace(',','.'))
    my_release["formation"]["procuringEntity"]["id"]["name"] = 'Fonctionnaires Ville Centrale'
    my_release["awards"][0]["awardID"] = re.sub("[^0-9]", "",row[1] )+ str(random.randrange(1, 100000))
    my_release["awards"][0]["awardDate"] = "2014-12-31"



    my_release["awards"][0]["awardValue"]["amount"] = float(row[6].replace(',','.'))
    my_release["awards"][0]["suppliers"][0]["id"]["name"] = row[0]
    my_release["awards"][0]["itemsAwarded"][0]["description"] = row[3]
    my_release["awards"][0]["itemsAwarded"][0]["classificationDescription"] = row[5]

    return my_release

def field_mapper_pol_mtl(row):
    my_release = json.load(open('templates/release.json'))

    # TODO: USE NO DOSSIER OR NO DECISION? 
    my_release["ocid"] = row[4]
    my_release["buyer"]["id"]["name"] = row[2]
    my_release["formation"]["notice"]["id"] = row[6]
    my_release["formation"]["itemsToBeProcured"][0]["description"] = row[5]

    #TODO Using the direction, but ideally it would be the category
    my_release["formation"]["itemsToBeProcured"][0]["classificationDescription"] = row[3]
    
    

    my_release["formation"]["totalValue"] = float(row[8].replace(',','.'))

    #TODO : Pass the procuring entity as a paramter of the mapper?
    my_release["formation"]["procuringEntity"]["id"]["name"] = 'Conseil municipal'
    my_release["awards"][0]["awardID"] = row[4]
    my_release["awards"][0]["awardDate"] = row[7]



    my_release["awards"][0]["awardValue"]["amount"] = float(row[8].replace(',','.'))
    my_release["awards"][0]["suppliers"][0]["id"]["name"] = row[0]
    my_release["awards"][0]["itemsAwarded"][0]["description"] = row[5]

    #TODO : Pass the procuring entity as a paramter of the mapper?
    my_release["awards"][0]["itemsAwarded"][0]["classificationDescription"] = row[3]

    return my_release

class Mapper():

    def __init__(self, url, mapper_type, options={}):
 
        if re.match("^http", url) == None:
            self.cr = csv.reader(open(url))
        else:
            self.cr = csv.reader(urllib2.urlopen(url))
        self.output = {}
        self.release_list= []
        self.mapper_type = mapper_type
        self.csv_skip = 1
        if "skip_lines" in options:
             self.csv_skip  = options["skip_lines"]




    def to_ocds(self):

        custom_mapper = getattr(sys.modules[__name__],  self.mapper_type)

        i = 0
        for row in self.cr:
            if i >= self.csv_skip:
                self.release_list.append(custom_mapper(row))
    
            i = i+1

        self.output["releases"] = self.release_list 
        #print(self.output["releases"])
        return self.output

        #print json.dumps(self.output)

