import json
import csv
import time
import random
import re
import urllib2

class Mapper():

    def __init__(self, url, options=None):
 
        fieldnames = ("provider","id","date","description", "service", "activity", "amount")
        if re.match("^http", url) == None:
            self.cr = csv.reader(open(url), fieldnames)
        else:
            self.cr = csv.reader(urllib2.urlopen(url), fieldnames)
        self.output = {}
        self.release_list= []
        #self.json_release_template = json.load(open('templates/release.json'))

    def row_mapper(self, row):
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

        #print ("*************************************************** J'ajoute ca : ")

        return my_release

    def csv_mapper(self):
        for row in self.cr:
            #print(row[0])
            self.release_list.append(self.row_mapper(row))

        self.output["releases"] = self.release_list 
        #print(self.output["releases"])
        return self.output

        #print json.dumps(self.output)

