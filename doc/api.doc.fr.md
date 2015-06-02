# Documentation de l'interface programmable (API) des contrats de la Ville de Montréal

Le présent document décrit le fonctionnement de l'API développée pour rendre disponible les données de contrats et de subventions de la Ville de Montréal. L'API sert d'assise pour l'outil de visualisation des contrats et est également rendue disponible pour quiconque souhaite explorer les contrats.

Le code de l'API est disponible sous licence BSD 3 clauses sur [Github](https://github.com/opennorth/ovc-vdm) et peut être installé et modifié.

## Considérations générales

Quelques éléments généraux concernant l'API et son fonctionnement

L'API fonctionne selon la logique "[REST](http://en.wikipedia.org/wiki/Representational_state_transfer)", à savoir: 

- Chaque requête est indépendante des autres, le serveur ne gère pas de session ou d'état;
- L'API repose largement sur les fonctionnalités fournies par le protocole HTTP 1.1;
- Seul l'accès en lecture (GET) est possible;
- Conséquemment, l'ensemble des requêtes peuvent être réalisées à travers un navigateur web.


## Open Contracting Data Standard

Les listes de contrats sont formattées selon le format [Open Contracting Data Standard (OCDS)](http://ocds.open-contracting.org/standard/r/1__0__RC/en/standard/intro/) dans sa sérialisation en JSON. Un contrat ou une subvention est représenté dans la logique OCDS par le concept de `release`. De part la structure des données disponible, chaque `release` contient exactement un `award`, un `tender` et un `supplier`. 

En plus des attributs fournis dans la spécification officielle, les champs suivants ont été ajouté pour transmettre certaines informations spécifiques au contexte de la Ville de Montréal:

- `subject`: Liste de valeur en text libre obligatoire contenant les domaines d'activité selon la structure de la Ville de Montréal ("Infrastructure", "transport", etc.);
- `subOrganisationOf`: Champ optionnel pouvant contenir la direction dont dépend un service;
- `repartition`: Champ optionnel pouvant contenir l'information de répartition de la dépense (souvent la ville, l'agglomération, etc.)

Par ailleurs, le champ `procurementMethodRationale` est utilisé pour distinguer les contrats et les subventions.

De manière à rester cohérent, les autres points d'accès sont au format JSON mais selon une structure développée pour les besoins de l'API.

### Vocabulaire

Pour être cohérent avec le format OCDS, les attributs utilisent le vocabulaire anglais suivant:

- `release` : contrat ou subvention;
- `supplier` : fournisseur;
- `buyer`: donneur d'ouvrage (généralement un service de la Ville de Montréal);
- `procuring entity`: entité ayant, dans le cas de la ville de Montréal, approuvé le contrat (conseil municipal, fonctionnaire, etc.)

## Optimisation et fonctionnalités HTTP

Plusieurs fonctionnalités d'optimisation de contenu ont été mises en oeuvre dans l'API pour améliorer le temps de réponse:

