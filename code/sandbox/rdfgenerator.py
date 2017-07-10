
from pymarc import MARCReader
import hashlib
import re
import difflib
import pickle
import fnmatch
import codecs
import unidecode
import sqlite3
from rdflib import URIRef, Graph, Literal, Namespace
from rdflib.namespace import RDF, FOAF, DC, SKOS, RDFS, OWL
import urllib.parse
import re
from urllib.request import urlopen, urlparse
from bs4 import BeautifulSoup
import os
import ssl

context = ssl._create_unverified_context()
# NOTE
# load the pickle objects that will be used for university and subject uri generation
with open("files/universities.pickle", "rb") as handle:
    universities = pickle.load(handle)      # key: name, value: uri

with open("files/subjects_full.pickle", "rb") as handle:
    subjects = pickle.load(handle)      # key: subject name, value: uri

# with open("files/authoritiesnames.pickle", "rb") as handle:
#     names = pickle.load(handle)         # key: name, value: uri


# set up the RDFLib output
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
g.bind("owl", OWL)
# used to keep non-persistent memory of the universities we have processed before
# so that we don't need to go to dbpedia every time
university_uri_cache = {}

# will be filled after the validation function is done
# warnings = []
# errors = []
logs = []

class Thesis():
    def __init__(self, record):
        self.record = record
        
        self.control = self.getControlNumber()
        self.linking = self.getLinkingControlNumber()
        self.author = self.getAuthorName()
        self.title = self.getTitle()
        self.university = self.getUniversity()
        self.universityUri = self.getUniversityUri()
        self.authorUri = self.getAuthorUri()
        self.date = self.getDate()
        self.language = self.getLanguage()
        self.subjects = self.getSubjects()
        self.subjectUris = self.getSubjectUris()
        self.degree = self.getDegree()
        self.degreeLabel, self.degreeUri = self.getDegreeUri()
        self.advisors = self.getAdvisors()
        self.advisorUris = self.getAdvisorUris()
        self.contentUrl = self.getContentUrl()
        self.manifestations = self.getManifestations() 
        self.uri = self.getURI()        

    def getControlNumber(self):
        value_001 = getField(self.record, "001")
        
        if not value_001:
            return None
        
        return(str(value_001).split()[1])
            
    def getLinkingControlNumber(self):
        value_004 = getField(self.record, "004")
        
        if not value_004:
            return None
        
        return(str(value_004).split()[1])

    def getAuthorName(self):
        value_100a = getField(self.record, "100", "a")

        if not value_100a: 
            return None

        return(value_100a[0].strip(" .,"))

    def getAuthorUri(self):
        if not self.author:
            return None
        # see if the uri is given in the records
        value_100zero = getField(self.record, "100", "0")
        if value_100zero:
            return(value_100zero[0])
        
        # # check the authoritiesnames file to see if it exists
        # modifiedName = "".join([x for x in unidecode.unidecode(self.author.lower()).replace(" ", "") if x.isalpha()])

        # if modifiedName in names.keys():
        #     return("<http://id.loc.gov/authorities/names/" + names[modifiedName] + ">")

        if not self.universityUri:
            return None

        return("http://canlink.library.ualberta.ca/Person/"+str(hashlib.md5(self.author.encode("utf-8")+self.universityUri.encode("utf-8")).hexdigest()))

    def getTitle(self):
        if not self.record.title():
            return None
        return(self.record.title().strip("/. "))

    def getUniversity(self): 

        value_502c = getField(self.record, "502", "c")
        value_710a = getField(self.record, "710", "a")
        value_502a = getField(self.record, "502", "a")
        value_264b = getField(self.record, "264", "b")
        value_260b = getField(self.record, "260", "b")
        
        university = None
        
        if value_502c: 
            university = value_502c[0]
        elif value_710a: 
            university = value_710a[0]
        elif value_502a:
            university = value_502a[0].split("thesis", 1)[-1].split("Thesis", 1)[-1].split("--", 1)[-1].split("-", 1)[-1]
        elif value_264b: 
            university = value_264b[0]
        elif value_260b: 
            university = value_260b[0]


        if not university:
            return None

        # remove the extra characters
        university = university.replace(".", "").replace(",", "").strip()
        university = ''.join([i for i in university if not i.isdigit()])
        # university = ''.join([i for i in university if i.isalpha() or i == " "])    # remove the dates or anything else it might have

        # # removes the brackets
        # university = re.sub(r'\(.*\)', '', university)

        return university
        
    def getUniversityUri(self):
        if not self.university:
            return None

        # get rid of slashes if they exist
        universityName = self.university.split("/")[0]
        # remove the special characters like accents
        universityName = unidecode.unidecode(universityName)
        
        if universityName in university_uri_cache.keys():
            # print("Found in cache: ", universityName, self.control)
            return(university_uri_cache[universityName])    
        else:
            # get the names of the universities
            universityNames = universities.keys()

            # print("Processing: ", universityName, self.control)
            # find the closest university name in the list of names
            match = difflib.get_close_matches(universityName, universityNames, n=1)

            if match:
                uri = universities[match[0]]
                # save to cache for future reference
                university_uri_cache[universityName] = uri
                return uri    # return the uri associated with that name
            else:
                return None

    def getDate(self):
        value_260c = getField(self.record, "260", "c")
        value_264c = getField(self.record, "264", "c")
        
        date = None

        if value_260c:
            date = value_260c[0]
        elif value_264c:
            date = value_264c[0]

        if not date: 
            return None
         # remove all non numeric characters
        return(''.join(c for c in date if str(c).isdigit()))

    def getSubjects(self):
        value_630a = getField(self.record, "630", "a")
        value_650a = getField(self.record, "650", "a")
        value_653a = getField(self.record, "653", "a")

        subjects = []

        for subject in value_630a:
            subjects.append(subject)

        for subject in value_650a:
            subjects.append(subject)
        
        for subject in value_653a:
            subjects.append(subject)
        
        if not subjects:    
            return None

        return([subject.strip(".") for subject in subjects])

    def getSubjectUris(self):
        if not self.subjects:
            return None

        # URIs = []
        URIs = {}
        for subject in self.subjects:
            if subject.lower() in subjects.keys():
                # exact subject found
                URIs[subject] = subjects[subject.lower()]
                # URIs.append(subjects[subject.lower()])
            else:
                URIs[subject] = None
            # elif len(subject) > 3 and len(subject) < 30:
            #   # get the closest subject but making sure that atleast the first character matches
            #   closest = difflib.get_close_matches(subject, [key for key in subjects.keys() if key[0:4] == subject[0:4]], n=1, cutoff=0.90)
            #   if not closest:
            #       continue
            #   URIs.append("http://id.loc.gov/authorities/subjects/" + closest[0])
            #   print("NEW SUBJECT GENERATED: " + closest[0] + " for original:" + subject)

        return URIs
    # TODO Make sure to update this function in processing.py
    def getLanguage(self):
        value_008 = getField(self.record, "008")
        value_040b = getField(self.record, "040", "b")
        value_041a = getField(self.record, "041", "a")

        language = "eng"

        if value_008 and len(str(value_008).split()[1]) >= 38: 
            language = str(value_008).split()[1][35:38]
        elif value_041a: 
            language = value_041a[0]
        elif value_040b: 
            language = value_040b[0]
        
        # print(language)
        return("http://id.loc.gov/vocabulary/languages/"+language)

    def getDegree(self):
        value_502a = getField(self.record, "502", "a")
        value_502b= getField(self.record, "502", "b")

        degree = None

        if value_502b: 
            degree = value_502b[0]
        elif value_502a: 
            degree = value_502a[0].split("--", 1)[0].split(",", 1)[0]

        if not degree:  
            return None

        degree = degree.replace("Thesis", "").replace("thesis", "").replace("(", "").replace(")", "").strip()

        if degree:
            return degree
        return None

    def getDegreeUri(self):
        # convert the degree name to lowercase and remove the extra characters except for the space
        if not self.degree:
            return([None, None])
        
        degree = self.degree 
        # remove everything after "in" since that indicates a specialization
        if "in" in degree.split():
            degree = " ".join(degree.split()[:degree.split().index("in")])

        if "," in degree:
            degree = " ".join(degree[:degree.index(",")].split())

        degree = ''.join([i for i in degree if i.isalpha()]).lower()
        uri = None
        label = None        # label = MSc for degree = msc
        # do the basic ones
        degree_codes = {
                        "maîtrise":["Master", "http://canlink.library.ualberta.ca/thesisDegree/master"],
                        "mphysed":["MPhysEd", "http://canlink.library.ualberta.ca/thesisDegree/mphysed"],
                        "menvsc":["MEnv", "http://canlink.library.ualberta.ca/thesisDegree/menv"],
                        "mdent":["MDent", "http://canlink.library.ualberta.ca/thesisDegree/mdent"],
                        "maît":["Master", "http://canlink.library.ualberta.ca/thesisDegree/master"],
                        "maed":["MAEd", "http://canlink.library.ualberta.ca/thesisDegree/maed"],
                        "meng":["MEng", "http://canlink.library.ualberta.ca/thesisDegree/meng"],
                        "mdes":["MDes", "http://canlink.library.ualberta.ca/thesisDegree/mdes"],
                        "dent":["MDent", "http://canlink.library.ualberta.ca/thesisDegree/mdent"],
                        "masc":["MASc", "http://canlink.library.ualberta.ca/thesisDegree/masc"],
                        "msc":["MSc", "http://canlink.library.ualberta.ca/thesisDegree/msc"],
                        "llm":["LLM", "http://id.loc.gov/authorities/subjects/sh2012003813"],
                        "mws":["MWS", "http://canlink.library.ualberta.ca/thesisDegree/mws"],
                        "mhk":["MHK", "http://canlink.library.ualberta.ca/thesisDegree/mhk"],
                        "mpp":["MPP", "http://canlink.library.ualberta.ca/thesisDegree/mpp"],
                        "mba":["MBA", "http://id.loc.gov/authorities/subjects/sh85081991"],
                        "mfa":["MFA", "http://canlink.library.ualberta.ca/thesisDegree/mfa"],
                        "sjd":["SJD", "http://canlink.library.ualberta.ca/thesisDegree/sjd"],
                        "edd":["EDD", "http://canlink.library.ualberta.ca/thesisDegree/edd"],
                        "med":["MEd", "http://id.loc.gov/authorities/subjects/sh2010014261"],
                        "phd":["PhD", "http://id.loc.gov/authorities/subjects/sh85038715"],
                        "dba":["DBA", "http://canlink.library.ualberta.ca/thesisDegree/dba"],
                        "dsc":["DSc", "http://id.loc.gov/authorities/subjects/sh85038715"],
                        "des":["Des", "http://canlink.library.ualberta.ca/thesisDegree/des"],
                        "msw":["MSW", "http://canlink.library.ualberta.ca/thesisDegree/msw"],
                        "ma":["MA", "http://id.loc.gov/authorities/subjects/sh85081990"],
                        "mn":["MN", "http://canlink.library.ualberta.ca/thesisDegree/mn"]
        }

        for code in degree_codes:
            if code in degree:
                return(degree_codes[code][0], degree_codes[code][1])

        # check for longer sentences if the keywords aren't available
        degrees = {"masterofscience":["MSc", "http://canlink.library.ualberta.ca/thesisDegree/msc"],
                 "masterofarts":["MA", "http://id.loc.gov/authorities/subjects/sh85081990"],
                 "masteroffinearts":["MFA", "http://canlink.library.ualberta.ca/thesisDegree/mfa"],
                 "masterofappliedscience":["MASc", "http://canlink.library.ualberta.ca/thesisDegree/masc"],
                 "masteroflaws":["LLM", "http://id.loc.gov/authorities/subjects/sh2012003813"],
                 "masterofenvironmentalstudies":["MEnv", "http://canlink.library.ualberta.ca/thesisDegree/menv"],
                 "masterofeducation":["MEd", "http://id.loc.gov/authorities/subjects/sh2010014261"],
                 "masterofnursing":["MN", "http://canlink.library.ualberta.ca/thesisDegree/mn"],
                 "masterofarchitecture":["MArch", "http://canlink.library.ualberta.ca/thesisDegree/march"],
                 "masterofmathematics":["MMath", "http://canlink.library.ualberta.ca/thesisDegree/mmath"],
                 "masterofhealthstudies":["MHStud", "http://canlink.library.ualberta.ca/thesisDegree/mhstud"],
                 "masterofcounselling":["MCoun", "http://canlink.library.ualberta.ca/thesisDegree/mcoun"],
                 "masterofengineering":["MEng", "http://canlink.library.ualberta.ca/thesisDegree/meng"],
                 "masterofadvancedstudies":["MAS", "http://canlink.library.ualberta.ca/thesisDegree/mas"],
                 "masterofphysicaleducation":["MPhysEd", "http://canlink.library.ualberta.ca/thesisDegree/mphysed"],
                 "masterofbusinessadministration":["MBA", "http://id.loc.gov/authorities/subjects/sh85081991"],
                 "masterofworshipstudies":["MWS", "http://canlink.library.ualberta.ca/thesisDegree/mws"],
                 "doctorofphilosophy":["PhD", "http://id.loc.gov/authorities/subjects/sh85038715"],
                 "doctoralthesis":["PhD", "http://id.loc.gov/authorities/subjects/sh85038715"],
                 "doctorofbusinessadministration":["DBA", "http://canlink.library.ualberta.ca/thesisDegree/dba"],
                 "doctorofscience":["PhD", "http://id.loc.gov/authorities/subjects/sh85038715"],
                 "doctor":["PhD", "http://id.loc.gov/authorities/subjects/sh85038715"]}
        
        if "master" in degree or "doctor" in degree:
            match = difflib.get_close_matches(degree, degrees.keys(), n=1, cutoff=0.90)
            if match:
                return(degrees[match[0]][0], degrees[match[0]][1])
            if "master" in degree:
                return(["Master", "http://canlink.library.ualberta.ca/thesisDegree/master"])
            return(["PhD", "http://canlink.library.ualberta.ca/thesisDegree/phd"])


        # if uri: return(uri)

        return([None, None])

    def getAdvisors(self):
        value_500a = getField(self.record, "500", "a")
        value_720a= getField(self.record, "720", "a")

        if value_720a: 
            return(value_720a)

        if value_500a:
            for item in value_500a:
                if "advisor" in item.lower() or "directeur" in item.lower() and ":" in item:
                    return([advisor.strip(" .,") for advisor in item.split(":", 1)[1].split(",")])
        
        return None

    def getAdvisorUris(self):
        uris = []
        
        if not self.advisors:
            return None
        
        for name in self.advisors:
            uri = ""
            if self.universityUri:
                uri = "http://canlink.library.ualberta.ca/Person/"+str(hashlib.md5(name.encode("utf-8")+self.universityUri.encode("utf-8")).hexdigest())
            else:
                uri = "http://canlink.library.ualberta.ca/Person/"+str(hashlib.md5(name.encode("utf-8")).hexdigest())

            uris.append(uri)

        return uris

    def getContentUrl(self):
        value_856u = getField(self.record, "856", "u")

        if not value_856u:
            return None
        
        urls = [urllib.parse.quote(url, safe="%/:=&?~#+!$,;'@()*[]") for url in value_856u]
        output = []

        for url in urls:
            output.append(url)
            if ".pdf" not in url:
                # the url is not linking to a pdf - a handle.net url or something else
                # need to extract the link to the pdf from here
                try:
                    output.append(self.getPDFFromPage(url))
                except:
                    pass

        return(output)
        # return(["<"+url+">" for url in value_856u])
    def getPDFFromPage(self, url):
        html_object = urlopen(url, context=context)
        html_doc = html_object.read()
        soup = BeautifulSoup(html_doc, "html.parser")

        pdf_url = ""
        # find all the .pdf links in the page
        for link in soup.find_all("a"):
            l = link.get("href")
            if ".pdf" in str(l):
                pdf_url = str(l)

        # convert relative links to absolute links if necessary
        if pdf_url and "http" not in pdf_url and "www" not in pdf_url:
            redirect_url = html_object.geturl()
            if pdf_url[0] == "/":
                # append to the base of the redirect url
                base_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(redirect_url))
                return(base_url + pdf_url)
            else:
                # append to the end of the redirect url
                return(redirect_url + pdf_url)
        return(pdf_url)

    def getManifestations(self):
        # returns a list of the content urls hashed and with a ualberta uri 
        if not self.contentUrl:
            return None

        manifestations = []
        for url in self.contentUrl:
            manifestations.append("http://canlink.library.ualberta.ca/manifestation/"+hashlib.md5(url.encode("utf-8")).hexdigest())

        return manifestations

    def getURI(self):
        if self.author and self.title:
            identifier = hashlib.md5((str(self.author).encode("utf-8") + str(self.title).encode("utf-8"))).hexdigest()
            return("http://canlink.library.ualberta.ca/thesis/"+str(identifier))
        return None

    def generateRDF(self):
        # thesis title - don't need to check if it exists because validateRecords did that already
        g.add((URIRef(self.uri), DC.title, Literal(self.title)))
        # same as (links that are not pdf files but still contain information about this thesis)
        if self.contentUrl:
            for url in self.contentUrl:
                if ".pdf" not in url:
                    g.add((URIRef(self.uri), OWL.sameAs, URIRef(url)))

        # date
        if self.date:
            g.add((URIRef(self.uri), DC.issued, Literal(self.date, datatype="gYear")))
        # language
        if self.language:
            g.add((URIRef(self.uri), DC.language, URIRef(self.language)))
        # degree
        if self.degreeUri:
            g.add((URIRef(self.uri), BIBO.degree, URIRef(self.degreeUri)))
            g.add((URIRef(self.degreeUri), RDF.type, BIBO.thesisDegree))
            g.add((URIRef(self.degreeUri), RDFS.label, Literal(self.degreeLabel)))
        # author uri
        if self.authorUri:
            g.add((URIRef(self.uri), DC.creator, URIRef(self.authorUri)))
            g.add((URIRef(self.uri), REL.author, URIRef(self.authorUri)))
            # author type
            g.add((URIRef(self.authorUri), RDF.type, FOAF.Person))
            # author name
            if "," in self.author:
                g.add((URIRef(self.authorUri), FOAF.lastName, Literal(self.author.split(",")[0].strip())))   
                g.add((URIRef(self.authorUri), FOAF.firstName, Literal(self.author.split(",")[1].strip())))    
            else:
                g.add((URIRef(self.authorUri), FOAF.name, Literal(self.author.strip())))
        # publisher
        if self.universityUri:
            g.add((URIRef(self.uri), DC.publisher, URIRef(self.universityUri))) 
        # thesis types
        g.add((URIRef(self.uri), RDF.type, FRBR.Work)) 
        g.add((URIRef(self.uri), RDF.type, FRBR.Expression)) 
        g.add((URIRef(self.uri), RDF.type, SCHEMA.creativeWork))
        g.add((URIRef(self.uri), RDF.type, BIBO.thesis))
        # advisors
        if self.advisorUris:
            for index, uri in enumerate(self.advisorUris):
                g.add((URIRef(self.uri), REL.ths, URIRef(uri)))
                g.add((URIRef(uri), FOAF.name, Literal(self.advisors[index])))
                g.add((URIRef(uri), RDF.type, FOAF.Person))
        # subjects
        if self.subjectUris:
            for subject in self.subjectUris.keys():
                # check if we have the uri for it - we made a dictionary and set the value to None if we couldn't find a uri
                if self.subjectUris[subject]:
                    g.add((URIRef(self.uri), DC.subject, URIRef(self.subjectUris[subject])))
                else:
                    # the subject uri couldn't be found for this
                    # create a skos:concept node, add the subject heading string as rdfs:label of that new node and then link the new node as a subject heading of the current thesis - use md5 of the lower case value of the subject heading so we don't generate doubles (Rob - June 23)
                    newSubjectUri = "http://canlink.library.ualberta.ca/subject/" + hashlib.md5(subject.lower().encode("utf-8")).hexdigest()

                    g.add((URIRef(newSubjectUri), RDF.type, SKOS.Concept))
                    g.add((URIRef(newSubjectUri), RDFS.label, Literal(subject.lower())))
                    g.add((URIRef(self.uri), DC.subject, URIRef(newSubjectUri)))
        # manifestation
        if self.manifestations:
            for index, manifestation in enumerate(self.manifestations):
                if ".pdf" not in self.contentUrl[index]: continue       # we already took care of non pdf links by using OWL:sameAs
                g.add((URIRef(manifestation), SCHEMA.encodesCreativeWork, URIRef(self.uri)))
                g.add((URIRef(manifestation), SCHEMA.contentUrl, URIRef(self.contentUrl[index])))
                g.add((URIRef(manifestation), RDF.type, FRBR.Manifestation))
                g.add((URIRef(manifestation), RDF.type, SCHEMA.MediaObject))


    def __str__(self):
        return """Control:          %s<br>Title:                   %s<br>URI:                   %s<br>Author:          %s<br>Author Uri:          %s<br>University:          %s<br>University Uri: %s<br>Date:                   %s<br>Language:          %s<br>Subjects:          %s<br>Subjects Uris:          %s<br>Degree:          %s<br>Degree Uri:          %s<br>Advisors:          %s<br>Advisor Uris:          %s<br>Content Url:          %s<br>Manifest.:          %s
        """ % (self.control, self.title, self.uri, self.author, self.authorUri, self.university, self.universityUri, self.date, self.language, self.subjects, self.subjectUris, self.degree, self.degreeUri, self.advisors, self.advisorUris, self.contentUrl, self.manifestations)

