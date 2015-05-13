import urllib2
# For http://www.rcsb.org/pdb/software/static.do?p=/software/webservices/search_nmr.jsp

url = 'http://www.rcsb.org/pdb/rest/search'
queryText = """
<?xml version="1.0" encoding="UTF-8"?>
<orgPdbQuery>
<version>B0907</version>
<queryType>org.pdb.query.simple.ExpTypeQuery</queryType>
<description>Experimental Method Search : Experimental Method=SOLID-STATE NMR</description>
<mvStructure.expMethod.value>SOLID-STATE NMR</mvStructure.expMethod.value>
</orgPdbQuery>
"""


print "query:\n", queryText
print "querying PDB...\n"

req = urllib2.Request(url, data=queryText)
f = urllib2.urlopen(req)
result = f.read()


if result:
    print "Found number of PDB entries:", result.count('\n')
else:
    print "Failed to retrieve results"