- Cache interne: le premier accès à une ressource nécessite un calcul complet mais les appels suivants font appels à une cache interne. La cache est maintenue tant que des nouvelles données ne sont pas ajoutées;
- [eTag](http://en.wikipedia.org/wiki/HTTP_ETag): L'API fournit un attribut `etag` dans toutes les réponses. Un client peut renvoyer la valeur du etag dans une requête via l'attribut `If-None-Match`. Si le etag n'a pas changé, le serveur renvoie une réponse sans contenue et avec le code HTTP 304 signifiant que la ressource n'a pas changé, sinon la réponse en renvoyée au complet avec un code HTTP 200. L'attribut etag est calculé en utilisant un *hash* de la réponse.
- Compression gzip: Si la requête contient l'attribut `Accept-Encoding: gzip`, l'API retournera le contenu compressé en gzip, permettant généralement un gain de 80-90% en volume de données et donc en temps de téléchargement de la ressource.


Par ailleurs, l'API supporte la fonctionnalité [CORS](http://en.wikipedia.org/wiki/Cross-origin_resource_sharing): L'API envoie l'attribut HTTP `Access-Control-Allow-Origin: *` permettant d'envoyer des requêtes à partir d'un site web avec un autre nom de domaine que celui de l'API. 

## Point d'accès

L'API décompose les données de contrat selon plusieurs points d'accès. Les points d'accès peuvent être séparé en 3 catégories:
- La racine
- Les données de support
- Les contrats et les données de contrat groupées

### Point d'accès "racine"

URL: [/api/](./api/)

Le point d'accès racine contient les champs suivants:

- `endpoint`: Une liste de points d'accès pour les contrats
    - `url` : chemin relatif du point d'accès 
	- `description` : description du point d'accès
	- `accepted_parameters`: Liste des paramètres acceptés pour filtrer le contenu
	- `accepted_order_by`: Liste des valeurs acceptés pour ordonner les résultats
- `parameters_description`: Description des paramètres de filtrage acceptés
- `sources` : Liste des sources de données utilisées par l'API
- `releases_count` : Nombre de contrats actuellement gérés dans l'API
- `releases_value` : Valeur totale des contrats gérés dans l'API
- `supplier_count` : Nombre de fournisseurs listés dans l'API
- `buyer_count`: Nombre de donneurs d'ordre listés dans l'API
- `last_update` : Dernière date de mise à jour des données 

### Points d'accès de support

Les points d'accès de support permettent d'accéder à certaines listes utiles pour développer des visualisations et des interfaces basées sur l'API.

#### Liste des donneurs d'ouvrage et identifiants uniques

- URL: [/api/helpers/buyer_slugs](./api/helpers/buyer_slugs)
- Description: Fournit une liste complète des donneurs d'ouvrage avec leur nom et leur identifiant
- Champs:
    - `name`: Nom complet du donneur d'ouvrage
    - `slug`: Identifiant unique du donneur d'ouvrage (utilisé pour filtrer les données)

#### Liste fournisseurs et identifiants uniques

- URL: [/api/helpers/supplier_slugs](./api/helpers/supplier_slugs)
- Description: Fournit une liste complète des fournisserus avec leur nom et leur identifiant
- Champs
    - `name`: Nom complet du fournisseur
    - `slug`: Identifiant unique du fournisseur (utilisé pour filtrer les données)


#### Liste des domaines d'activité

- URL: /api/helpers/activity_list
- Description: Pour faciliter l'utilisation des données, les contrats sont regroupés par domaines d'activité (environnement, transport, etc.). Le point d'accès `activity_list` fournit la liste des domaines d'activités déclarés.
- Champs
    - `name`: Nom complet du domaine d'activité
    - `color_code`: Code couleur utilisé pour affiché le domaine d'activité dans l'interface graphique de la Ville de Montréal.


### Points d'accès aux données

Les points d'accès aux données permettent d'accéder à la liste des contrats ainsi qu'à obtenir certaines valeurs calculées par l'API, notamment permettant groupements selon différentes facettes.

#### Filtres et option de tri

Les points d'accès aux données partagent une série de paramètres permettant de filtrer et de trier le contenu. Ces paramètres doivent êtres fournis comme paramètre d'URL, par exemple [`/api/releases?q=test&date_gt=2014-01-01`](./api/releases?q=test&date_gt=2014-01-01)

La liste ci-dessous décrit la totalité des paramètres existants tandis qu'une liste des paramètres acceptés est fournie pour chaque point d'accès.

*Les filtres*

- `q`: Paramètre de recheche en texte libre. Plusieurs termes peuvent être fournis, séparé par un espace. Par exemple: [`/api/releases?q=excavation%20chaussée`](./api/releases?q=excavation%20chaussée). À noter que les accents sont acceptés mais que l'ensemble des recherches est effectué en mode 'désaccentué'.
- `highlight`: Paramètre permettant d'ajouter une balise `<em>` aux termes recherchés avec le paramètre `q`. Par exemple [`/api/releases?q=excavation%20chaussée&highlight=True`](./api/releases?q=excavation%20chaussée&highlight=True). Important: le moteur de recherche peut retourner des valeurs proches (par exemple une occurrence au pluriel d'un mot recherché au singulier). C'est pour cette raison que s'il est nécessaire pour l'application de surligner les résultats de recherche, il est important de laisser l'API mettre les balises de surlignage.
- `value_gt`: Paramère filtrant les contrats dont le montant est supérieur ou égal à la valeur fournie dans le paramètre. Accepte seulement un nombre entier. Par exemple: [`/api/releases?value_gt=100000`](./api/releases?value_gt=100000) 
- `value_lt`: Paramère filtrant les contrats dont le montant est inférieur ou égal à la valeur fournie dans le paramètre. Accepte seulement un nombre entier. Par exemple: [`/api/releases?value_lt=100000`](./api/releases?value_lt=100000) 
- `date_gt`: Paramère filtrant les contrats dont la date est postérieure ou égale à la date fournie dans le paramètre. Format accepté: `AAAA-MM-JJ`. Par exemple: [`/api/releases?date_gt=2014-01-01`](./api/releases?date_gt=2014-01-01) 
- `date_lt`: Paramère filtrant les contrats dont la date est antérieure ou égale à la date fournie dans le paramètre. Format accepté: `AAAA-MM-JJ`. Par exemple: [`/api/releases?date_lt=2014-01-01`](./api/releases?date_lt=2014-01-01) 
- `buyer`: Paramère filtrant les contrats dont le donneur d'ouvrage est celui fourni dans le paramètre. La valeur correspond à l'identifiant unique du donneur d'ouvrage disponible dans le champs `slug` du point d'accès `/api/helpers/buyer_slugs` ou dans le champ `buyer.identifier.id` dans la structure du contract (`release`). Par exemple: [`/api/releases?buyer=service-du-developpement-economique`](./api/releases?buyer=service-du-developpement-economique). Plusieurs acheteurs peuvent être demandés en séparant les identifiants de ces derniers par un point-virgule `;`.
- `supplier`: Paramère filtrant les contrats dont le fournisseur est celui fourni dans le paramètre. La valeur correspond à l'identifiant unique du fournisseur disponible dans le champs `slug` du point d'accès `/api/helpers/supplier_slugs` ou dans le champ `awards.suppliers.identifier.id` dans la structure du contract (`release`). Par exemple: [`/api/releases?supplier=hydro-quebec`](./api/releases?supplier=hydro-quebec). Plusieurs fournisseurs peuvent être demandés en séparant les identifiants de ces derniers par un point-virgule `;`.
- `procuring_entity`: Paramère filtrant les contrats dont l'autorité d'approbation est celle fourni dans le paramètre. La valeur correspond à celle fournie dans `tender.procuringEntity.identifier.id` dans la structure du contract (`release`). Par exemple: [`/api/releases?procuring_entity=fonctionnaires`](./api/releases?procuring_entity=fonctionnaires). Plusieurs autoritées peuvent être demandées en séparant les identifiants de ces derniers par un point-virgule `;`.
- `activity`: Paramère filtrant les contrats appartenant au domaine d'activité fourni dans le paramètre. La valeur correspond à celle fournie dans le champs `subject` dans la structure du contract (`release`) ou dans le champs `name` du point d'accès `/api/helpers/activity_list`. Par exemple: [`/api/releases?activity=Arrondissements`](./api/releases?activity=Arrondissements). Plusieurs activités peuvent être demandées en séparant les identifiants de ces derniers par un point-virgule `;`.
- `type`: Paramère permettant de sélectionner les contrats ou les subventions. Valeurs acceptés: `contract` pour les contrats, `subvention` pour les subventions. Si le paramètre n'est pas fourni, l'API renvoie par défaut les contrats. Par exemple: [`/api/releases?type=subvention`](./api/releases?type=subvention).
- `aggregate`: Paramère spécifique au point d'accès `/api/releases/by_month_activity`. Ce paramètre permet d'agréger les résultats par activité avec les 4 principales activités. Les valeurs acceptées sont `value` pour agréger par valeur totale des contrats ou `count` pour agréger par nombre de contrat. Par exemple [`/api/releases/by_month_activity?aggregate=value&date_gt=2014-01-01`](./api/releases/by_month_activity?aggregate=value&date_gt=2014-01-01) va calculer les 4 principales activités par montant (top 4) pour les contrats postérieurs au 1<sup>er</sup> janvier 2014. Le top 4 sera affiché normalement et les autres activités seront agrégée dans une activité "Autres".
- `bucket`: Paramère spécifique au point d'accès `/api/releases/by_value`. Ce paramètre permet de définir des segments de valeur dans lesquels regrouper les valeurs des contrat. Le paramètre contient trois valeurs séparées par une virgule. Les deux premières valeurs sont les montants minimum et maximum qui devraient être les mêmes que `value_lt` et `value_gt` si fournis. La dernière valeur représente le nombre de séparateurs de segment. Ainsi en mettant la valeur `19` on obtient 20 segments. La valeur par défaut est `0,100000000,19`. Par exemple: [`/api/releases/by_value?bucket=0,10000000,19`](/api/releases/by_value?bucket=0,10000000,19) va créer 20 segments de 500 000$.

