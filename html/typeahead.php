<?php require_once( "sparqllib.php" );
$storeURL = "http://canlink.library.ualberta.ca/sparql";
error_reporting(E_ALL); 
 $db = sparql_connect($storeURL );
 if (( $db->alive()) && ($_GET["term"])) {
$result = sparql_query("
SELECT distinct ?uri ?value WHERE {
{   
   ?uri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/ontology/bibo/thesis> .  
   OPTIONAL {?uri <http://purl.org/dc/terms/abstract> ?value . }
   OPTIONAL {?uri <http://purl.org/dc/terms/title> ?value . }
   OPTIONAL {?uri <http://purl.org/dc/terms/issued> ?value . } 
   OPTIONAL {?uri <http://www.w3.org/2000/01/rdf-schema#label> ?value . }
   filter (regex(?value, '" . $_GET["term"]  . "','i'))
} UNION {

   ?uri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://www.w3.org/2002/07/owl#Thing> . 
   OPTIONAL {?uri <http://xmlns.com/foaf/0.1/name> ?value . }
   OPTIONAL {?uri <http://xmlns.com/foaf/0.1/lastName> ?value . }
   OPTIONAL {?uri <http://xmlns.com/foaf/0.1/firstName> ?value . }
   OPTIONAL {?uri <http://www.w3.org/2000/01/rdf-schema#label> ?value . }
   filter (regex(?value, '" . $_GET["term"]  . "','i'))
}UNION {

   ?uri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://xmlns.com/foaf/0.1/Person> . 
   OPTIONAL {?uri <http://xmlns.com/foaf/0.1/name> ?value . }
   OPTIONAL {?uri <http://xmlns.com/foaf/0.1/lastName> ?value . }
   OPTIONAL {?uri <http://xmlns.com/foaf/0.1/firstName> ?value . }
   OPTIONAL {?uri <http://www.w3.org/2000/01/rdf-schema#label> ?value . }
   filter (regex(?value, '" . $_GET["term"]  . "','i'))
}UNION {

   ?uri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>  <http://www.w3.org/2004/02/skos/core#Concept> . 
   OPTIONAL {?uri <http://xmlns.com/foaf/0.1/name> ?value . }
   OPTIONAL {?uri <http://www.w3.org/2004/02/skos/core#prefLabel> ?value . }
   OPTIONAL {?uri <http://www.w3.org/2004/02/skos/core#altLabel> ?value . }
   OPTIONAL {?uri <http://www.w3.org/2000/01/rdf-schema#label> ?value . }
   filter (regex(?value, '" . $_GET["term"]  . "','i'))
}
   
  } order by strlen(str(?value)) limit 15
");
$array = array();
while( $row = sparql_fetch_array( $result ) )
{
        $array[] = array (
            'label' => $row["value"], 'value' => $row["uri"], 'id'  => $row["uri"]);        
}
echo json_encode ($array);
}
?>
