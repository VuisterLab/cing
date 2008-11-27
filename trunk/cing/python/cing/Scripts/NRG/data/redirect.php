<?php

#$url_base = 'http://www.bmrb.wisc.edu/servlet_data/molgrap';	
$url_base = 'URL_BASE';	
#echo "url base: $url_base\n";


function GetBMRBPage( $bmrbID ) {
    global $url_base;
	$indexNum = -1;
    $url_full = $url_base . '/index/index_bmrb.csv';
	$file_handle = fopen(  $url_full, 'r' );
	
	while( $fileString = fgets( $file_handle, 32 ) ) {
		$data = explode( ',', $fileString );

		if( $bmrbID  == $data[1] || $bmrbID  == $data[2] || 
		   ($bmrbID - $data[1] < 0 && $bmrbID - $data[2]> 0) ) {
			$indexNum = $data[0];
			break;
		}
	}
	fclose( $file_handle );
	
	return $indexNum;
}
	
#################
# GetPDBPage
#################
function GetPDBPage( $pdbID ) {
    global $url_base;
	$indexNum = '-1';
	$pdbID = strtoupper( $pdbID );
	
    $url_full = $url_base . '/index/index_pdb.csv';
	$file_handle = fopen(  $url_full, 'r' );
	while( $fileString = fgets( $file_handle, 32 ) ) {
		$data = explode( ',', $fileString );
		$cmp1 = strncmp( $pdbID, $data[1], 4 );
		$cmp2 = strncmp( $pdbID, $data[2], 4 );
		if( $cmp1 == 0 ||  $cmp2 == 0 || ( $cmp1 > 0 && $cmp2 < 0 ) ) {
			$indexNum = $data[0];
			break;
		}
	}
	fclose( $file_handle );
	
	return $indexNum;
}


##### begin ####	
$inputStr = $_SERVER['QUERY_STRING'];
$variables = array();
parse_str( $inputStr, $variables );
$newURL = 'sorry.html';


if( $variables['database'] == 'bmrb' ) {
    $indexNum = GetBMRBPage( $variables['id'] );
    $newURL = $url_base . "/index/index_bmrb_{$indexNum}";
} elseif( $variables['database'] == 'pdb' ) {
    $indexNum = GetPDBPage( $variables['id'] );
    $newURL = $url_base . "/index/index_pdb_{$indexNum}";
}
if( $indexNum > 0 ) {
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
