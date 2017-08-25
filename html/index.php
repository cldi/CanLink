<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?php require_once( "sparqllib.php" );
$storeName ="CanLink - CanaLien";
$storeURL = "http://canlink.library.ualberta.ca/sparql";
error_reporting(E_ALL); php?>
<html xmlns="http://www.w3.org/1999/xhtml">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title><?php print $storeName; ?> SPARQL Server</title>
<link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
<script src="https://code.jquery.com/jquery-1.12.4.js"></script>
	<script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
<script>
$(function() { 

    $("#txtSearch").autocomplete({
        source: "typeahead.php"
    });
 
});
</script>
<style type="text/css" media="screen">

.ui-autocomplete {
z-index: 100;
}
/* highlight results */
.ui-autocomplete span.hl_results {
    background-color: #ffff66;
}
 
/* loading - the AJAX indicator */
.ui-autocomplete-loading {
    background: white url('../img/ui-anim_basic_16x16.gif') right center no-repeat;
}
 
/* scroll results */
.ui-autocomplete {
    max-height: 250px;
    overflow-y: auto;
    /* prevent horizontal scrollbar */
    overflow-x: hidden;
    /* add padding for vertical scrollbar */
    padding-right: 5px;
}
 
.ui-autocomplete li {
    font-size: 16px;
}
 
/* IE 6 doesn't support max-height
* we use height instead, but this forces the menu to always be this tall
*/
* html .ui-autocomplete {
    height: 250px;
}

  * {
    margin: 0px 0px 0px 0px;
    padding: 0px 0px 0px 0px;
  }

  body, html {
    padding: 3px 3px 3px 3px;

    background-color: #D8DBE2;

    font-family: Verdana, sans-serif;
    font-size: 11pt;
    text-align: center;
  }

  div.main_page {
    position: relative;
    display: table;

    width: 1000px;

    margin-bottom: 3px;
    margin-left: auto;
    margin-right: auto;
    padding: 0px 0px 0px 0px;

    border-width: 2px;
    border-color: #212738;
    border-style: solid;

    background-color: #FFFFFF;

    text-align: center;
  }

  div.page_header {
    height: 99px;
    width: 100%;

    background-color: #F5F6F7;
  }

  div.page_header span {
    margin: 15px 0px 0px 50px;

    font-size: 180%;
    font-weight: bold;
  }

  div.page_header img {
    margin: 3px 0px 0px 40px;

    border: 0px 0px 0px;
  }

  div.table_of_contents {
    clear: left;

    min-width: 200px;

    margin: 3px 3px 3px 3px;

    background-color: #FFFFFF;

    text-align: left;
  }

  div.table_of_contents_item {
    clear: left;

    width: 100%;

    margin: 4px 0px 0px 0px;

    background-color: #FFFFFF;

    color: #000000;
    text-align: left;
  }

  div.table_of_contents_item a {
    margin: 6px 0px 0px 6px;
  }

  div.content_section {
    margin: 3px 3px 3px 3px;

    background-color: #FFFFFF;

    text-align: left;
  }

  div.content_section_text {
    padding: 4px 8px 4px 8px;

    color: #000000;
    font-size: 100%;
  }

  div.content_section_text pre {
    margin: 8px 0px 8px 0px;
    padding: 8px 8px 8px 8px;

    border-width: 1px;
    border-style: dotted;
    border-color: #000000;

    background-color: #F5F6F7;

    font-style: italic;
  }

  div.content_section_text p {
    margin-bottom: 6px;
  }

  div.content_section_text ul, div.content_section_text li {
    padding: 4px 8px 4px 16px;
  }

  div.section_header {
    padding: 3px 6px 3px 6px;

    background-color: #8E9CB2;

    color: #FFFFFF;
    font-weight: bold;
    font-size: 112%;
    text-align: center;
  }

  div.section_header_red {
    background-color: #CD214F;
  }

  div.section_header_grey {
    background-color: #9F9386;
  }

  .floating_element {
    position: relative;
    float: left;
  }

  div.table_of_contents_item a,
  div.content_section_text a {
    text-decoration: none;
    font-weight: bold;
  }

  div.table_of_contents_item a:link,
  div.table_of_contents_item a:visited,
  div.table_of_contents_item a:active {
    color: #000000;
  }

  div.table_of_contents_item a:hover {
    background-color: #000000;

    color: #FFFFFF;
  }

  div.content_section_text a:link,
  div.content_section_text a:visited,
   div.content_section_text a:active {
    background-color: #DCDFE6;

    color: #000000;
  }

  div.content_section_text a:hover {
    background-color: #000000;

    color: #DCDFE6;
  }

  div.validator {
  }
    </style>

  </head>
  <body>
    <div class="main_page">
          <br/>
          <p><a href="sparql"><?php print $storeName; ?> SPARQL Server</a></p>
          <br/>
          <a href="faq-en.html">Frequently Asked Questions</a> - <a href="faq-fr.html">Foire aux questions</a> - <a href="/downloads">Downloads</a> - <a href="mailto:canlink@gmail.com">Contact</a> - <a href="https://twitter.com/canlink2017">Twitter</a>
          <br/>
    </div>
    <div class="main_page">    
