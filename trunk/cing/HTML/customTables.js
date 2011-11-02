// NB - watch out for extra comma's are a fault in JS according to IE8
//    - Customized jquery.dataTables.js for:
//	  - Added additional number of rows to paginate (5 and up to 10,000)
//    - Changed the wording of 'entries' to 'items'.
jQuery(document).ready(function() {

    TableTools.DEFAULTS.aButtons = [ "copy", "csv", "xls" ];
    
    TableTools.BUTTONS.download = {
            "sAction": "text",
            "sFieldBoundary": "",
            "sFieldSeperator": "\t",
            "sNewLine": "<br>",
            "sToolTip": "",
            "sButtonClass": "DTTT_button_text",
            "sButtonClassHover": "DTTT_button_text_hover",
            "sButtonText": "Download",
            "mColumns": "all",
            "iDisplayLength": "123456", // special value to indicate all in selected rows.
            "bHeader": true,
            "bFooter": true,
            "sDiv": "",
            "fnMouseover": null,
            "fnMouseout": null,
            "fnClick": function( nButton, oConfig ) {
              var oParams = this.s.dt.oApi._fnAjaxParameters( this.s.dt );
              var iframe = document.createElement('iframe');
              iframe.style.height = "0px";
              iframe.style.width = "0px";
              iframe.src = oConfig.sUrl+"?"+$.param(oParams);
              document.body.appendChild( iframe );
            },
            "fnSelect": null,
            "fnComplete": null,
            "fnInit": null
//            "fnServerParams": function ( aoData ) { // FAILS
//                aoData.push( { "name": "query_type3", "value": "download" } );
//            }            
        };
        
    var oTable = $("table[id^='dataTables-summaryArchive']").dataTable({
        "bSort": true,
        // Initially show the reverse natural order of PDB entries. High numbers in NRG-CING are more interesting.
        "aaSorting": [[2,'desc']],
        // Set the data types just in case the automatic detection fails (because of '.' values eg). Important for sorting.
        // mandatory to list each column if using this parameter!
        "aoColumns": [
                      { "sType": "html" }, 				    	// entry_id html
                      { "sType": "html" }, 				    	// image html
                      { "sType": "html", "sClass": "left" },    // pdb
                      { "sType": "html", "sClass": "right" },	// bmrb 
                      { "sType": "html", "sClass": "left" },	// rog_str                      
                      { "sType": "numeric", "sClass": "right" },// distance_count 
                      { "sType": "numeric", "sClass": "right" },// cs_count 
                      { "sType": "numeric", "sClass": "right" },// chothia_class 
                      { "sType": "numeric", "sClass": "right" },// chain_count 
                      { "sType": "numeric", "sClass": "right" } // res_count 
                  ],
        // Pagination options.
        "bPaginate": true,
        "sPaginationType": "full_numbers",
        "bLengthChange": true,
        "iDisplayLength": 5,
        "bFilter": true,
        "bProcessing": true,
        "bServerSide": true,
//        "bStateSave": true,
        "bAutoWidth": false, // recalculates the column widths on the fly but as this fails it's switched off.
        "sDom": 'iT<"clear"><lfr><"clear">tp',        
        "sAjaxSource": '../../cgi-bin//cingRdbServer/DataTablesServer.py',
        "oLanguage": {
            "sSearch": "Filter (e.g. beta):",
            "sProcessing":  "Please wait...",
                            "sLengthMenu": 'Show <select>'+
                                '<option value="5">5</option>'+
                                '<option value="10">10</option>'+
                                '<option value="25">25</option>'+
                                '<option value="100">100</option>'+
                                '<option value="1000">1000</option>'+
                                '<option value="10000">10000</option>'+
                            '</select> records'
//            "sInfo": "Showing _START_:_END_ of _TOTAL_",
//            "sInfoEmpty": "Showing 0 to 0 of 0 entries",
//            "sInfoFiltered": "(filtered from _MAX_ total)"                                
        },
        "fnServerParams": function ( aoData ) { // WORKS
            aoData.push( { "name": "query_type", "value": "normal" } );
        },                
        "oTableTools": {
            "sSwfPath": "./dataTableMedia/swf/copy_cvs_xls.swf",
            "aButtons": [ {
                "sExtends": "download",
                "sButtonText": "CSV",
                "sButtonClass": "DTTT_button_csv",
                "sButtonClassHover": "DTTT_button_csv_hover",
                "sUrl": "../../cgi-bin/cingRdbServer/DataTablesServer.py"            
            } ]
        }        
    } );
    
//    Add a select menu for some TH element (rog and chothia_class) in the table footer 
    /*
    $("tfoot th").each( function ( i ) {
        if (i != 1 && i != 4) {
            return;
        }
        $('select', this).change( function () {
            oTable.fnFilter( $(this).val(), i );
        } );
    } );
    */
    
    // Usage of the console object
//    console.log("Hello World! 2");
    /* td[class^='PDB'] */
//    $("#dataTables-summaryArchive td[class^='PDB']").each( function(nr, elem) {
//        console.log("Hello World! I'm in.");    	
//        var url = "http://www.bla.nl/" + $(elem).text().substring(1, 3) + "/" + $(elem).text() + ".gif";
//        var a = "<a href='" + url + "'>" + $(elem).text() + "</a>";
//        $(elem).html(a);
//    });
    
    $("table[id^='dataTables-atomList']").dataTable({
        "sDom": 'iT<"clear"><lfr><"clear">tp',
        "oTableTools": { "sSwfPath": "../dataTableMedia/swf/copy_cvs_xls.swf" },
        "oLanguage": {
            "sSearch": "Search (e.g. 13c leu):"
        },
        
        "bSort": true,
        // Initially show the natural order in molecule in order to show critiqued near by when coming in from other page.
        "aaSorting": [[0,'asc'], [1,'asc'], [3,'asc']],
        // Set the data types just in case the automatic detection fails (because of '.' values eg). Important for sorting.
        // mandatory to list each column if using this parameter!
        "aoColumns": [
                      { "sType": "html" }, 						// ch
                      { "sType": "numeric", "sClass": "right" },// resi
                      { "sType": "html" }, 						// resn
                      { "sType": "html" }, 						// atom name
                      { "sType": "html" }, 						// atom type
                      { "sClass": "center"}, 					// stereo (s) now

                      { "sType": "numeric", "sClass": "right"}, // obs
                      { "sType": "numeric", "sClass": "right"}, // error

                      { "sType": "numeric", "sClass": "right"}, // shiftx
                      { "sType": "numeric", "sClass": "right"}, // error
                      { "sType": "numeric", "sClass": "right"}, // delta

                      { "sType": "numeric", "sClass": "right"}, // dbase
                      { "sType": "numeric", "sClass": "right"}, // error
                      { "sType": "numeric", "sClass": "right"}, // delta

                      { "sType": "html", "sClass": "left" } // criteria is html too (list)
                  ],
        // Pagination options.
        "bPaginate": true,
        "bLengthChange": true,
        "iDisplayLength": 10000,
        "bFilter": true,
        "bProcessing": true,        
        "bAutoWidth": false // recalculates the column widths on the fly but as this fails it's switched off.
//        "bStateSave": true, // uses cookie! test first! Not really nicer..
    } );


//    $("table[id^='dataTables-DRSsaHeader']").dataTable({
//        "bSort": false,
//        "bPaginate": false,
//        "bLengthChange": false,
//        "bFilter": false,
//        "bInfo": false,
//        "bProcessing": false,
////        "sDom": 'T<"clear">lfrtip',
//        "aoColumns": [
//                      { "sType": "html",    "sClass": "left" }, // parameter
//                      { "sType": "numeric", "sClass": "left" }  // value
//                  ]
//    } );

    $("table[id^='dataTables-DRSsaMain']").dataTable({
        "bSort": true,
        "aaSorting": [[0,'asc']],
        "bPaginate": true,
        "bLengthChange": true,
        "iDisplayLength": 10,
        "bFilter": true,
        "bInfo": true,
        "bProcessing": true,
        "bAutoWidth": false,
        "sDom": 'i<"clear"><lfr><"clear">tp',
//        "oTableTools": { "sSwfPath": "../dataTableMedia/swf/copy_cvs_xls.swf" }, # Can't get this one working without showing it first?
        "oLanguage": {
            "sSearch": "Search (e.g. leu):"
        },
        "aoColumns": [
                      {"sType": "numeric", "sClass": "right" }, // 1 #
                      {"sType": "html" }, 						// 2 ch
                      {"sType": "numeric", "sClass": "right" }, // 3 resi
                      {"sType": "html" }, 						// 4 resn
                      {"sType": "html" },						// 5 atom name
                      {"sType": "numeric", "sClass": "right" }, // 6 Num
                      {"sType": "html"},  						// 7 Swapped
                      {"sType": "numeric", "sClass": "right"},  // 8 Models Favoring
                      {"sType": "numeric", "sClass": "right"},  // 9 Energy Diff.%
                      {"sType": "numeric", "sClass": "right"},  //10 Energy Diff.
                      {"sType": "numeric", "sClass": "right"},  //11 Energy +
                      {"sType": "numeric", "sClass": "right"},  //12 Energy -
                      {"sType": "numeric", "sClass": "right"},  //13 Constraint Count
                      {"sType": "numeric", "sClass": "right"},  //14 Constraint Ambi Count
                      {"sType": "html"},   						//15 Deassigned
                      {"sType": "numeric", "sClass": "right"},  //16 Violation Max
                      {"sType": "numeric", "sClass": "right"},  //17 Single Mdl Crit Count
                      {"sType": "numeric", "sClass": "right"}   //18 Multi Mdl Crit Count
                  ]
    } );

    $("table[id^='dataTables-DRList']").dataTable({
        "bSort": true,
        "aaSorting": [[0,'asc']],
        "bPaginate": true,
        "bLengthChange": true,
        "iDisplayLength": 10000,
        "bFilter": true,
        "bInfo": true,
        "bProcessing": true,
        "bAutoWidth": false,
        "sDom": 'iT<"clear"><lfr><"clear">tp',
        "oTableTools": { "sSwfPath": "../dataTableMedia/swf/copy_cvs_xls.swf" },
        "oLanguage": {
            "sSearch": "Search (e.g. viol):"
        },
        "aoColumns": [
                      { "sType": "numeric", "sClass": "right" }, // #
         // atom 1
                      { "sType": "html" }, 						// ch
                      { "sType": "numeric", "sClass": "right" },// resi
                      { "sType": "html" },                		// resn
                      { "sType": "html" }, 						// atom name
//       // atom 2
                      { "sType": "html" },
                      { "sType": "numeric", "sClass": "right" },
                      { "sType": "html" },
                      { "sType": "html" },
//                      // values.
                      {"sType": "numeric", "sClass": "right"},   //        lower.
//                    "sType": "numeric",  {"sClass": "right"},   //        target
                     {"sType": "numeric", "sClass": "right"},  //        upper
                     {"sType": "numeric", "sClass": "right"},   //        av
                     {"sType": "numeric", "sClass": "right"},   //        sd
                     {"sType": "numeric", "sClass": "right"},   //        min
                     {"sType": "numeric", "sClass": "right"},   //        max
                     {"sType": "numeric", "sClass": "right"},   //        vAv
                     {"sType": "numeric", "sClass": "right"},   //        vSd
                     {"sType": "numeric", "sClass": "right"},   //        vMax
                     {"sType": "numeric", "sClass": "right"},   //        c.1
                     {"sType": "numeric", "sClass": "right"},   //        c.3
                     {"sType": "numeric", "sClass": "right"},   //        c.5
//                     { "sType": "html", "sWidth":"100em", "sClass": "left" } // criteria is html too (list)
                     { "sType": "html", "sClass": "left" } // criteria is html too (list)
                  ]
    } );

    $("table[id^='dataTables-ACList']").dataTable({
        "bSort": true,
        "aaSorting": [[0,'asc']],
        "bPaginate": true,
        "bLengthChange": true,
        "iDisplayLength": 10000,
        "bFilter": true,
        "bInfo": true,
        "bProcessing": true,
        "bAutoWidth": false,
        "sDom": 'iT<"clear"><lfr><"clear">tp',
          "oTableTools": { "sSwfPath": "../dataTableMedia/swf/copy_cvs_xls.swf" },
          "oLanguage": {
              "sSearch": "Search (e.g. leu):"
          },
        
        "aoColumns": [
                      { "sType": "numeric", "sClass": "right" },// #
                      { "sType": "html" }, 						// ch
                      { "sType": "numeric", "sClass": "right" },// resi
                      { "sType": "html" }, 						// resn
                      { "sClass": "left"}, 					    // angle name
                      { "sType": "html" }, 						// atom name 1
                      { "sType": "html" }, 						// atom name 2 potentially different residue
                      { "sType": "html" }, 						// atom name 3
                      { "sType": "html" }, 						// atom name 4
                      {"sType": "numeric", "sClass": "right"},   //        lower.
//                    {"sClass": "right"},   //        target
                    {"sType": "numeric", "sClass": "right"},  //        upper
                    {"sType": "numeric", "sClass": "right"},   //        cav
                    {"sType": "numeric", "sClass": "right"},   //        cv
                    {"sType": "numeric", "sClass": "right"},   //        c3
                    {"sType": "numeric", "sClass": "right"},   //        vAv
                    {"sType": "numeric", "sClass": "right"},   //        vSd
                    {"sType": "numeric", "sClass": "right"},   //        vMax
//                    { "sType": "html", "sWidth":"100em", "sClass": "left" }
                    { "sType": "html", "sClass": "left" }
                  ]
    } );


    $("table[id^='dataTables-1dPeakList']").dataTable({
        "bSort": true,
        "aaSorting": [[0,'asc']],
        "bPaginate": true,
        "bLengthChange": true,
        "iDisplayLength": 10000,
        "bFilter": true,
        "bInfo": true,
        "bProcessing": true,
        "bAutoWidth": false,
        "sDom": 'i<"clear"><lfr><"clear">tp',
      "oTableTools": { "sSwfPath": "../dataTableMedia/swf/copy_cvs_xls.swf" },
      "oLanguage": {
          "sSearch": "Search (e.g. leu):"
      },
        "aoColumns": [
                      { "sType": "numeric", "sClass": "right" }, // #

                      {"sClass": "right", "sType": "numeric"},   //        pos1

                      {"sClass": "right", "sType": "numeric"},   //        height.
                      {"sClass": "right", "sType": "numeric"},   //        sd
                      {"sClass": "right", "sType": "numeric"},   //        volume.
                      {"sClass": "right", "sType": "numeric"},   //        sd

// atom 1
                      { "sType": "html" }, 						// ch
                      { "sType": "numeric", "sClass": "right" },// resi
                      { "sType": "html" },                		// resn
                      { "sType": "html" }, 						// atom name

                      { "sType": "html", "sClass": "left" } // criteria is html too (list)
                  ]
    } );
    $("table[id^='dataTables-2dPeakList']").dataTable({
        "bSort": true,
        "aaSorting": [[0,'asc']],
        "bPaginate": true,
        "bLengthChange": true,
        "iDisplayLength": 10000,
        "bFilter": true,
        "bInfo": true,
        "bProcessing": true,
        "bAutoWidth": false,
        "sDom": 'i<"clear"><lfr><"clear">tp',
        "oTableTools": { "sSwfPath": "../dataTableMedia/swf/copy_cvs_xls.swf" },
        "oLanguage": {
            "sSearch": "Search (e.g. leu):"
        },
        "aoColumns": [
                      { "sType": "numeric", "sClass": "right" }, // #

                      {"sClass": "right", "sType": "numeric"},   //        pos1
                      {"sClass": "right", "sType": "numeric"},   //        pos2

                      {"sClass": "right", "sType": "numeric"},   //        height.
                      {"sClass": "right", "sType": "numeric"},   //        sd
                      {"sClass": "right", "sType": "numeric"},   //        volume.
                      {"sClass": "right", "sType": "numeric"},   //        sd

// atom 1
                      { "sType": "html" }, 						// ch
                      { "sType": "numeric", "sClass": "right" },// resi
                      { "sType": "html" },                		// resn
                      { "sType": "html" }, 						// atom name
// atom 2
                      { "sType": "html" },
                      { "sType": "numeric", "sClass": "right" },
                      { "sType": "html" },
                      { "sType": "html" },

                      { "sType": "html", "sClass": "left" } // criteria is html too (list)
                  ]
    } );
    $("table[id^='dataTables-3dPeakList']").dataTable({
        "bSort": true,
        "aaSorting": [[0,'asc']],
        "bPaginate": true,
        "bLengthChange": true,
        "iDisplayLength": 10000,
        "bFilter": true,
        "bInfo": true,
        "bProcessing": true,
        "bAutoWidth": false,
        "sDom": 'i<"clear"><lfr><"clear">tp',
        "oTableTools": { "sSwfPath": "../dataTableMedia/swf/copy_cvs_xls.swf" },
        "oLanguage": {
            "sSearch": "Search (e.g. leu):"
        },
        "aoColumns": [
                      { "sType": "numeric", "sClass": "right" }, // #

                      {"sClass": "right", "sType": "numeric"},   //        pos1
                      {"sClass": "right", "sType": "numeric"},   //        pos2
                      {"sClass": "right", "sType": "numeric"},   //        pos3

                      {"sClass": "right", "sType": "numeric"},   //        height.
                      {"sClass": "right", "sType": "numeric"},   //        sd
                      {"sClass": "right", "sType": "numeric"},   //        volume.
                      {"sClass": "right", "sType": "numeric"},   //        sd

// atom 1
                      { "sType": "html" }, 						// ch
                      { "sType": "numeric", "sClass": "right" },// resi
                      { "sType": "html" },                		// resn
                      { "sType": "html" }, 						// atom name
// atom 2
                      { "sType": "html" },
                      { "sType": "numeric", "sClass": "right" },
                      { "sType": "html" },
                      { "sType": "html" },
// atom 3
                      { "sType": "html" },
                      { "sType": "numeric", "sClass": "right" },
                      { "sType": "html" },
                      { "sType": "html" },

                      { "sType": "html", "sClass": "left" } // criteria is html too (list)
                  ]
    } );
    $("table[id^='dataTables-4dPeakList']").dataTable({
        "bSort": true,
        "aaSorting": [[0,'asc']],
        "bPaginate": true,
        "bLengthChange": true,
        "iDisplayLength": 10000,
        "bFilter": true,
        "bInfo": true,
        "bProcessing": true,
        "bAutoWidth": false,
        "sDom": 'i<"clear"><lfr><"clear">tp',
        "oTableTools": { "sSwfPath": "../dataTableMedia/swf/copy_cvs_xls.swf" },
        "oLanguage": {
            "sSearch": "Search (e.g. leu):"
        },
        "aoColumns": [
                      { "sType": "numeric", "sClass": "right" }, // #

                      {"sClass": "right", "sType": "numeric"},   //        pos1
                      {"sClass": "right", "sType": "numeric"},   //        pos2
                      {"sClass": "right", "sType": "numeric"},   //        pos3
                      {"sClass": "right", "sType": "numeric"},   //        pos4

                      {"sClass": "right", "sType": "numeric"},   //        height.
                      {"sClass": "right", "sType": "numeric"},   //        sd
                      {"sClass": "right", "sType": "numeric"},   //        volume.
                      {"sClass": "right", "sType": "numeric"},   //        sd

// atom 1
                      { "sType": "html" }, 						// ch
                      { "sType": "numeric", "sClass": "right" },// resi
                      { "sType": "html" },                		// resn
                      { "sType": "html" }, 						// atom name
// atom 2
                      { "sType": "html" },
                      { "sType": "numeric", "sClass": "right" },
                      { "sType": "html" },
                      { "sType": "html" },
// atom 3
                      { "sType": "html" },
                      { "sType": "numeric", "sClass": "right" },
                      { "sType": "html" },
                      { "sType": "html" },
// atom 4
                      { "sType": "html" },
                      { "sType": "numeric", "sClass": "right" },
                      { "sType": "html" },
                      { "sType": "html" },


                      { "sType": "html", "sClass": "left" } // criteria is html too (list)
                  ]
    } );

    /* Residue tables need to have a smaller font size defined in cing.css */
    $("table[id^='dataTables-res']").addClass("smallerEm");

    $("table[id^='dataTables-resDRList']").dataTable({
        "bPaginate": true,
        "bLengthChange": true,
        "iDisplayLength": 5,
        "bInfo": true,
        "bProcessing": true,
        "bAutoWidth": false,
        "sDom": 'i<"clear"><lfr><"clear">tp',
//        "oTableTools": { "sSwfPath": "../../../dataTableMedia/swf/copy_cvs_xls.swf" },
        "oLanguage": {
            "sSearch": "Search (e.g. HA):"
        },
        "aaSorting": [[8,'desc'],[0,'asc']],
        "aoColumns": [
          { "sType": "html", "sClass": "right" }, // 0 #
          { "sType": "html", "sClass": "left" }, 	 // 1 at1
          { "sType": "html", "sClass": "left" }, 	 // 2 at2
          { "sType": "numeric", "sClass": "right"},   // 3       lower.
          { "sType": "numeric", "sClass": "right"},  //  4      upper
          { "sClass": "right"},   // 5       actual
          { "sClass": "right"},   // 6       violations
          { "sType": "numeric", "sClass": "right"},   // 7       max
          { "sType": "numeric", "sClass": "center"},   //8       >threshold
          { "sType": "html", "sClass": "left" } // criteria is html too (list)
      ]
    } );

    $("table[id^='dataTables-resACList']").dataTable({
        "bPaginate": true,
        "bLengthChange": true,
        "iDisplayLength": 5,
        "bInfo": true,
        "bProcessing": true,
        "bAutoWidth": false,
        "sDom": 'i<"clear"><lfr><"clear">tp',
        "aaSorting": [[9,'desc'],[0,'asc']],
        "aoColumns": [
/*          { "sType": "numeric", "sClass": "right", "bVisible": false, "sWidth": "30em"  }, */
          { "sType": "html", "sClass": "right" }, //0 # id
          {"sClass": "left" }, 	 //1 	name
          {"sType": "numeric", "sClass": "right"},   //2        lower.
          {"sType": "numeric", "sClass": "right"},   //3        upper
          {"sType": "numeric", "sClass": "right"},   //4        actual
          {"sType": "numeric", "sClass": "right"},   //5        cv
          {"sType": "numeric", "sClass": "right"},   //6        vAv
          {"sType": "numeric", "sClass": "right"},   //7        vSd
          {"sType": "numeric", "sClass": "right"},   //8        max
          {"sType": "numeric", "sClass": "center"},  //9        >threshold
          { "sType": "html", "sClass": "left" } //10 criteria is html too (list)
      ]
    } );

    $("#example").dataTable({
        "sDom": 'T<"clear">lfrtip'
    } );    
});