def getField(record, tag_value, subfield_value=None):
    # tag ex: "710"
    # subfield ex: "b"
    # need this function since just doing record["710"]["b"] doesn't work if 
    # there are multiple lines of the same tag
    results = []
    for field in record.get_fields(tag_value):
        if not subfield_value:
            return(field)
        for subfield in field:
            if subfield[0] == subfield_value:
                results.append(subfield[1])

    # remove the duplicate results because sometimes they exist
    results = list(set(results))
    return(results)


def mergeRecords(thesis1, thesis2):
    # takes in two theses (objects of Thesis class) and merges the information into one
    # if thesis2 contains some authors and thesis1 contains some, then they won't be merged even though it logically makes sense to merge them --> assuming that a single field isn't split between two records
    
    # the list of attributes that need to be merged into one object
    attributes = ["title", "author", "university", "universityUri", "authorUri", "date", "language", "subjects", "subjectUris", "degree", "degreeUri", "advisors", "advisorUris", "contentUrl", "uri", "manifestations"]

    for attribute in attributes:
        # if thesis1 doesn't have a value for this attribute, then copy it from thesis2
        thesis1_attribute_value = getattr(thesis1, attribute)
        thesis2_attribute_value = getattr(thesis2, attribute)

        if not thesis1_attribute_value and thesis2_attribute_value:
            # copy that value to the same attribute of thesis1
            setattr(thesis1, attribute, thesis2_attribute_value)

    # generate authoruri and uri again since they depend on other values that may not have existed in the individual records before merging
    thesis1.authorUri = thesis1.getAuthorUri()
    thesis1.uri = thesis1.getURI()


