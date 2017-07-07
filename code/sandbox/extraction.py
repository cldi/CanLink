
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
from rdflib.namespace import RDF, FOAF, DC, SKOS, RDFS
import urllib.parse

# load the pickle objects that will be used for university and subject uri generation
with open("files/universities.pickle", "rb") as handle:
    universities = pickle.load(handle)      # key: name, value: uri

with open("files/subjects.pickle", "rb") as handle:
    subjects = pickle.load(handle)      # key: subject name, value: uri

# with open("files/authoritiesnames.pickle", "rb") as handle:
#     names = pickle.load(handle)         # key: name, value: uri

# TODO will need to convert this to a proper mysql database OR
# maybe just keep it on the server but add it to .gitignore if doing 
# production deployment through github
conn = sqlite3.connect("files/advisors.db")
c = conn.cursor()

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

# used to keep non-persistent memory of the universities we have processed before
# so that we don't need to go to dbpedia every time
university_uri_cache = {}

# will be filled after the validation function is done
warnings = {}
errors = {}
logs = {}

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
        self.degreeUri = self.getDegreeUri()
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
        return(self.record.title().strip("/"))

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
            print("Found in cache: ", universityName, self.control)
            return(university_uri_cache[universityName])    
        else:
            # get the names of the universities
            universityNames = universities.keys()

            print("Processing: ", universityName, self.control)
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
            # 	# get the closest subject but making sure that atleast the first character matches
            # 	closest = difflib.get_close_matches(subject, [key for key in subjects.keys() if key[0:4] == subject[0:4]], n=1, cutoff=0.90)
            # 	if not closest:
            # 		continue
            # 	URIs.append("http://id.loc.gov/authorities/subjects/" + closest[0])
            # 	print("NEW SUBJECT GENERATED: " + closest[0] + " for original:" + subject)

        return URIs
    # TODO Make sure to update this function in processing.py
    def getLanguage(self):
        value_008 = getField(self.record, "008")
        value_040b = getField(self.record, "040", "b")
        value_041a = getField(self.record, "041", "a")

        language = "eng"

        if value_008: 
            language = str(value_008).split()[1][35:38]
        elif value_041a: 
            language = value_041a[0]
        elif value_040b: 
            language = value_040b[0]
        
        
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
            return None
        
        degree = self.degree 
        # remove everything after "in" since that indicates a specialization
        if "in" in degree.split():
            degree = " ".join(degree.split()[:degree.split().index("in")])

        if "," in degree:
            degree = " ".join(degree[:degree.index(",")].split())

        degree = ''.join([i for i in degree if i.isalpha()]).lower()
        uri = None
        # do the basic ones
        if "ma" in degree: uri = "http://id.loc.gov/authorities/subjects/sh85081990"
        if "msc" in degree: uri = "http://canlink.library.ualberta.ca/thesisDegree/msc"
        if "mn" in degree: uri = "http://canlink.library.ualberta.ca/thesisDegree/mn"
        if "llm" in degree: uri = "http://id.loc.gov/authorities/subjects/sh2012003813"
        if "mws" in degree: uri = "http://canlink.library.ualberta.ca/thesisDegree/mws"
        if "mhk" in degree: uri = "http://canlink.library.ualberta.ca/thesisDegree/mhk"
        if "mpp" in degree: uri = "http://canlink.library.ualberta.ca/thesisDegree/mpp"
        if "maed" in degree: uri = "http://canlink.library.ualberta.ca/thesisDegree/maed"
        if "mba" in degree: uri = "http://id.loc.gov/authorities/subjects/sh85081991"
        if "mfa" in degree: uri = "http://canlink.library.ualberta.ca/thesisDegree/mfa"
        if "sjd" in degree: uri = "http://canlink.library.ualberta.ca/thesisDegree/sjd"
        if "edd" in degree: uri = "http://canlink.library.ualberta.ca/thesisDegree/edd"
        if "med" in degree: uri = "http://id.loc.gov/authorities/subjects/sh2010014261"
        if "mas" in degree: uri = "http://canlink.library.ualberta.ca/thesisDegree/mas"
        if "masc" in degree: uri = "http://canlink.library.ualberta.ca/thesisDegree/masc"
        if "meng" in degree: uri = "http://canlink.library.ualberta.ca/thesisDegree/meng"
        if "dent" in degree or "mdent" in degree: uri = "http://canlink.library.ualberta.ca/thesisDegree/mdent"
        if "mdes" in degree: uri = "http://canlink.library.ualberta.ca/thesisDegree/mdes"
        if "msw" in degree: uri = "http://canlink.library.ualberta.ca/thesisDegree/msw"
        if "mphysed" in degree: uri = "http://canlink.library.ualberta.ca/thesisDegree/mphysed"
        if "menvsc" in degree: uri = "http://canlink.library.ualberta.ca/thesisDegree/menv"
        if "doctor" in degree: uri = "http://id.loc.gov/authorities/subjects/sh85038715"
        if "doctoral" in degree: uri = "http://id.loc.gov/authorities/subjects/sh85038715"
        if "maîtrise" in degree or "maît" in degree or "matr" in degree: uri = "http://canlink.library.ualberta.ca/thesisDegree/master"
        if "phd" in degree: uri = "http://id.loc.gov/authorities/subjects/sh85038715"
        if "dba" in degree: uri = "http://canlink.library.ualberta.ca/thesisDegree/dba"
        if "dsc" in degree: uri = "http://id.loc.gov/authorities/subjects/sh85038715"
        if "des" in degree: uri = "http://canlink.library.ualberta.ca/thesisDegree/des"

        # check for longer sentences if the keywords aren't available
        degrees = {"masterofscience":"http://canlink.library.ualberta.ca/thesisDegree/msc", "masterofarts":"http://id.loc.gov/authorities/subjects/sh85081990", "masteroffinearts":"http://canlink.library.ualberta.ca/thesisDegree/mfa", "masterofappliedscience":"http://canlink.library.ualberta.ca/thesisDegree/masc", "masteroflaws":"http://id.loc.gov/authorities/subjects/sh2012003813", "masterofenvironmentalstudies":"http://canlink.library.ualberta.ca/thesisDegree/menv", "masterofeducation":"http://id.loc.gov/authorities/subjects/sh2010014261", "masterofnursing":"http://canlink.library.ualberta.ca/thesisDegree/mn", "masterofarchitecture":"http://canlink.library.ualberta.ca/thesisDegree/march", "masterofmathematics":"http://canlink.library.ualberta.ca/thesisDegree/mmath", "masterofhealthstudies":"http://canlink.library.ualberta.ca/thesisDegree/mhstud", "masterofcounselling":"http://canlink.library.ualberta.ca/thesisDegree/mcoun", "masterofengineering":"http://canlink.library.ualberta.ca/thesisDegree/meng", "masterofadvancedstudies":"http://canlink.library.ualberta.ca/thesisDegree/mas", "masterofphysicaleducation":"http://canlink.library.ualberta.ca/thesisDegree/mphysed", "masterofbusinessadministration":"http://id.loc.gov/authorities/subjects/sh85081991", "masterofworshipstudies":"http://canlink.library.ualberta.ca/thesisDegree/mws", "doctorofphilosophy":"http://id.loc.gov/authorities/subjects/sh85038715", "doctoralthesis":"http://id.loc.gov/authorities/subjects/sh85038715", "doctorofbusinessadministration":"http://canlink.library.ualberta.ca/thesisDegree/dba", "doctorofscience":"http://id.loc.gov/authorities/subjects/sh85038715"}
        
        if "master" in degree or "doctor" in degree:
            match = difflib.get_close_matches(degree, degrees.keys(), n=1, cutoff=0.90)
            if match:
                return(degrees[match[0]])
            return("http://canlink.library.ualberta.ca/thesisDegree/master")

        if uri: return(uri)

        return(None)

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
            # check if it exists in the sqlite database already
            r = c.execute("SELECT uri FROM advisors WHERE name like ? and university_uri like ? ", (name, self.universityUri,))
            rows = r.fetchall()
            
            if len(rows) >= 1:
                # found the advisor from the database - we have seen this person in a record before
                uris.append(rows[0][0])
                print("FOUND VALUE")
            
            elif self.universityUri:
                # generate a uri for this advisor and save it to the database for later
                uri = "http://canlink.library.ualberta.ca/Person/"+str(hashlib.md5(name.encode("utf-8")+self.universityUri.encode("utf-8")).hexdigest())
                # save the uri to the database so that it can be reused later 
                c.execute("INSERT INTO advisors VALUES(?, ?, ?)", (name, self.universityUri, uri,))
                print("ADDED VALUE")
                uris.append(uri)

        return uris

    def getContentUrl(self):
        value_856u = getField(self.record, "856", "u")

        if not value_856u:
            return None
            
        return([urllib.parse.quote(url, safe="%/:=&?~#+!$,;'@()*[]") for url in value_856u])
        # return(["<"+url+">" for url in value_856u])

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
        # date
        if self.date:
            g.add((URIRef(self.uri), DC.issued, Literal(self.date)))
        # language
        if self.language:
            g.add((URIRef(self.uri), DC.language, URIRef(self.language)))
        # degree
        if self.degreeUri:
            g.add((URIRef(self.uri), BIBO.degree, URIRef(self.degreeUri)))
            g.add((URIRef(self.degreeUri), RDF.type, BIBO.thesisDegree))
        # author uri
        g.add((URIRef(self.uri), DC.creator, URIRef(self.authorUri)))
        g.add((URIRef(self.uri), REL.author, URIRef(self.authorUri)))
        # author name
        g.add((URIRef(self.authorUri), FOAF.name, Literal(self.author)))
        # author type
        g.add((URIRef(self.authorUri), RDF.type, FOAF.Person))
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
                if self.subjectUris[subject]:
                    g.add((URIRef(self.uri), DC.subject, URIRef(self.subjectUris[subject])))
                else:
                    # the subject uri couldn't be found for this
                    # create a skos:concept node, add the subject heading string as rdfs:label of that new node and then link the new node as a subject heading of the current thesis - use md5 of the lower case value of the subject heading so we don't generate doubles (Rob - June 23)
                    newSubjectUri = "http://canlink.library.ualberta.ca/subject/" + hashlib.md5(subject.lower().encode("utf-8")).hexdigest()

                    g.add((URIRef(newSubjectUri), RDF.type, SKOS.Concept))
                    g.add((URIRef(newSubjectUri), RDFS.label, Literal(subject)))
                    g.add((URIRef(self.uri), DC.subject, URIRef(newSubjectUri)))
        # manifestation
        if self.manifestations:
            for index, manifestation in enumerate(self.manifestations):
                g.add((URIRef(manifestation), SCHEMA.encodesCreativeWork, URIRef(self.uri)))
                g.add((URIRef(manifestation), SCHEMA.contentUrl, URIRef(self.contentUrl[index])))
                g.add((URIRef(manifestation), RDF.type, FRBR.Manifestation))
                g.add((URIRef(manifestation), RDF.type, SCHEMA.MediaObject))



    def __str__(self):
        return """\nControl: \t%s\nTitle: \t\t%s\nURI: \t\t%s\nAuthor: \t%s\nAuthor Uri: \t%s\nUniversity: \t%s\nUniversity Uri: %s\nDate: \t\t%s\nLanguage: \t%s\nSubjects: \t%s\nSubjects Uris: \t%s\nDegree: \t%s\nDegree Uri: \t%s\nAdvisors: \t%s\nAdvisor Uris: \t%s\nContent Url: \t%s\nManifest.: \t%s
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
    attributes = ["title", "author", "university", "universityUri", "authorUri", "date", "language", "subjects", "subjectUris", "degree", "degreeUri", "advisors", "advisorUris", "contentUrl", "uri"]

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


def validateRecord(record):
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
    if record.control[0] == "R":
        recordNumber = record.control[1:]       # everything after "R" is the occurence number
        record_warnings.append("Record #" + recordNumber + " didn't have a control number - #" + record.control + " was assigned to it")

    errors[record.control] = record_errors
    warnings[record.control] = record_warnings
    
    return status

def main():
    # reader = MARCReader(open("files/MUN_4971_Theses_for_CLDI_linked.mrc", "rb"), force_utf8=True)
    # reader = MARCReader(open("files/qs_thesis.mrc", "rb"), force_utf8=True)
    reader = MARCReader(open("files/CLDI_LAC_bib_file_fixed.mrc", "rb"), force_utf8=True)
    # reader = MARCReader(open("files/U_Montreal_100_BibliographicRecords_from_IR.mrc", "rb"), force_utf8=True)
    # reader = MARCReader(open("files/U_Montreal_100_BibliographicRecords_from_IR.mrc", "rb"), force_utf8=True)

    # reader = MARCReader(open("files/LAC_CLDI_Authority_fixed.mrc", "rb"), force_utf8=True, utf8_handling='ignore', to_unicode=True)        # won't print anything since it doesnt have a title and the next few lines block empty entries
    # reader = MARCReader(open("files/qs_thesis.mrc", "rb"), force_utf8=True, utf8_handling='ignore', to_unicode=True)
    
    records = {}

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
            print("Control")
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
        print(thesis)
        if validateRecord(thesis):
            # if there were no errors (could still have warnings) then generate RDF
            thesis.generateRDF()
        print("-"*50)

    print(g.serialize(format="n3").decode("utf-8"))
    conn.commit()
    # conn.close()      causes a problem when refreshing the website and submitting again
    return(errors, warnings)

main()
    
