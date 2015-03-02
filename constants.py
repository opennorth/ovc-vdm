# -*- coding: utf-8 -*-


#Mapping between buyer names (e.g services) and categories that people will understand
buyer_category = {
	"SERVICE DE CONCERTATION DES ARRONDISSEMENTS ET DES RESSOURCES MATÉRIELLES" : "Services administratifs",
	"SERVICE DES INFRASTRUCTURES, DU TRANSPORT ET DE L'ENVIRONNEMENT": "Meuh"

}

OCDS_META = {
	"uri" : '',
	"publishedDate" : '',
	"license": "https://creativecommons.org/licenses/by/4.0/",
	"publicationPolicy": 'http://donnees.ville.montreal.qc.ca/licence-2014/',
	"publisher" : { "name": 'Ville de Montréal',
					"address" : {	"streetAddress" : '275 Rue Notre-Dame Est, Montréal',
									"locality" : 'Montréal',
									"region" : 'QC',
									"postalCode" : 'H2Y1C6',
									"countryName" : 'Canada'
						},
					"contactPoint": {
	                    "name" : 'Bureau de la Ville Intelligente',
	                    "email" : 'villeintelligente@ville.montreal.qc.ca',
	                    "telephone" : '',
	                    "faxNumber" : '',
	                    "url" : 'http://ville.montreal.qc.ca/'
					}
		}
}