*Tri et pagination*

- `order_by`: Paramètre permettant de trier les résultats selon un champ particulier. Les valeurs varient en fonction du point d'accès.
- `order_dir`: paramètre à utiliser en conjonction de `order_by` pour définir l'order de tri. Les valeurs acceptés sont `desc`pour un tri descendant et `asc` pour un tri ascendant. Par exemple: `/api/releases?order_by=date&order_dir=desc`
- `limit` : Paramètre permettant de limiter le nombre de résultat retourné lors d'un requête. Pour les listes de contrats, la valeur par défaut est 50. La valeur maximale acceptée est 10 000.
- `offset`: Paramètre permettant de définir quel est le rang du premier résultat à retourné. Ce paramètre est à utiliser avec le paramètre `limit` pour obtenir une pagination. Par exemple: `/api/releases?limit=10&offset=50` permet d'obtenir les contrats entre le 50<sup>ème</sup> et le 60<sup>ème</sup> rang.

*Format de données*

Pour les listes de contrats (point d'accès `/api/releases`), il est possible de choisir plusieurs formats.

- `json` (valeur par défaut): permet d'obtenir un résultat sérialisé en JSON avec une structure `meta` fournissant des informations de contexte (voir plus bas)
- `ocds` : permet d'obtenir un fichier suivant la spécification Open Contracting Data Standard.
- `csv` :  permet d'obtenir un fichier au format CSV (*comma separated value* ou champs séparé par des virgules).
- `xlsx` : permet d'obtenir un fichier au format Open Office XML compatible avec Microsoft Office 2007 et versions suivantes
- `pdf` : permet d'obtenir un fichier au format Adobe PDF.


#### Liste des contrats

- URL : /api/releases
- Description : Point d'accès permettant d'accéder à une liste des contrats au format Open Contracting Data Stardard (à moins qu'un autre `format` soit fourni). 
- Champs: En plus de la structure OCDS, l'API retourne une structure `meta` contenant les champs suivants:
	- `count`: Nombre total de contrats correspondant aux filtres demandés
	- `total_value` : Montant total des contrats correspondant aux filtres demandés
	- `max_value` : Montant du contrat le plus élevé correspondant aux filtres demandés
	- `min_value` : Montant du contrat le plus petit correspondant aux filtres demandés
	- `pagination` : retourne les informations de pagination `limit` et `offset` correspondant aux paramètres d'URL fournis ou des valeurs par défaut.
- Filtres acceptés: `q`, `offset`, `limit`, `value_gt`, `value_lt`, `date_gt`, `date_lt`, `buyer`, `activity`, `supplier`, `order_by`, `order_dir`, `type`, `supplier_size`, `procuring_entity`, `highlight`, `format`
- Paramètre de tri acceptés: `value`, `buyer` (alphabétique), `supplier` (alphabétique), `id` (alphabétique), `date`


#### Contrats par fournisseurs

- URL : /api/releases/by_supplier
- Description : Point d'accès groupant les contrats par fournisseurs
- Champs:
	- `supplier`: Nom complet du fournisseur
	- `supplier_slug`: Identifiant du fournisseur
	- `count`: Nombre total de contrats attibués à ce fournisseur et correspondant aux filtres demandés
	- `total_value` : Valeure totale des contrats alloués à ce fournisseur et correspondant aux filtres demandés
- Filtres acceptés: `q`, `offset`, `limit`, `value_gt`, `value_lt`, `date_gt`, `date_lt`, `buyer`, `activity`, `supplier`, `order_by`, `order_dir`, `type`, `procuring_entity`
- Paramètre de tri acceptés: `total_value`, `count`, `buyer_slug` (alphabétique)


#### Contrats par donneurs d'ouvrage

- URL : /api/releases/by_buyer
- Description : Point d'accès groupant les contrats par donneur d'ouvrage
- Champs. Liste d'acheteurs, chaque élément contenant les champs suivants:
	- `buyer`: Nom complet du donneur d'ouvrage
	- `buyer_slug`: Identifiant du donneur d'ouvrage
	- `count`: Nombre total de contrats attibués par ce donneur d'ouvrage et correspondant aux filtres demandés
	- `total_value` : Valeur totale des contrats attribués par ce donneur d'ouvrage et correspondant aux filtres demandés
- Filtres acceptés: `q`, `offset`, `limit`, `value_gt`, `value_lt`, `date_gt`, `date_lt`, `buyer`, `activity`, `supplier`, `order_by`, `order_dir`, `type`, `procuring_entity`
- Paramètre de tri acceptés: `total_value`, `count`, `buyer_slug` (alphabétique)

#### Contrats par entité d'autorisation

- URL : /api/releases/by_procuring_entity
- Description : Point d'accès groupant les contrats par entité d'autorisation
- Champs. Liste des entités, chaque élément contenant les champs suivants:
	- `procuring_entity`: Nom complet de l'entité d'autorisation
	- `buyer_slug`: Identifiant de l'entité d'autorisation
	- `count`: Nombre total de contrats autorisés par cette entité et correspondant aux filtres demandés
	- `total_value` : Valeur totale des contrats autorisés par cette entité et correspondant aux filtres demandés
- Filtres acceptés: `q`, `offset`, `limit`, `value_gt`, `value_lt`, `date_gt`, `date_lt`, `buyer`, `activity`, `supplier`, `order_by`, `order_dir`, `type`, `procuring_entity`
- Paramètre de tri acceptés: `total_value`, `count`, `procuring_entity` (alphabétique)


#### Contrats par segment de valeur

- URL : /api/releases/by_value
- Description : Point d'accès groupant les contrats selon des segments de valeur déterminé via le paramètre `bucket`. Important: Le client se doit de calculer lui-même la valeur maximale et minimale de chaque segment. Les segments vide ne sont pas retournés.
- Champs. Le point d'accès renvoie une liste de segment avec les champs suivants:
	- `segment`: Rang du segment retourné (nombre entier)
	- `count`: Nombre total de contrats inclus dans le segment et correspondant aux filtres demandés
	- `total_value` : Valeur totale des contrats inclus dans le segment et correspondant aux filtres demandés
- Filtres acceptés: `q`, `offset`, `limit`, `value_gt`, `value_lt`, `date_gt`, `date_lt`, `buyer`, `activity`, `supplier`, `order_by`, `order_dir`, `type`, `procuring_entity`, `bucket`
- Paramètre de tri acceptés: `total_value`, `count`, `procuring_entity` (alphabétique)


#### Contrats par mois-année

- URL : /api/releases/by_month
- Description : Point d'accès groupant les contrats pour chaque mois et année de la période couverte par les données
- Champs:
	- `month`: Mois-année au format `AAAA-MM`
	- `count`: Nombre total de contrats inclus dans ce mois-année et correspondant aux filtres demandés
	- `total_value` : Valeur totale des contrats inclus ce mois-année et correspondant aux filtres demandés
- Filtres acceptés: `q`, `offset`, `limit`, `value_gt`, `value_lt`, `date_gt`, `date_lt`, `buyer`, `activity`, `supplier`, `order_by`, `order_dir`, `type`, `procuring_entity`
- Paramètre de tri acceptés: `total_value`, `count`, `month` (alphabétique)

#### Contrats par mois et activité

- URL : /api/releases/by_month_activity
- Description : Point d'accès groupant les contrats par mois puis par domaine d'activité. Ce point d'appel est utilisé pour créer le principal graphique de l'application web de visualisation de contrat. Ce point d'appel support un paramètre spécifique, `aggregate` permettant d'agréger dans la catégories "Autres" les activités après les 4 principales.
- Champs: Le point d'accès fournit une liste de mois-années ayant chacune la structure suivante:
	- `month`: Moins-année au format `AAAA-MM`
	- Liste d'activité, chaque élément ayant la structure:
		- `activity` : Nom de l'activité
		- `count`: Nombre total de contrats appartenant à l'activité pour le mois-année parent et correspondant aux filtres demandés
		- `total_value` : Valeur totale des contrats appartenant à l'activité pour le mois-année parent et correspondant aux filtres demandés
- Filtres acceptés: `q`, `offset`, `limit`, `value_gt`, `value_lt`, `date_gt`, `date_lt`, `buyer`, `activity`, `supplier`, `order_by`, `order_dir`, `type`, `procuring_entity`, `aggregate`.
- Paramètre de tri acceptés: `month`