def validateRecord(record, errors, warnings):
    record_errors = []
    record_warnings = []

    # valudates a record after the file has been processed - does NOT check for errors in the file
    status = True

    if not record.title: 
        record_errors.append("Title not found - Please enter the titles and submit form again")
        status = False
    if not record.author: 
        record_errors.append("Author Name not found - Please enter the author name and submit the form again")
        status = False
    if not record.universityUri: record_warnings.append("University URI couldn't be generated - Make sure the University Name is valid")
    if not record.date: record_warnings.append("Publication Date not found")
    if not record.language: record_warnings.append("Language not found - Setting language to English")
    if not record.subjects: record_warnings.append("Subjects not found")
    if record.subjects and record.subjectUris and len(record.subjectUris) < len(record.subjects): record_warnings.append("Some Subject URIs couldn't be generated")
    if not record.degree: record_warnings.append("Degree Type not found")
    if not record.degreeUri: record_warnings.append("Degree URI could not be generated - Please make sure the degree is valid")
    if not record.advisors: record_warnings.append("Advisors not found")
    if not record.contentUrl: record_warnings.append("Content URLs not found")

    # check if the control number was randomly generated - it didn't exist in the original records
    # if record.control[0] == "R":
    #     recordNumber = record.control[1:]       # everything after "R" is the occurence number
    #     warnings.append("Record #" + recordNumber + " didn't have a control number - #" + record.control + " was assigned to it")

    for error in record_errors:
        errors.append("Record #" + record.control + " - " + error)

    for warning in record_warnings:
        warnings.append("Record #" + record.control + " - " + warning)

    
    return status


