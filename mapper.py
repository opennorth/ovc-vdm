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
import hashlib


def field_mapper_pol_mtl(row, source):
    my_release = json.load(open('templates/release.json'))
    eastern = pytz.timezone('US/Eastern')
    contract_date = eastern.localize(datetime.strptime(row[7], "%Y-%m-%d"))

    # TODO: USE NO DOSSIER OR NO DECISION? 
    key = hashlib.sha1(bytes(row[0] + row[2] + row[4] + row[7] + row[8])).hexdigest()
    my_release["ocid"] =  app.config["OCID_PREFIX"] + key
    my_release["id"] =  key

    #TODO: IL FAUT SUREMENT AJOUTER UN TIMEZONE
    my_release["date"] = contract_date.isoformat()
    my_release["buyer"]["name"] = row[2]
    my_release["buyer"]["identifier"]["id"] = slugify(row[2], to_lower=True)
    my_release["buyer"]["subOrganisationOf"]["name"] = row[3]


    #TODO: FAIT MAPPING SERVICE  => ACTIVITE
    my_release["subject"] = ["Autre"]

    if (row[2] in app.config["SERVICE_TO_ACTIVITY"]):
        my_release["subject"] = app.config["SERVICE_TO_ACTIVITY"][row[2]]


    #TODO : Pass the procuring entity as a paramter of the mapper?
    my_release["tender"]["procuringEntity"]["name"] = source.name
    my_release["tender"]["procuringEntity"]["identifier"]["id"] = slugify(source.name, to_lower=True)


    my_release["awards"][0]["id"] = row[4]
    my_release["awards"][0]["date"] = contract_date.isoformat()
    my_release["awards"][0]["repartition"] = row[1]

    my_release["awards"][0]["value"]["amount"] = float(row[8].replace(',','.'))
    my_release["awards"][0]["suppliers"][0]["name"] = row[0]
    my_release["awards"][0]["suppliers"][0]["identifier"]["id"] = slugify(row[0], to_lower=True)
    my_release["awards"][0]["items"][0]["id"] = row[6]

    #TODO : Pass the procuring entity as a paramter of the mapper?
    my_release["awards"][0]["items"][0]["description"] = row[5]

    return my_release

def field_mapper_fonc_mtl(row, source):
    my_release = json.load(open('templates/release.json'))
    eastern = pytz.timezone('US/Eastern')
    contract_date = eastern.localize(datetime.strptime(row[2], "%Y-%m-%d"))

    # TODO: USE NO DOSSIER OR NO DECISION? 
    key = hashlib.sha1(bytes(row[0] + row[1] + row[2] + row[4] + row[5] + row[7])).hexdigest()
    my_release["ocid"] =  app.config["OCID_PREFIX"] + key
    my_release["id"] =  key

    #TODO: IL FAUT SUREMENT AJOUTER UN TIMEZONE
    my_release["date"] = contract_date.isoformat()
    my_release["buyer"]["name"] = row[5]
    my_release["buyer"]["identifier"]["id"] = slugify(row[5], to_lower=True)


    #TODO: FAIT MAPPING SERVICE  => ACTIVITE
    my_release["subject"] = ["Autre"]

    if (row[5] in app.config["SERVICE_TO_ACTIVITY"]):
        my_release["subject"] = app.config["SERVICE_TO_ACTIVITY"][row[5]]


    #TODO : Pass the procuring entity as a paramter of the mapper?
    my_release["tender"]["procuringEntity"]["name"] = source.name
    my_release["tender"]["procuringEntity"]["identifier"]["id"] = slugify(source.name, to_lower=True)


    my_release["awards"][0]["id"] = row[1]
    my_release["awards"][0]["date"] = contract_date.isoformat()

    my_release["awards"][0]["value"]["amount"] = float(row[7].replace(',','.'))
    my_release["awards"][0]["suppliers"][0]["name"] = row[0]
    my_release["awards"][0]["suppliers"][0]["identifier"]["id"] = slugify(row[0], to_lower=True)
    my_release["awards"][0]["items"][0]["id"] = ""

    #TODO : Pass the procuring entity as a paramter of the mapper?
    description = row[4] + "."
    description += " " + row[6]
    description += "Approuvé par : " + row[3]
    my_release["awards"][0]["items"][0]["description"] = description

    return my_release

def field_mapper_subvention_mtl(row, source):
    my_release = json.load(open('templates/release.json'))
    eastern = pytz.timezone('US/Eastern')
    contract_date = eastern.localize(datetime.strptime(row[7], "%Y-%m-%d"))

    # TODO: USE NO DOSSIER OR NO DECISION? 
    key = hashlib.sha1(bytes(row[0] + row[2] + row[4] + row[7] + row[8])).hexdigest()
    my_release["ocid"] =  app.config["OCID_PREFIX"] + key
    my_release["id"] =  key
    my_release["tender"]["procurementMethodRationale"] =  source.type

    #TODO: IL FAUT SUREMENT AJOUTER UN TIMEZONE
    my_release["date"] = contract_date.isoformat()
    my_release["buyer"]["name"] = row[2]
    my_release["buyer"]["identifier"]["id"] = slugify(row[2], to_lower=True)
    my_release["buyer"]["subOrganisationOf"]["name"] = row[3]


    #TODO: FAIT MAPPING SERVICE  => ACTIVITE
    my_release["subject"] = ["Autre"]

    if (row[2] in app.config["SERVICE_TO_ACTIVITY"]):
        my_release["subject"] = app.config["SERVICE_TO_ACTIVITY"][row[2]]


    #TODO : Pass the procuring entity as a paramter of the mapper?
    my_release["tender"]["procuringEntity"]["name"] = source.name
    my_release["tender"]["procuringEntity"]["identifier"]["id"] = slugify(source.name, to_lower=True)


    my_release["awards"][0]["id"] = row[4]
    my_release["awards"][0]["date"] = contract_date.isoformat()
    my_release["awards"][0]["repartition"] = row[1]

    my_release["awards"][0]["value"]["amount"] = float(row[8].replace(',','.'))
    my_release["awards"][0]["suppliers"][0]["name"] = row[0]
    my_release["awards"][0]["suppliers"][0]["identifier"]["id"] = slugify(row[0], to_lower=True)
    my_release["awards"][0]["items"][0]["id"] = row[6]

    #TODO : Pass the procuring entity as a paramter of the mapper?
    my_release["awards"][0]["items"][0]["description"] = row[5]

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
        self.source = source
        self.csv_skip = 1
        if hasattr(source, "skip_lines") and source.skip_lines != None:
            self.csv_skip  = source.skip_lines




    def to_ocds(self):

        custom_mapper = getattr(sys.modules[__name__],  self.mapper_type)

        i = 0
        errors = []
        for row in self.cr:
            if i >= self.csv_skip:
                try:
                    self.release_list.append(custom_mapper(row, self.source))
                except (ValueError, IndexError) as e:
                    errors.append('Ligne #: %s  \tMessage: %s \nContenu de la ligne: %s' % (i+1, repr(e), row))   
    
            i = i+1

        message = ''
        if len(errors) > 0:
            app.logger.error("Erreur lors du chargement du fichier %s \n\n%s" %  (self.source.url, '\n'.join(errors)))

        self.output["releases"] = self.release_list 

        return self.output
