<?

//Bibtex export
//
@Comment{This is an export from CanLink}


select *

WHERE {
?uri dc:title ?title .
?uri dc:creator ?author . 
?author foaf:name ?authorname . 
?uri dc:issued ?year .
?uri dc:publisher ?school .
?uri bibo:degree ?degree .
?degree rdf:type bibo:thesisDegree . 
?uri rdf:type bibo:thesis .
?uri rdf:type FRBR:Work . 
optional { ?uri owl:sameAs ?doi . }
optional { ?uri foaf:name ?schoolname . }
optional { ?uri schema:encodesCreativeWork ?manifestion .
?manifestion schema:contentURL ?pdf . }
optional { ?uri rel:ths ?advisor .
?advisor foaf:name ?advisorname . }
optional { ?uri bibo:numPages ?pages . }

//keywork
//abstract

TY - THES
A3  -	Advisor
AB  -	Abstract
AU  -	Author
DA  - 	Date
DB - CanLink
DO  -	DOI
DP  -	Database Provider
KW  -	Keywords
L1  -	File Attachments
L4  -	Figure
LA  -	Language
LB  -	Label
M1  - 	Document Number
M3  -	Thesis Type
PB  -	University
PY  -	Year
SP  -	Number of Pages
T2  -	Academic Department
TA  -	Translated Author
TI  -	Title
UR  -	URL
VL  - 	Degree
Y2  -	Access Date
ER  -	{IGNORE}
