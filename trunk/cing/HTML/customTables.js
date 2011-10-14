// NB - watch out for extra comma's are a fault in JS according to IE8
//    - Customized jquery.dataTables.js for:
//	  - Added additional number of rows to paginate (5 and up to 10,000)
//    - Changed the wording of 'entries' to 'items'.
jQuery(document).ready(function() {
    // Safe variable for below JS.
    var oTable = $("table[id^='dataTables-summaryArchive']").dataTable({
        "bSort": true,
        // Initially show the reverse natural order of PDB entries. High numbers in NRG-CING are more interesting.
        "aaSorting": [[0,'desc']],
        // Set the data types just in case the automatic detection fails (because of '.' values eg). Important for sorting.
        // mandatory to list each column if using this parameter!
        "aoColumns": [
                      { "sType": "html" }, 				        // image html
                      { "sType": "html" }, 				        // pdb html
                      { "sType": "numeric", "sClass": "right" },// bmrb 
                      { "sType": "numeric", "sClass": "right" },// rog 
                      { "sType": "numeric", "sClass": "right" },// distance_count 
                      { "sType": "numeric", "sClass": "right" },// cs_count 
                      { "sType": "numeric", "sClass": "right" },// chothia_class 
                      { "sType": "numeric", "sClass": "right" },// chain_count 
                      { "sType": "numeric", "sClass": "right" } // res_count 
                  ],
        // Pagination options.
        "bPaginate": true,
        "bLengthChange": true,
        "iDisplayLength": 10,
        "bFilter": true,
        "bProcessing": true,
        "bAutoWidth": false, // recalculates the column widths on the fly but as this fails it's switched off.
        "sDom": 'lfrtip',
//        "sSwfPath": "",       
//      "sSwfPath": "dataTableMedia/swf/ZeroClipboard.swf",       
//        "sSwfPath": "dataTableMedia/swf/copy_cvs_xls_pdf.swf"},
        "sAjaxSource": 'entry_list_summary.json'
    } );            
//    Add a select menu for some TH element (rog and chothia_class) in the table footer 
    $("tfoot th").each( function ( i ) {
        if (i != 3 && i != 6) {
            return;
        }
        $('select', this).change( function () {
            oTable.fnFilter( $(this).val(), i );
        } );
    } );
    
    $("table[id^='dataTables-atomList']").dataTable({
        "sDom": 'T<"clear">lfrtip',
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
        "bAutoWidth": false, // recalculates the column widths on the fly but as this fails it's switched off.
        "sDom": 'T<"clear">lfrtip'
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
        "sDom": 'T<"clear">lfrtip',
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
        "sDom": 'T<"clear">lfrtip',
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
        "sDom": 'T<"clear">lfrtip',
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
        "sDom": 'T<"clear">lfrtip',
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
        "sDom": 'T<"clear">lfrtip',
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
        "sDom": 'T<"clear">lfrtip',
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
        "sDom": 'T<"clear">lfrtip',
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
        "iDisplayLength": 10,
        "bInfo": true,
        "bProcessing": true,
        "bAutoWidth": false,
        "sDom": 'T<"clear">lfrtip',
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
        "iDisplayLength": 10,
        "bInfo": true,
        "bProcessing": true,
        "bAutoWidth": false,
        "sDom": 'T<"clear">lfrtip',
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