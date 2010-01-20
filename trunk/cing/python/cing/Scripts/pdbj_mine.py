#!/usr/bin/env python
'''
Created on Jan 13, 2010

@author: pdbj

Call like:

python $CINGROOT/python/cing/Scripts/pdbj_mine.py csv $CINGROOT/python/cing/NRG/sql/pdbx_nmr_software.sql
'''

# import modules
import sys
import urllib

# set proxy if you need
#proxy_dict = {'http': 'http://proxy.example.com:3128'}
proxy_dict = None


# You don't need to edit below.

# set parameters
base_url = 'http://service.pdbj.org/mine/sql'
output_format = sys.argv[1]
sql_query = open(sys.argv[2], 'r')
post_parameter = urllib.urlencode({'format':output_format, 'q':sql_query.read()})

# generate access query
result = urllib.urlopen(base_url, post_parameter, proxies=proxy_dict)

# show result
print result.read()