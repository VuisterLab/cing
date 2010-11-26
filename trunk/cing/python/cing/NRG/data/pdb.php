<?php

//echo $_SERVER['PATH_INFO'];
//exit();

list ($pdb_id, $foo) = explode("/", substr($_SERVER['PATH_INFO'],1));
//echo $pdb_id;
//exit();

$ch23 = substr($pdb_id, 1,2);
$newURL = "../data/{$ch23}/{$pdb_id}/{$pdb_id}.cing/{$pdb_id}/HTML/index.html";
header( "Location:$newURL" );
exit();

?>
