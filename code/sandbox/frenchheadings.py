from rdflib import Graph

g = Graph()

# load the french headings
g.parse("csh.rdf", format="xml")

print(len(g))

count = 0
for item in g:
    # if str(item[1]) in ['http://www.w3.org/2004/02/skos/core#altLabel', 'http://www.w3.org/2004/02/skos/core#prefLabel']:
    print(item)
        #count += 1

print(count)

