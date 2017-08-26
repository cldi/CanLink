<?

//Bibtex export
//
@Comment{This is an export from CanLink}


select ?title, ?authorname, ?year, ?schoolname, ?uri, ?degree, 

WHERE {
?uri dc:title ?title .
?uri dc:creator ?author . 
?author foaf:name ?authorname . 
?uri dc:issued ?year .
?uri dc:publisher ?school .
?uri foaf:name ?schoolname .
?uri bibo:degree ?degree .
?degree rdf:type bibo:thesisDegree . 
?uri rdf:type bibo:thesis .
?uri rdf:type FRBR:Work . 
option 


@PHDTHESIS{
 Required fields: author, title, school, year

Optional fields: address, month, note, key 
doi, advisor, abstract, url, pdf, keywords,


//
//https://raw.githubusercontent.com/clarkgrubb/latex-input/master/latex.el
     @MASTERSTHESIS{citation_key,
                    required_fields [, optional_fields] }

Required fields: author, title, school, year

Optional fields: address, month, note, key 