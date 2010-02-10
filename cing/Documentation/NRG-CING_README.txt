Sequence of events:


- BMRB updates NRG on one machine
- BMRB syncs daily to: http://restraintsgrid.bmrb.wisc.edu
- BMRB dumps mysql rdb on Thu 00:00 to http://restraintsgrid.bmrb.wisc.edu/servlet_data/viavia/mr_mysql_backup/
- BMRB rsyncs every 8 hours the CCPN tgz to CMBI

- CMBI every day checks mysql rdb dump for updates
- CMBI every day runs <=20 new only entries and updates NRG-CING indices.

