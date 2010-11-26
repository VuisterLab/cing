<?php
list ($id, $foo) = explode("/", substr($_SERVER['PATH_INFO'],1));
?>

<?php

$inputStr = $_SERVER['QUERY_STRING'];
$variables = array();
parse_str( $inputStr, $variables );
$sorryURL = 'sorry.html';
$newURL = $sorryURL;

if( $variables['database'] == 'pdb' ) { # BMRB id would be another option
    $pdb_id = $variables['id'];
    $ch23 = substr($pdb_id, 1,2);
    $newURL = "./data/{$ch23}/{$pdb_id}/{$pdb_id}.cing/{$pdb_id}/HTML/index.html";
}

if( $newURL != $sorryURL ) {
    header( "Location:$newURL" );
    exit();
}

?>

<HTML> <HEAD> <TITLE>Apology</TITLE> </HEAD> <BODY>
  <?php
    echo "<P>Either the parameters: '<B>$inputStr</B>' do not contain enough information or
    the id was out of bounds</P>";
  ?>
</BODY> </HTML>