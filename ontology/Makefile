MAKEFLAGS += -J2
# "2010-01-01"^^xsd:date
ONTOLOGY=canlink
ONTOLOGY_DATE = $(shell date -u +"%Y-%m-%d")
DATE_CLEAN = $(shell date -u +"%Y%m%d")
ONTOLOGY_LONGDATE = $(shell date -d '$(ONTOLOGY_DATE)'  +'%d %B %Y')
ONTOLOGY_VERSION = $(shell xpath -e '/rdf:RDF/owl:Ontology/owl:versionInfo/text()' $(ONTOLOGY).owl  2> /dev/null)
ONTOLOGY_LOGO = $(shell xpath -e '/rdf:RDF/owl:Ontology/foaf:logo/@rdf:resource' $(ONTOLOGY).owl  2> /dev/null | sed 's/\//\\\//g' | cut -d "\"" -f 2)
PREVIOUS_ONTOLOGY = $(shell xpath -e '/rdf:RDF/owl:Ontology/owl:priorVersion/@rdf:resource' $(ONTOLOGY).owl  2> /dev/null | sed 's/\//\\\//g' | cut -d "\"" -f 2)
TOTAL_TRIPLES_CWRC_ONTOLOGY = $(shell cat $(ONTOLOGY)-$(ONTOLOGY_DATE).counts)
TOTAL_ENTITIES_CWRC_ONTOLOGY = $(shell cat $(ONTOLOGY)-$(ONTOLOGY_DATE).unique)
$(ONTOLOGY)-$(ONTOLOGY_DATE).tmp: $(ONTOLOGY).owl
	xpath -e "/rdf:RDF"  $(ONTOLOGY).owl  1> /dev/null 2> /dev/null
	echo $(DATE_CLEAN)
	LC_CTYPE=en_CA.UTF-8 sed 's/DATE_TODAY/$(DATE_CLEAN)/g' < $(ONTOLOGY).owl > $(ONTOLOGY)-$(ONTOLOGY_DATE).tmp    
$(ONTOLOGY)-$(ONTOLOGY_DATE).counts: $(ONTOLOGY)-$(ONTOLOGY_DATE).tmp
	rapper $(ONTOLOGY)-$(ONTOLOGY_DATE).tmp | wc -l > $(ONTOLOGY)-$(ONTOLOGY_DATE).counts
$(ONTOLOGY)-$(ONTOLOGY_DATE).unique: $(ONTOLOGY)-$(ONTOLOGY_DATE).tmp
	rapper $(ONTOLOGY)-$(ONTOLOGY_DATE).tmp | cut -d " " -f 1 | sort | sort -u | wc -l > $(ONTOLOGY)-$(ONTOLOGY_DATE).unique
$(ONTOLOGY)-$(ONTOLOGY_DATE).owl: $(ONTOLOGY)-$(ONTOLOGY_DATE).unique $(ONTOLOGY)-$(ONTOLOGY_DATE).counts $(ONTOLOGY)-$(ONTOLOGY_DATE).tmp
	cat $(ONTOLOGY)-$(ONTOLOGY_DATE).tmp | LC_CTYPE=en_CA.UTF-8 sed 's/ONTOLOGY_DATE/$(ONTOLOGY_DATE)/g' | LC_CTYPE=en_CA.UTF-8 sed 's/TOTAL_TRIPLES_CWRC_ONTOLOGY/$(TOTAL_TRIPLES_CWRC_ONTOLOGY)/g' | LC_CTYPE=en_CA.UTF-8 sed 's/TOTAL_ENTITIES_CWRC_ONTOLOGY/$(TOTAL_ENTITIES_CWRC_ONTOLOGY)/g' > $(ONTOLOGY)-$(ONTOLOGY_DATE).owl       
$(ONTOLOGY)-$(ONTOLOGY_DATE).nt: $(ONTOLOGY)-$(ONTOLOGY_DATE).owl
	rapper $(ONTOLOGY)-$(ONTOLOGY_DATE).owl > $(ONTOLOGY)-$(ONTOLOGY_DATE).nt
$(ONTOLOGY)-$(ONTOLOGY_DATE).ttl: $(ONTOLOGY)-$(ONTOLOGY_DATE).owl
	rapper -o turtle $(ONTOLOGY)-$(ONTOLOGY_DATE).owl > $(ONTOLOGY)-$(ONTOLOGY_DATE).ttl  
all: $(ONTOLOGY)-$(ONTOLOGY_DATE).nt $(ONTOLOGY)-$(ONTOLOGY_DATE).owl $(ONTOLOGY)-$(ONTOLOGY_DATE).ttl

clean: rm canlink-*-*-*.*
