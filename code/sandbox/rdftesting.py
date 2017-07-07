# a sample file for getting it to output proper rdf

from rdflib import URIRef, Graph, Literal, Namespace
from rdflib.namespace import RDF, FOAF, DC, SKOS, RDFS
import hashlib
g = Graph()

REL = Namespace("http://purl.org/vocab/relationship/")
BIBO = Namespace("http://purl.org/ontology/bibo/")
SCHEMA = Namespace("http://schema.org/")
FRBR = Namespace("http://purl.org/vocab/frbr/core#")

g.bind("foaf", FOAF)
g.bind("dc", DC)
g.bind("rdf", RDF)
g.bind("rel", REL)
g.bind("frbr", FRBR)
g.bind("bibo", BIBO)
g.bind("schema", SCHEMA)
g.bind("skos", SKOS)
g.bind("rdfs", RDFS)

# gather the data
_title= "Ethnomusicologie et esthétique de la réflexion épistémologique à la recherche de terrain : une étude comparative de la vocalité de tradition orale au sud de l'Italie"
_uri = "http://canlink.library.ualberta.ca/thesis/e7bc15c53a705f580b2091631a8dd7af"
_author_name = "Gervasi, Flavia"
_author_uri = "http://id.loc.gov/authorities/names/n2017002478"
_univesity_uri = "http://dbpedia.org/resource/Université_de_Montréal"
_date = "2011"
_language = "http://id.loc.gov/vocabulary/languages/fre"
_subject_uris = {'Revival': 'http://id.loc.gov/authorities/subjects/sh99002501', 'Rural universe': None, 'Communications and the Arts - Music / Communication et les arts - Musique (UMI : 0413)': None, 'Esthétique': None, 'Notte della Taranta': None, 'Southern Italy': 'http://id.loc.gov/authorities/subjects/sh85069035', 'Italie du sud': None, 'Paysannerie': None, 'Pratiques vocales': None, 'Salento': None, 'Aesthetics': 'http://id.loc.gov/authorities/subjects/sh85001441', 'Vocal practices': None, 'Oral tradition': 'http://id.loc.gov/authorities/subjects/sh85095251', 'Tradition orale': None, 'World music': 'http://id.loc.gov/authorities/subjects/sh93002569', 'Revivalisme': None}

_degree_uri = "http://canlink.library.ualberta.ca/thesisDegree/phd"
_advisors = ['Jean-Jacques Nattiez']
_advisor_uris = ['http://canlink.library.ualberta.ca/Person/39277b8eac6ee2e80cce5bc186031d73']
_content_urls = ['http://hdl.handle.net/1866/8535']
_manifestations = ['http://canlink.library.ualberta.ca/manifestation/af66271fd92a60199b4c71c55c423ea5']

# PROCESSING 

# title
g.add((URIRef(_uri), DC.title, Literal(_title)))       # NOTE that there are two paranthesis 
# date
g.add((URIRef(_uri), DC.issued, Literal(_date)))
# language
g.add((URIRef(_uri), DC.language, URIRef(_language)))
# degree
g.add((URIRef(_uri), BIBO.degree, URIRef(_degree_uri)))
g.add((URIRef(_degree_uri), RDF.type, BIBO.thesisDegree))
# author uri
g.add((URIRef(_uri), DC.creator, URIRef(_author_uri)))
g.add((URIRef(_uri), REL.author, URIRef(_author_uri)))
# author name
g.add((URIRef(_author_uri), FOAF.name, Literal(_author_name)))
# author type
g.add((URIRef(_author_uri), RDF.type, FOAF.Person))
# publisher
g.add((URIRef(_uri), DC.publisher, URIRef(_univesity_uri))) 
# thesis types
g.add((URIRef(_uri), RDF.type, FRBR.Work)) 
g.add((URIRef(_uri), RDF.type, FRBR.Expression)) 
g.add((URIRef(_uri), RDF.type, SCHEMA.creativeWork))
g.add((URIRef(_uri), RDF.type, BIBO.thesis))
# advisors
for index, uri in enumerate(_advisor_uris):
    g.add((URIRef(_uri), REL.ths, URIRef(uri)))
    g.add((URIRef(uri), FOAF.name, Literal(_advisors[index])))
    g.add((URIRef(uri), RDF.type, FOAF.Person))
# subjects
for subject in _subject_uris.keys():
    if _subject_uris[subject]:
        g.add((URIRef(_uri), DC.subject, URIRef(_subject_uris[subject])))
    else:
        # the subject uri couldn't be found for this
        # create a skos:concept node, add the subject heading string as rdfs:label of that new node and then link the new node as a subject heading of the current thesis - use md5 of the lower case value of the subject heading so we don't generate doubles (Rob - June 23)
        newSubjectUri = "http://canlink.library.ualberta.ca/subject/" + hashlib.md5(subject.lower().encode("utf-8")).hexdigest()

        g.add((URIRef(newSubjectUri), RDF.type, SKOS.Concept))
        g.add((URIRef(newSubjectUri), RDFS.label, Literal(subject)))
        g.add((URIRef(_uri), DC.subject, URIRef(newSubjectUri)))
# manifestation
for index, manifestation in enumerate(_manifestations):
    g.add((URIRef(manifestation), SCHEMA.encodesCreativeWork, URIRef(_uri)))
    g.add((URIRef(manifestation), SCHEMA.contentUrl, URIRef(_content_urls[index])))
    g.add((URIRef(manifestation), RDF.type, FRBR.Manifestation))
    g.add((URIRef(manifestation), RDF.type, SCHEMA.MediaObject))


print(g.serialize(format="n3").decode("utf-8"))


# # still maintains the proper encoding when printing - just looks weird in the file 
# print(g.value(subject=uri, predicate=DC.title))

