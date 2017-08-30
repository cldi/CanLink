# this script will find all the theses in the triplestore and find the PDF links and the length of the PDF
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import defaultdict
import requests
from bs4 import BeautifulSoup
import ssl
from io import StringIO, BytesIO
from PyPDF2.pdf import PdfFileReader
import urllib.parse
from urllib.request import urlopen, urlparse
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

context = ssl._create_unverified_context()

def getPDFUrl(url):
    # finds the pdf link on the website
    r = requests.get(url, verify=False)
    html = r.text
    redirect_url = r.url

    soup = BeautifulSoup(html, "html.parser")

    # see if there is any ".pdf" link on the page
    pdf_url = ""

    links = []
    for link in soup.find_all("a"):
        l = link.get("href")
        links.append(l)
        if ".pdf" in str(l).lower():
            if (pdf_url == "" or len(pdf_url) > len(str(l))):
                pdf_url = str(l)

    # convert relative links to absolute links if necessary
    if pdf_url and "http" not in pdf_url and "www" not in pdf_url:
        if pdf_url[0] == "/":
            base_url = '{uri.scheme}://{uri.netloc}'.format(uri=urllib.request.urlparse(redirect_url))
            pdf_url = base_url + pdf_url
        else:
            pdf_url = redirect_url + pdf_url

    # if the ".pdf" url was found - properly format it and return
    if pdf_url:
        pdf_url = urllib.parse.quote(pdf_url, safe="%/:=&?~#+!$,;'@()*[]")
        # print("PDF URL:", pdf_url)
        return(pdf_url)
        # return {"pdf_url":pdf_url, "record_id":record_id}
    # else:
    #     # couldn't find a pdf link  - go through all the links to see which is of pdf type
    #     # (not ".pdf" extension because some pdfs don't have a ".pdf" extension)
    #     for link in links:
    #         if link and link[0:4] == "http":
    #             r = requests.get(link, verify=False)
    #             if "pdf" in r.headers["Content-Type"]:
    #                 pdf_url = urllib.parse.quote(r.url, safe="%/:=&?~#+!$,;'@()*[]")
    #                 return(pdf_url)
    #                 # print("PDF URL:", pdf_url)
    #                 # return {"pdf_url":pdf_url, "record_id":record_id}

def getNumPages(url):
    try:
        pdf_request = requests.get(pdf_url, verify=False)
        pdf_object = BytesIO(pdf_request.content)
        num_pages = PdfFileReader(pdf_object).getNumPages()
        return(num_pages)
    except:
        pass

def addManifestation(thesis_uri, url):
    sparql = SPARQLWrapper("http://18ed7af0.ngrok.io/canlink/update")
    sparql.setQuery("""
    PREFIX void:  <http://rdfs.org/ns/void#>
    PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX doap:  <http://usefulinc.com/ns/doap#>
    PREFIX owl:   <http://www.w3.org/2002/07/owl#>
    PREFIX rel:   <http://id.loc.gov/vocabulary/relators/>
    PREFIX bibo:  <http://purl.org/ontology/bibo/>
    PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX cwrc:  <http://sparql.cwrc.ca/ontologies/genre#>
    PREFIX prov:  <http://www.w3.org/ns/prov#>
    PREFIX foaf:  <http://xmlns.com/foaf/0.1/>
    PREFIX dc:    <http://purl.org/dc/terms/>
    PREFIX schema: <http://schema.org/>
    PREFIX frbr: <http://purl.org/vocab/frbr/core#>

    INSERT DATA{
	<%s> dc:subject <%s>
    }
    """%(thesis_uri, url))

    sparql.method = "POST"
    # sparql.query()

    print("Adding Manifestation for:", thesis_uri, "with content url =", url)


def addNumPages(thesis_uri, num_pages):
    print("Adding numPages for:", thesis_uri, "with numPages =", num_pages)

sparql = SPARQLWrapper("http://18ed7af0.ngrok.io/canlink/sparql")

sparql.setQuery("""
PREFIX void:  <http://rdfs.org/ns/void#>
PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX doap:  <http://usefulinc.com/ns/doap#>
PREFIX owl:   <http://www.w3.org/2002/07/owl#>
PREFIX rel:   <http://id.loc.gov/vocabulary/relators/>
PREFIX bibo:  <http://purl.org/ontology/bibo/>
PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
PREFIX cwrc:  <http://sparql.cwrc.ca/ontologies/genre#>
PREFIX prov:  <http://www.w3.org/ns/prov#>
PREFIX foaf:  <http://xmlns.com/foaf/0.1/>
PREFIX dc:    <http://purl.org/dc/terms/>
PREFIX schema: <http://schema.org/>
PREFIX frbr: <http://purl.org/vocab/frbr/core#>

SELECT ?thesis ?url
WHERE {
	?thesis rdf:type bibo:thesis .
    ?thesis owl:sameAs ?url .
    MINUS { ?thesis bibo:numPages ?c . }
}
""")



# run the query and put the results in a dictionary with the values being a list of urls associated with the thesis uri
data = defaultdict(list)

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for thesis in results["results"]["bindings"]:
    thesis_uri = thesis["thesis"]["value"]
    url = thesis["url"]["value"]

    data[thesis_uri].append(url)

# process each thesis individually
for thesis_uri in data:
    urls = data[thesis_uri]

    num_pages = 0
    # go through all the urls and find the pdf links for all of them
    # find the num_pages from the first url
    print("-"*50)
    for url in urls:
        # print(url)
        if ".pdf" not in url.lower():
            pdf_url = getPDFUrl(url)

            if pdf_url:
                addManifestation(thesis_uri, pdf_url)
        else:
            pdf_url = url

        if pdf_url and num_pages == 0:
            num_pages = getNumPages(url)
            addNumPages(thesis_uri, num_pages)

            # TODO add the numPages value to the thesis object

        # print()
        elif urls.index(url) == len(urls)-1:
            # if this is the last url given for this thesis and we still don't have a num_pages
            # then put in numPages = N/A
            # if we don't do this, this record will come up again everytime this function is called
            # and it won't be able to find the number of pages ever due to a broken link

            addNumPages(thesis_uri, num_pages="N/A")
        # print(url, num_pages)

    # print(thesis_uri)
