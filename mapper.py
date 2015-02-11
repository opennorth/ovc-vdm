import json
import csv
import time
import random
import re

fonctionnaires = csv.reader(open('fonctionnaires.csv'))
the_dict = {}
output = []

def gen_json(row):

    my_release = json.load(open('empty_release.json'))

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
    #print (json.dumps(my_release))

    return my_release



for row in fonctionnaires:

    output.append(gen_json(row))
    #print ("*************************************************** J'obtiens ca:  ")
    #print (json.dumps(output))    

the_dict["releases"] = output

print json.dumps(the_dict)

