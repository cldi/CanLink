<?php

//Bibtex export
//
require_once( "sparqllib.php" );
$mylang=strtolower($_GET["lang"]);
if ((strlen($mylang) < 2) || 
( ! in_array($mylang, array("en","fr","de","es")))) {
$mylang="en";
}
$storeName ="CanLink - CanaLien";
$storeURL = "http://canlink.library.ualberta.ca/sparql";
//$URI="http://canlink.library.ualberta.ca/thesis/b1d69d5514023b77b1b1908355c65114";
//$URI="http://canlink.library.ualberta.ca/thesis/b5a2c518f0f81edc5ab2f8227b8e981c";
$URI=$_GET["url"];
$URIBits = parse_url($URI);
//error_reporting(E_ALL);
$db = sparql_connect($storeURL );
if (! $db->alive()) {
  print "500 Server failiure";
 } else {
header('Content-Type: application/x-research-info-systems');
header('Content-Disposition: attachment; filename="' . substr( strrchr($URI,"/"),1) . '.ris"');
header("HTTP/1.0 200 OK");
$sparqlQuery = "
SELECT ?title ?year (SAMPLE(COALESCE(?universityReq,?universityEN,?universityANY))) as ?university 
   (SAMPLE(COALESCE(?fullname, CONCAT(?firstName, \" \", ?lastName)))) as ?authorname ?advisorName
   (SAMPLE(COALESCE(?abstractReq, ?abstractEN, ?abstractANY))) as ?abstract ?degree ?pdfurl
    WHERE { 
   <" . $URI . "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/ontology/bibo/thesis> . 
   <" . $URI . "> <http://purl.org/dc/terms/title> ?title .
   <" . $URI . "> <http://purl.org/dc/terms/issued> ?year .
   <" . $URI . "> <http://purl.org/dc/terms/creator> ?author .
   <" . $URI . "> <http://purl.org/ontology/bibo/degree> ?degree .
   OPTIONAL {?author <http://xmlns.com/foaf/0.1/name> ?fullname . }
   OPTIONAL {?author <http://xmlns.com/foaf/0.1/lastName> ?lastName . }
   OPTIONAL {?author <http://xmlns.com/foaf/0.1/firstName> ?firstName . }
   OPTIONAL {  <" . $URI . ">  <http://id.loc.gov/vocabulary/relators/ths> ?advisor .
              ?advisor <http://xmlns.com/foaf/0.1/name> ?advisorName . } 
   OPTIONAL { <" . $URI . ">  <http://purl.org/dc/terms/publisher> ?uni .
             ?uni <http://xmlns.com/foaf/0.1/name> ?universityReq . 
             FILTER(LANG(?universityReq) = \"" . $mylang  . "\") }
   OPTIONAL { <" . $URI . ">  <http://purl.org/dc/terms/publisher> ?uni .
             ?uni <http://xmlns.com/foaf/0.1/name> ?universityANY .  }
   OPTIONAL { <" . $URI . ">  <http://purl.org/dc/terms/publisher> ?uni .
             ?uni <http://xmlns.com/foaf/0.1/name> ?universityEN . 
             FILTER(LANG(?universityEN) = \"en\") }
   OPTIONAL { <" . $URI . "> <http://purl.org/dc/terms/abstract> ?abstractReq .
             FILTER(LANG(?abstractReq) = \"" . $mylang  . "\") }
   OPTIONAL { <" . $URI . "> <http://purl.org/dc/terms/abstract> ?abstractANY . }
   OPTIONAL { <" . $URI . "> <http://purl.org/dc/terms/abstract> ?abstractEN .
             FILTER(LANG(?abstractEN) = \"en\") }         
   OPTIONAL {  ?themanifestation <http://schema.org/encodesCreativeWork> <" . $URI . "> .
               ?themanifestation  <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/vocab/frbr/core#Manifestation> .
                ?themanifestation <http://schema.org/contentUrl> ?pdfurl .
                FILTER regex(STR(?pdfurl), \"pdf\$\", \"i\" )}                
    
  }";
$result = sparql_query($sparqlQuery);
$row = sparql_fetch_array( $result );
$degree="Masters Thesis";
$degreeT ="MAST";
if ( strpos(strtolower($row["degree"]) ,"/ph") > 0 ) {
 $degree="Phd Thesis";
 $degreeT ="PHDT";
}
print "TY  - " . $degreeT  . "\n";
if ($row["advisorName"]) {
 print "A3  - " . $row["advisorName"] . "\n";
}
if ($row["abstract"]) {
 print "AB  - " . $row["abstract"] . "\n";
}
print "AU  - " . $row["authorname"] . "\n";
print "DA  - " . $row["year"] . "\n";
print "DB  - CanLink\n";
//print "DO   -	DOI\n";
print "DP  - CanLink\n";
//print "KW   -	Keywords\n";
//print "L1   -	File Attachments\n";
//print "L4   -	Figure\n";
//print "LA   -	Language\n";
//print "LB   -	Label\n";
//print "M1   - 	Document Number\n";
print "M3  - " . $degree . "\n";
print "PB  - " . $row["university"] . "\n";
print "PY  - " . $row["year"] . "\n";
//print "SP   -	Number of Pages\n";
//print "T2   -	Academic Department\n";
//print "TA   -	Translated Author\n";
print "T1  - " . $row["title"] . "\n";
if ($row["pdfurl"]) {
 print "UR  - " . $row["pdfurl"] . "\n";
} else {
 print "UR  - " . $URI . "\n";
}
print "VL  - " . $degree . "\n";
//print "Y2   -	Access Date\n";
print "ER  - \n";
}
?>
