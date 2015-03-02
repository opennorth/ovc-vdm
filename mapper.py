# -*- coding: utf-8 -*-

import json
import csv
import time
import random
import re
import urllib2
import sys
from datetime import datetime
from app import app
import pytz
from slugify import slugify


def field_mapper_pol_mtl(row):
    my_release = json.load(open('templates/release.json'))
    eastern = pytz.timezone('US/Eastern')
    contract_date = eastern.localize(datetime.strptime(row[7], "%Y-%m-%d"))

    # TODO: USE NO DOSSIER OR NO DECISION? 
    my_release["ocid"] =  app.config["OCID_PREFIX"] + row[4]
    my_release["id"] =  row[4]

    #TODO: IL FAUT SUREMENT AJOUTER UN TIMEZONE
    my_release["date"] = contract_date.isoformat()
    my_release["buyer"]["name"] = row[2]
    my_release["buyer"]["identifier"]["id"] = slugify(row[2], to_lower=True)

    my_release["tender"]["id"] = row[6]

    #TODO: FAIT MAPPING SERVICE  => ACTIVITE
    my_release["tender"]["title"] = "Autre"

    if (row[2] in app.config["SERVICE_TO_ACTIVITY"]):
        my_release["tender"]["title"] = app.config["SERVICE_TO_ACTIVITY"][row[2]]

    my_release["tender"]["description"] = row[5]
    my_release["tender"]["items"][0]["description"] = row[3] + ". " + row[1]
    my_release["tender"]["items"][0]["id"] = row[6]


    my_release["tender"]["value"] = float(row[8].replace(',','.'))

    #TODO : Pass the procuring entity as a paramter of the mapper?
    my_release["tender"]["procuringEntity"]["name"] = 'Conseil municipal'


    my_release["awards"][0]["id"] = row[4]
    my_release["awards"][0]["date"] = contract_date.isoformat()

    my_release["awards"][0]["value"]["amount"] = float(row[8].replace(',','.'))
    my_release["awards"][0]["suppliers"][0]["name"] = row[0]
    my_release["awards"][0]["suppliers"][0]["identifier"]["id"] = slugify(row[0], to_lower=True)
    my_release["awards"][0]["items"][0]["id"] = row[6]

    #TODO : Pass the procuring entity as a paramter of the mapper?
    my_release["awards"][0]["items"][0]["description"] = row[5]

    return my_release


def field_mapper_fonc_mtl(row):
    my_release = json.load(open('templates/release.json'))
    eastern = pytz.timezone('US/Eastern')
    contract_date = eastern.localize(datetime.strptime("2015-01-01", "%Y-%m-%d"))

    # TODO: USE NO DOSSIER OR NO DECISION? 
    my_release["ocid"] =  app.config["OCID_PREFIX"] + row[1]
    my_release["id"] =  re.sub("[^0-9]", "", row[1] + row[6]) 

    #TODO: IL FAUT SUREMENT AJOUTER UN TIMEZONE
    my_release["date"] = contract_date.isoformat()
    my_release["buyer"]["name"] = row[4]
    my_release["buyer"]["identifier"]["id"] = slugify(row[4], to_lower=True)

    my_release["tender"]["id"] = row[1]

    #TODO: FAIT MAPPING SERVICE  => ACTIVITE
    my_release["tender"]["title"] = "Autre"

    if (row[2] in app.config["SERVICE_TO_ACTIVITY"]):
        my_release["tender"]["title"] = app.config["SERVICE_TO_ACTIVITY"][row[4]]

    my_release["tender"]["description"] = row[5]
    my_release["tender"]["items"][0]["description"] = row[3]
    my_release["tender"]["items"][0]["id"] = row[1]

    my_release["tender"]["value"] = float(row[6].replace(',','.'))

    #TODO : Pass the procuring entity as a paramter of the mapper?
    my_release["tender"]["procuringEntity"]["name"] = 'Fonctionnaires Ville de Montréal'


    my_release["awards"][0]["id"] = row[1]
    my_release["awards"][0]["date"] = contract_date.isoformat()

    my_release["awards"][0]["value"]["amount"] = float(row[6].replace(',','.'))
    my_release["awards"][0]["suppliers"][0]["name"] = row[0]
    my_release["awards"][0]["suppliers"][0]["identifier"]["id"] = slugify(row[0], to_lower=True)
    my_release["awards"][0]["items"][0]["id"] = row[1]

    #TODO : Pass the procuring entity as a paramter of the mapper?
    my_release["awards"][0]["items"][0]["description"] = row[3]

    return my_release

class Mapper():

    def __init__(self, source, options={}):
 
        if re.match("^http", source.url) == None:
            self.cr = csv.reader(open(source.url))
        else:
            self.cr = csv.reader(urllib2.urlopen(source.url))
        self.output = {}
        self.release_list= []
        self.mapper_type = source.mapper
        self.csv_skip = 1
        if hasattr(source, "skip_lines") and source.skip_lines != None:
            self.csv_skip  = source.skip_lines




    def to_ocds(self):

        custom_mapper = getattr(sys.modules[__name__],  self.mapper_type)

        i = 0
        for row in self.cr:
            if i >= self.csv_skip:
                self.release_list.append(custom_mapper(row))
            else:
                print("skip %s" % row)
    
            i = i+1

        self.output["releases"] = self.release_list 
        #print(self.output["releases"])
        return self.output

        #print json.dumps(self.output)

