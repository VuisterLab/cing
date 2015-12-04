from __future__ import unicode_literals, print_function, absolute_import, division

from collections import OrderedDict
import csv
import time
import subprocess
import os

from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponse
from django.views.generic.base import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

import psycopg2 as pg


nrg_file_location = 'http://143.210.185.204/NRG-CING/data'

nrg_settings = settings.DATABASES['nrg']
CONN_STRING = "host='{HOST}' dbname={NAME} user={USER} password={PASSWORD}".format(**nrg_settings)
_COLUMNS = 'is_solid name pdb_id bmrb_id rog_str distance_count cs_count chothia_class_str chain_count res_count'.split()
_sTable = "nrgcing.cingentry"

@csrf_exempt
def fakeDataTableServer(request):

    if ('database' in request.GET):
        name = request.GET['id']
        return redirect('{0}/{1}/{2}/{2}.cing'.format(nrg_file_location, name[1:3], name))

    else:
        conn = pg.connect(CONN_STRING)
        cur = conn.cursor()

        resp = OrderedDict()
        resp['sEcho'] = request.GET['sEcho']

        cur.execute('SELECT COUNT(*) from {}'.format(_sTable))
        resp['iTotalRecords'] = cur.fetchone()[0]

        likeString = request.GET['sSearch'] + '%'
        likeString = likeString[:4]
        matchCountQuery = "SELECT COUNT(*) FROM {} WHERE pdb_id LIKE '{}'".format(_sTable, likeString)
        cur.execute(matchCountQuery)
        resp['iTotalDisplayRecords'] = cur.fetchone()[0]

        resultsQuery = "SELECT {} FROM {} WHERE pdb_id LIKE '{}'".format(', '.join(_COLUMNS),
                                                                        _sTable, likeString)

        if (request.GET['iSortCol_0'] != "") and (request.GET['iSortingCols'] > 0):
            resultsQuery += ' ORDER BY '
            for i in range(int(request.GET['iSortingCols'])):
                resultsQuery += _COLUMNS[int(request.GET['iSortCol_{}'.format(i)])]
                resultsQuery += ' '
                resultsQuery += request.GET['sSortDir_{}'.format(i)]
                resultsQuery += ' '

        if request.GET['iDisplayLength'] != -1:
            resultsQuery += "LIMIT {} OFFSET {}".format(request.GET['iDisplayLength'],
                                                        request.GET['iDisplayStart'])
        cur.execute(resultsQuery)
        resultData = cur.fetchall()

        if ('query_type' in request.GET) and (request.GET['query_type'] == 'normal'):
            resp['aaData'] = []
            for result in resultData:
                formattedResult = []
                name = result[1]
                pdb = result[2]
                bmrb = result[3]
                formattedResult.append("<a href='{0}/{1}/{2}/{2}.cing.tgz'><img src='/static/nrg/dataTableMedia/images/icon_download.gif' width=34 height=34 border=0></a>".format(nrg_file_location, name[1:3], name))
                formattedResult.append("<a href='{0}/{1}/{2}/{2}.cing'><img src='{0}/{1}/{2}/{2}.cing/{2}/HTML/mol_pin.gif' width=57 height=40 border=0></a>".format(nrg_file_location, name[1:3], name))
                formattedResult.append("<a href='http://www.rcsb.org/pdb/explore/explore.do?structureId={}'>{}</a>".format(name, pdb))

                if result[3] is not None:
                    formattedResult.append("<a href='http://www.bmrb.wisc.edu/data_library/generate_summary.php?bmrbId={0}'>{0}</a>".format(bmrb))
                else:
                    formattedResult.append('')

                if result[4] == 'red':
                    formattedResult.append("""<font color=#FF0000>red</font>""")
                elif result[4] == 'orange':
                    formattedResult.append("""<font color=#FFA500>orange</font>""")
                elif result[4] == 'green':
                    formattedResult.append("""<font color=#000000>green</font>""")
                else:
                    formattedResult.append("unknown")

                formattedResult += result[5:10]

                resp['aaData'].append(formattedResult)


            return JsonResponse(resp)
        else:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="NRG-CING_summary_selection.csv"'
            writer = csv.writer(response)

            writer.writerow(('pdb_id', 'bmrb_id', 'rog_str', 'distance_count', 'cs_count',
                             'chothia_class_str', 'chain_count', 'res_count'))

            for result in resultData:
                writer.writerow(result[2:10])

            return response


class RevisionedTemplateView(TemplateView):

    def cing_version(self):
        version = subprocess.check_output(["git", "describe"], cwd=os.environ['CINGROOT']),
        return version[0][:-1]

    def cing_update(self):
        return time.ctime(os.path.getmtime(os.path.join(os.environ['CINGROOT'],'.git', 'FETCH_HEAD')))

