
from pymarc import MARCReader
import hashlib
import re
import difflib
import pickle
import fnmatch
import codecs
import unidecode

# load the pickle objects that will be used for university and subject uri generation
with open("files/universities.pickle", "rb") as handle:
    universities = pickle.load(handle)      # key: name, value: uri

with open("files/subjects.pickle", "rb") as handle:
    subjects = pickle.load(handle)      # key: subject name, value: uri

university_uri_cache = {}

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
        self.contentUrl = self.getContentUrl()
        self.uri = self.getURI()

    def getControlNumber(self):
        
        return(str(getField(self.record, "001")).split()[1])

    def getLinkingControlNumber(self):
        value_004 = getField(self.record, "004")
        
        if not value_004:
            return None
        
        return(str(value_004).split()[1])

    def getAuthorName(self):
        value_100a = getField(self.record, "100", "a")

        if not value_100a: 
            return None

        return(value_100a[0].strip("."))

    def getAuthorUri(self):
        if not self.author:
            return None
            
        return("<http://canlink.library.ualberta.ca/Person/"+str(hashlib.md5(self.author.encode("utf-8")+self.university.encode("utf-8")).hexdigest()+">"))

    def getTitle(self):
        if not self.record.title():
            return None
        return(self.record.title().strip("/"))

    def getUniversity(self): 

        value_502c = getField(self.record, "502" "c")
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
            university = value_502a[0].split("--")[-1].split(",")[0]
        elif value_264b: 
            university = value_264b[0]
        elif value_260b: 
            university = value_260b[0]

        if not university:
            return None

        # remove the extra characters
        university = university.replace(".", "").replace(",", "").strip()
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
            print("Found in cache: ", universityName)
            return(university_uri_cache[universityName])    
        else:
            
            # get the names of the universities
            universityNames = universities.keys()

            print("Processing: ", universityName)
            # find the closest university name in the list of names
            match = difflib.get_close_matches(universityName, universityNames, n=1)

            if match:
                uri = "<"+universities[match[0]]+">"
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
        value_650a = getField(self.record, "650", "a")
        value_653a = getField(self.record, "653", "a")

        subjects = []

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

        URIs = []
        for subject in self.subjects:
            if subject.lower() in subjects.keys():
                URIs.append(subjects[subject.lower()])

        return URIs
    
    def getLanguage(self):
        value_008 = getField(self.record, "008")
        value_040b = getField(self.record, "040", "b")
        value_041a = getField(self.record, "041", "a")

        language = None

        if value_041a: 
            language = value_041a[0]
        elif value_040b: 
            language = value_040b[0]
        elif value_008: 
            language = str(value_008).split()[1][35:38]

        # generate the LOC Language URI
        # can just append the code to the end since the Marc records already follow this format
        if not language:
            return None        # the language code is given by characters 35-37 of tag 008
        
        return("<http://id.loc.gov/vocabulary/languages/"+language+">")

    def getDegree(self):
        value_502a = getField(self.record, "502", "a")
        value_502b= getField(self.record, "502", "b")

        degree = None

        if value_502b: 
            degree = value_502b[0]
        elif value_502a: 
            if "--" in value_502a[0]:
                # split by -- and take every section except the last one
                # ex: Inaug.--Diss.--Heidelberg, 1972. --> Inaug. Diss.
                # if there is only one "--" then it just gets the first section
                # which should be the degree type
                degree = " ".join(value_502a[0].split("--")[:-1])

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

        degree = ''.join([i for i in degree if i.isalpha() or i == " "]).lower()
        uri = None
        # do the basic ones
        if "msc" in "".join(degree.split()): uri = "msc"
        if "masc" in "".join(degree.split()): uri = "masc"
        if "ma" in degree.split(): uri = "ma"
        if "phd" in "".join(degree.split()): uri = "phd"
        if "dba" in degree.split(): uri = "dba"
        if "dent" in degree.split() or "mdent" in degree.split(): uri = "mdent"
        if "mdes" in degree.split(): uri = "mdes"
        if "msw" in degree.split(): uri = "msw"
        if "doctor" in degree.split(): uri = "phd"
        if "doctoral" in degree.split(): uri = "phd"
        if "mn" in degree.split(): uri = "mn"
        if "llm" in degree.split(): uri = "llm"
        if "mhk" in degree.split(): uri = "mhk"
        if "mpp" in degree.split(): uri = "mpp"
        if "maed" in degree.split(): uri = "maed"
        if "mfa" in degree.split(): uri = "mfa"
        if "sjd" in degree.split(): uri = "sjd"
        if "edd" in degree.split(): uri = "edd"

        if uri: return("http://canlink.library.ualberta.ca/thesisDegree/"+uri)

        # check for longer sentences if the keywords aren't available
        # try to search for the specific ones but if the degree name is not close enough, just return Masters if it contains "master" or None "if it doesn't" (phd already taken care of)
        masterOf = {"master of science":"msc", "master of arts":"ma", "master of applied science":"masc", "master of laws":"llm", "master of environmental studies":"menv", "master of education":"medu", "master of nursing":"mn", "master of architecture":"march", "master of mathematics":"mmath", "master of health studies":"mhstud", "master of counselling":"mcoun"}
        
        if "master" in degree:
            match = difflib.get_close_matches(degree, masterOf.keys(), n=1, cutoff=0.90)
            if match:
                return("http://canlink.library.ualberta.ca/thesisDegree/"+masterOf[match[0]])
            return("http://canlink.library.ualberta.ca/thesisDegree/master")

        return(None)

    def getAdvisors(self):
        value_500a = getField(self.record, "500", "a")
        value_720a= getField(self.record, "720", "a")
        
        if value_720a: 
            return(value_720a)

        if value_500a:
            # check if it follows the format given in this document
            # http://media2.proquest.com/documents/tags-marcxml.pdf
            if "Advisors:" in value_500a:
                return([advisor for advisor in value_500a.replace("Advisors:", "").strip().split(";")])
        
        return None

    def getContentUrl(self):
        value_856u = getField(self.record, "856", "u")

        if not value_856u:
            return None
            
        return(["<"+url+">" for url in value_856u])

    def getURI(self):
        if self.author and self.title:
            identifier = hashlib.md5((str(self.author).encode("utf-8") + str(self.title).encode("utf-8"))).hexdigest()
            return("<http://canlink.library.ualberta.ca/thesis/"+str(identifier)+">")
        return None  

    def __str__(self):
        return """\nControl: \t%s\nTitle: \t\t%s\nURI: \t\t%s\nAuthor: \t%s\nAuthor Uri: \t%s\nUniversity: \t%s\nUniversity Uri: %s\nDate: \t\t%s\nLanguage: \t%s\nSubjects: \t%s\nSubjects Uris: \t%s\nDegree: \t%s\nDegree Uri: \t%s\nAdvisors: \t%s\nContent Url: \t%s
        """ % (self.control, self.title, self.uri, self.author, self.authorUri, self.university, self.universityUri, self.date, self.language, self.subjects, self.subjectUris, self.degree, self.degreeUri, self.advisors, self.contentUrl)

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
    attributes = ["title", "author", "university", "universityUri", "authorUri", "date", "language", "subjects", "subjectUris", "degree", "degreeUri", "advisors", "contentUrl", "uri"]

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

def upload(records_file):
    # reader = MARCReader(open("CLDI_LAC_bib_file_fixed.mrc", "rb"), force_utf8=True, utf8_handling='ignore', to_unicode=True)
    reader = MARCReader(records_file, force_utf8=True)
    #reader = MARCReader(open("files/LAC_CLDI_Authority_fixed.mrc", "rb"), force_utf8=True, utf8_handling='ignore', to_unicode=True)        # won't print anything since it doesnt have a title and the next few lines block empty entries
    #reader = MARCReader(open("files/qs_thesis.mrc", "rb"), force_utf8=True, utf8_handling='ignore', to_unicode=True)
    
    records = {}

    # process and merge the records
    for record in reader: 
        # read record
        thesis = Thesis(record)
        # get control number and linking number
        controlNumber = thesis.control
        linkingNumber = thesis.linking
        # if no linking number, check if the control number shows up as a linking number of any other record -> merge them 
        # if linking number, check if the linking number shows up as a control number of any other record -> merge them

        if linkingNumber and linkingNumber in records.keys():
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
        print("-"*50)

    