def main():
    reader = MARCReader(open("files/U_Montreal_100_BibliographicRecords_from_ILS.mrc", "rb"), force_utf8=True)

    records = {}
    errors = []
    warnings = []
    theses = []

    # when the control number isn't given, we use this to generate one
    count = 0 
    # process and merge the records
    for record in reader: 
        # read record
        thesis = Thesis(record)
        count += 1
        # get control number and linking number
        controlNumber = thesis.control
        linkingNumber = thesis.linking
        # if no linking number, check if the control number shows up as a linking number of any other record -> merge them 
        # if linking number, check if the linking number shows up as a control number of any other record -> merge them
        if not controlNumber: 
            # TODO print("Control")
            thesis.control = "R"+str(count)        # permanently replacing the control number with a generated one for validation purposes
            records[thesis.control] = thesis

        elif linkingNumber and linkingNumber in records.keys():
            # linking number for the current record exists and we already processed the other record that this links to -> merge them into one
            rec = records[linkingNumber]        # rec = the record we are merging the current record into
            mergeRecords(rec, thesis)        

        elif not linkingNumber and controlNumber in records.keys():
            # linking number for the current record doesn't exist and we already processed the other record that this links to -> merge them into one
            rec = records[controlNumber]        # rec = the record we are merging the current record into
            mergeRecords(rec, thesis)

        elif linkingNumber:
            #pretend the linking number is a control number when adding to dictionary because the top two statements check for the control number and for the supplementary records, the control number is useless but we need to merge using identical linking numbers so store the linking number for searching
            records[linkingNumber] = thesis

        elif not linkingNumber:
            records[controlNumber] = thesis
        
    for thesis in records.values():
        # print(thesis)
        theses.append(str(thesis))
        if validateRecord(thesis, errors, warnings):
            # if there were no errors (could still have warnings) then generate RDF
            thesis.generateRDF()
        # print("-"*50)


    print(g.serialize(format="n3").decode("utf-8"))
    g.serialize("U_Montreal_100_BibliographicRecords_from_ILS.n3", format="n3")

    # sometimes the lists persist through different sessions so remove the duplicates for now
    # has to do something with the fact that process is called and the lists are outside 
    # return(sorted(list(set(errors))), sorted(list(set(warnings))))
    # NOTE
    # return(errors, warnings, theses)
# NOTE
main()