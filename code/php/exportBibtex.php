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
header('Content-Type: application/x-bibtex');
header('Content-Disposition: attachment; filename="' . substr( strrchr($URI,"/"),1) . '.bib"');
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
print "@Comment{This is an export from " . $storeName . " \\url{http://canlink.library.ualberta.ca/}}\n";
print "@Comment{Provient de " . $storeName . " \\url{http://canlink.library.ualberta.ca/}}\n";
//print $row["degree"];
$degree="mastersthesis";
if ( strpos(strtolower($row["degree"]) ,"/ph") > 0 ) {
 $degree="phdthesis";
}
print '@' . $degree;
print '{' . substr( strrchr($URI,"/"),1) . ",\n";
print "author={" . $row["authorname"] . "},\n";
print "title={" . $row["title"] . "},\n";
print "year={" . $row["year"] . "},\n";
print "school={" . $row["university"] . "},\n";
if ($row["advisorName"]) {
 print "advisor={" . $row["advisorName"] . "},\n";
}
if ($row["abstract"]) {
 print "abstract={" . $row["abstract"] . "},\n";
}
if ($row["pdfurl"]) {
 print "url={" . $row["pdfurl"] . "},\n";
} else {
 print 'url={' . $URI . "},\n";
}
print 'annote={Citation downloaded from \url{' . $URI . "}}\n";
print "}\n";
}
?>