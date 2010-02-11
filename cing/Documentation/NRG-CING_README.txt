Sequence of events

- BMRB works on grunt to update NRG (Tue).

- BMRB manually sync to manatee after updates.

- BMRB cron sync to web site (daily) to: http://restraintsgrid.bmrb.wisc.edu

- BMRB (JFD) cron rsyncs every 8 hours the CCPN tgz to CMBI from grunt

- CMBI every day checks mysql rdb dump for updates

- CMBI every day runs <=20 new only entries and updates NRG-CING indices.