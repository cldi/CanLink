<?

//Bibtex export
//
require_once( "sparqllib.php" );
$mylang=strtolower($_GET["lang"]);
if ((strlen($mylang) < 2) || ( ! $mylang in_array(array("en","fr","de","es")))) {
$mylang="en";
}
$storeName ="CanLink - CanaLien";
$storeURL = "http://canlink.library.ualberta.ca/sparql";
$URI=$_GET["URI"];
$URIBits = parse_url($URI);
error_reporting(E_ALL);
$db = sparql_connect($storeURL );
if (! $db->alive()) {
  print "500 Server failiure";
 } else {
$result = sparql_query("
SELECT ?title ?year (SAMPLE(COALESCE(?universityReq,?universityEN,?universityANY)) as ?university 
   (SAMPLE(COALESCE(?fullname, CONCAT(?firstName, " ", ?lastName)))) as ?authorname ?advisorName
   (SAMPLE(COALESCE(?abstractReq, ?abstractEN, ?abstractANY))) as ?abstract ?degree   
    WHERE { 
   <" . $URI . "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/ontology/bibo/thesis> . 
   <" . $URI . "> <http://purl.org/dc/terms/title> ?title .
   <" . $URI . "> <http://purl.org/dc/terms/issued> ?year .
   <" . $URI . "> <http://id.loc.gov/vocabulary/relators/aut> ?author .
   <" . $URI . "> <http://purl.org/ontology/bibo/degree> ?degree .
   OPTIONAL {?author <http://xmlns.com/foaf/0.1/name> ?fullname }
   OPTIONAL {?author <http://xmlns.com/foaf/0.1/lastName> ?lastName }
   OPTIONAL {?author <http://xmlns.com/foaf/0.1/firstName> ?firstName }
   OPTIONAL {  <" . $URI . ">  <http://id.loc.gov/vocabulary/relators/ths> ?advisor .
              ?advisor <http://xmlns.com/foaf/0.1/name> ?advisorName . } 
   OPTIONAL { <" . $URI . ">  <http://id.loc.gov/vocabulary/relators/pub> ?uni .
             ?uni <http://xmlns.com/foaf/0.1/name> ?universityReq . 
             FILTER(LANG(?universityReq) = \"" . $mylang  . "\") }
   OPTIONAL { <" . $URI . ">  <http://id.loc.gov/vocabulary/relators/pub> ?uni .
             ?uni <http://xmlns.com/foaf/0.1/name> ?universityANY .  }
   OPTIONAL { <" . $URI . ">  <http://id.loc.gov/vocabulary/relators/pub> ?uni .
             ?uni <http://xmlns.com/foaf/0.1/name> ?universityEN . 
             FILTER(LANG(?universityEN) = \"en\") }
   OPTIONAL { <" . $URI . "> <http://purl.org/dc/terms/abstract> ?abstractReq .
             FILTER(LANG(?abstractReq) = \"" . $mylang  . "\") }
   OPTIONAL { <" . $URI . "> <http://purl.org/dc/terms/abstract> ?abstractANY .
   OPTIONAL { <" . $URI . "> <http://purl.org/dc/terms/abstract> ?abstractEN .
             FILTER(LANG(?abstractEN) = \"en\") }          
  }");
$row = sparql_fetch_array( $result );
print "@Comment{This is an export from " . $storeName ."}"
print "@Comment{Provient de " . $storeName ."}";

$degree="MASTERSTHESIS";
if ( strpos(strtolower($row["degree"]) ,"/p") > 0 ) {
 $degree="PHDTHESIS";
}
print $degree;
print substr( strrchr($URI,"/"),1) . ",";
print "author={" . $row["authorname"] . "},";
print "title={" . $row["title"] . "},";
print "year={" . $row["year"] . "},";
print "school={" . $row["univesity"] . "},";
if ($row["advisorName"])
 print "advisor={" . $row["advisorName"] . "},";
}
if ($row["abstract"])
 print "abstract={" . $row["abstract"] . "},";
}

//@PHDTHESIS{
//Required fields: author, title, school, year
//Optional fields: address, month, note, key 
//doi, advisor, abstract, url, pdf, keywords,
//https://raw.githubusercontent.com/clarkgrubb/latex-input/master/latex.el
     @MASTERSTHESIS{citation_key,
                    required_fields [, optional_fields] }

Required fields: author, title, school, year

Optional fields: address, month, note, key UU