<?php
 $db = sparql_connect($storeURL );
 if (! $db->alive()) {
  print "<div style=\"display:inline;width:150px;color:#FF0000\">Offline</div>";
 } else {
//  $result = sparql_query("SELECT * WHERE {?void <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/TR/void/Dataset> . }");
$result = sparql_query("
SELECT ?graph ?uri ?name ?description ?status ?version ?prefix ?entities  WHERE { GRAPH ?graph {
?uri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Ontology> . 
   OPTIONAL {?uri <http://purl.org/dc/terms/description>  ?description . }
   OPTIONAL {?uri <http://www.w3.org/2002/07/owl#versionInfo> ?version .}
   OPTIONAL {?uri <http://xmlns.com/foaf/0.1/name> ?name . }
   OPTIONAL {?uri <http://rdfs.org/ns/void#inDataset> ?dataset .
             ?dataset <http://rdfs.org/ns/void#entities> ?entities . }
   OPTIONAL {?uri <http://www.w3.org/2003/06/sw-vocab-status/ns#term_status> ?status .}
   OPTIONAL {?uri <http://purl.org/vocab/vann/preferredNamespacePrefix> ?prefix . }
  filter (lang(?description) = 'en')
  filter (lang(?name) = 'en')
}  }");
?>
</div>
<div class="main_page"> The following ontologies are present on this server:</div>
<div class="main_page"> 
<table>
<thead><tr><th class="class">SPARQL Graph</th><th class="class">Name</th><th>Prefix</th><th>Description</th><th class="status">Version</th><th>Status</th><th>Size</th></tr></thead>
 <tbody>
<?php
while( $row = sparql_fetch_array( $result ) )
{
	print "<tr>";
        print "<td>" . $row["graph"] . "</td>"; 
        print "<td><a href=\"" . $row["uri"] . ".html\">";
         if (!empty($row["name"])) { 
          print $row["name"]; 
         } else { 
          print $row["prefix"]; 
         } 
        print   "</a></td>";
        print "<td><a href=\"" . $row["uri"] . ".owl\">" . $row["prefix"] . "</a></td>";
        print "<td>" . $row["description"] . "</td>";
        print "<td class=\"status\">" . $row["version"] . "</td>";
        print "<td class=\"status\">";
        if ($row["status"] == "Stable") {
         print "<div style=\"width:150px;color:#00FF00\">"  . $row["status"] . "</div>";
        } elseif ($row["status"] == "Unstable") {
         print "<div style=\"width:150px;color:#FF0000\">"  . $row["status"] . "</div>";
        } elseif ($row["status"] == "Testing") {
         print "<div style=\"width:150px;color:#FFFF99\">"  . $row["status"] . "</div>";
        } else {
         print "<div style=\"width:150px;color:#000000\">"  . $row["status"] . "</div>";        
        } 
        print "</td>";
        print "<td>" . number_format($row["entities"]) . "</td>";
	print "</tr>\n";
}

print " </tbody></table></div>";


print '    <div class="main_page"> ';   

$result = sparql_query("
SELECT ?graph ?uri ?name ?description ?status ?version ?prefix ?entities  WHERE { GRAPH ?graph {
?uri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://rdfs.org/ns/void#Dataset> . 
   OPTIONAL { ?auri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Ontology> .
              FILTER (?uri = ?auri) . }
   OPTIONAL {?uri <http://purl.org/dc/terms/description>  ?description . }
   OPTIONAL {?uri <http://www.w3.org/2002/07/owl#versionInfo> ?version .}
   OPTIONAL {?uri <http://xmlns.com/foaf/0.1/name> ?name . }
   OPTIONAL {?uri <http://rdfs.org/ns/void#inDataset> ?dataset .
             ?dataset <http://rdfs.org/ns/void#entities> ?entities . }
   OPTIONAL {?uri <http://www.w3.org/2003/06/sw-vocab-status/ns#term_status> ?status .}
   OPTIONAL {?uri <http://purl.org/vocab/vann/preferredNamespacePrefix> ?prefix . }
  filter (lang(?description) = 'en')
  filter (lang(?name) = 'en')
  FILTER ( !BOUND(?auri) ) 
}  }
");
?>
</div>
<div class="main_page"> The following datasets are present on this server:</div>
<div class="main_page"> 
<table>
<thead><tr><th class="class">SPARQL Graph</th><th class="class">Name</th><th>Prefix</th><th>Description</th><th class="status">Version</th><th>Status</th><th>Size</th></tr></thead>
 <tbody>
<?php
while( $row = sparql_fetch_array( $result ) )
{
	print "<tr>";
        print "<td>" . $row["graph"] . "</td>"; 
        print "<td><a href=\"" . $row["uri"] . ".html\">";
         if (!empty($row["name"])) { 
          print $row["name"]; 
         } else { 
          print $row["prefix"]; 
         } 
        print   "</a></td>";
        print "<td><a href=\"" . $row["uri"] . ".owl\">" . $row["prefix"] . "</a></td>";
        print "<td>" . $row["description"] . "</td>";
        if (strlen($row["version"])>1) {
         print "<td class=\"status\">" . $row["version"] . "</td>";
        } else {
         print "<td class=\"status\">-</td>";
        }
        print "<td class=\"status\">";
        if ($row["status"] == "Stable") {
         print "<div style=\"width:150px;color:#00FF00\">"  . $row["status"] . "</div>";
        } elseif ($row["status"] == "Unstable") {
         print "<div style=\"width:150px;color:#FF0000\">"  . $row["status"] . "</div>";
        } elseif ($row["status"] == "Testing") {
         print "<div style=\"width:150px;color:#FFFF99\">"  . $row["status"] . "</div>";
        } else if (strlen($row["status"])>1) {
         print "<div style=\"width:150px;color:#000000\">"  . $row["status"] . "</div>";        
        } else {
         print "<div style=\"width:150px;color:#000000\">-</div>";
        }
        print "</td>";
        print "<td>" . number_format($row["entities"]) . "</td>";
	print "</tr>\n";
}
?>
 </tbody></table>
 </div>
    <div class="main_page"> 
    <br/>
    <div class="ui-widget">
<form name="formsearch" id="frmSearch" action="search.php"  onsubmit="return OnSubmitForm();">
<?php
$result = sparql_query("
SELECT count(?thesis)  as ?myc WHERE {
?thesis <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://purl.org/ontology/bibo/thesis> . 
}");
$row = sparql_fetch_array( $result );
print "<p>Search any of the " . $row["myc"]  .   " thesis on this server using a name, title, subject or university:</p>";
?>
        <input type="text" id="txtSearch" name="txt" alt="Search Criteria" size="40"/>
        <input type="submit" id="cmdSearch" name="cmdSearch" value="Search" alt="Run Search" />
        </form>
</div>
<br/>
<br/>
<br/>
</div>

</body>
<?php
 }
?>
</html>