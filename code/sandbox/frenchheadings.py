from rdflib import Graph
import pickle
import difflib

g = Graph()

# load the french headings
g.parse("csh.rdf", format="xml")

print(len(g))

count = 0

english = {}        # englishURI : englishLabel
related = {}        # frenchURI : englishURI
french = {}         # frenchURI : frenchLabel
final = {}          # frenchLabel : englishLabel

with open("files/subjects.pickle", "rb") as handle:
    subjects = pickle.load(handle)

for item in g:
    if str(item[1]) == "http://www.w3.org/2004/02/skos/core#prefLabel":
        if str(item[0][0]) == "N":
            # french uri to french label
            french[str(item[0])] = str(item[2])
        else:
            english[str(item[0])] = str(item[2])
        # print(item[0], item[1], item[2])

    # in the format englishuri related frenchuri
    elif str(item[1]) == 'http://www.w3.org/2004/02/skos/core#related' and str(item[2][0]) == "N":
        # print(item[0], item[1], item[2])
        related[str(item[2])] = str(item[0])
        #count += 1

# join them together
for french_uri in related:
    # print(french[french_uri])
    french_label = french[french_uri].lower().replace(" -- ", "--")
    english_label = english[related[french_uri]].lower().replace(" canada -- ", "").replace("canada --","").replace(" -- ", "--").replace("-- ", "--").replace(" --", "--").strip("-., ")

    if english_label in subjects:
        final[french_label] = subjects[english_label]

with open('subjects_french.pickle', 'wb') as handle:
    pickle.dump(final, handle, protocol=pickle.HIGHEST_PROTOCOL)

