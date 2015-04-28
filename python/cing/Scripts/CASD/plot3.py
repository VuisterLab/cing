#Code to go with casd3.py fro making the plots
#
#

from matplotlib.backends.backend_pdf import PdfPages

show = True

def doShow(fig, label):
    plt.tight_layout()
    plt.legend(loc='best')
    fn = analysisPath / label +'.pdf'
    pp = PdfPages(str(fn))
    pp.savefig( fig )
    pp.close()
    if show:
        plt.show()
#end def

def plotMethods(title, ylabel):
    #convienience method to initiate plot
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    
    plt.title(title)

    xtickNames = plt.setp(ax1, xticklabels=results.methods)
    plt.setp(xtickNames, rotation=90, fontsize=12)
    ax1.xaxis.set_ticks(range(1,len(results.methods)+1))
    plt.xlim(0.1, len(results.methods)+1)
    #ax1.xaxis.set_label_text('methods', fontsize=14)

    ax1.yaxis.set_label_text(ylabel, fontsize=14)
    ax1.grid(True)

    return fig, ax1
#end def

def plotMethodsAdd( ax1, target, par, color):
    x,values=results.getValues(target, par)
    tmp = ax1.plot(x,values)
    plt.setp(tmp, color=color, label=par, marker='s', markersize=8)
    return x,values
#end def

def plotRmsd(target):
    fig,ax1 = plotMethods(target,'pairwise bb rmsd')
    
    plotMethodsAdd(ax1, target, 'rmsd', 'blue')
    x,values = plotMethodsAdd(ax1, target, 'rmsdToTarget', 'red')
    
    plt.ylim(0.0,max(values)+0.2)
    doShow(fig,target + '_rmsd')
#end def

def plotRmsdBox(target):
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    
    x,rmsd=results.getValues(target, 'rmsd')    
    x2,rmsdToTarget=results.getValues(target, 'rmsdToTarget')
    bp = ax1.boxplot([rmsd,rmsdToTarget[1:]], notch=False, sym='+', vert=True, whis=1.5) # skip the original in rmsdToTarget as this has 0.0 by definition
    plt.setp(bp['boxes'], color='black', lw=2)
    plt.setp(bp['whiskers'], color='black', lw=2)
    plt.setp(bp['caps'], color='black', lw=2)
    plt.setp(bp['medians'], color='blue', lw=2)
    plt.setp(bp['fliers'], color='red', marker='D', lw=2,  markersize=8)
    
    plt.title(target)
    xtickNames = plt.setp(ax1, xticklabels=['ensemble','toTarget'])
    plt.ylabel('pairwise bb rmsd', fontsize=14)
    ax1.axis([0.5,2.5,0,max(rmsdToTarget)+0.2])
    ax1.grid(True)
    doShow(fig,target + '_rmsdBox')
#end def

def plotRmsdBoxAll():
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    
    values = []
    for target in results.targets:        
        x,rmsdToTarget=results.getValues(target, 'rmsdToTarget')
        values.append( rmsdToTarget[1:] ) # skip the original Targets as these al have 0.0
    bp = ax1.boxplot(values, notch=False, sym='+', vert=True, whis=1.5)
    plt.setp(bp['boxes'], color='black', lw=2)
    plt.setp(bp['whiskers'], color='black', lw=2)
    plt.setp(bp['caps'], color='black', lw=2)
    plt.setp(bp['medians'], color='blue', lw=2)
    plt.setp(bp['fliers'], color='red', marker='D', lw=2,  markersize=8)
    
    plt.title('RMSDs to Target')
    xtickNames = plt.setp(ax1, xticklabels=results.targets)
    plt.setp(xtickNames, rotation=90, fontsize=12)
    plt.ylabel('pairwise bb rmsd', fontsize=14)
    ax1.grid(True)
    doShow(fig,'rmsdBoxAll')
#end def

def plotROG(target):
    fig,ax1 = plotMethods(target,'ROG (%)')
    
    plotMethodsAdd(ax1, target, 'cing_red', 'red')
    plotMethodsAdd(ax1, target, 'cing_orange', 'orange')
    plotMethodsAdd(ax1, target, 'cing_green', 'green')
    
    plt.ylim(0,100)
    
    doShow(fig,target + '_ROG')
#end def

def plotProcheck(target):
    fig,ax1 = plotMethods(target,'Procheck (%)')
    
    plotMethodsAdd(ax1, target, 'pc_disallowed', 'red')
    plotMethodsAdd(ax1, target, 'pc_generous', 'orange')
    plotMethodsAdd(ax1, target, 'pc_allowed', 'blue')
    plotMethodsAdd(ax1, target, 'pc_core', 'green')
    
    plt.ylim(0,100)
    
    doShow(fig,target + '_Procheck')
#end def

def plotQuality(target):
    fig,ax1 = plotMethods(target,'Quality scores')
    
    plotMethodsAdd(ax1, target, 'WI_ramachandran', 'blue')
    plotMethodsAdd(ax1, target, 'WI_bbNormality', 'green')
    plotMethodsAdd(ax1, target, 'WI_janin', 'violet')
    plotMethodsAdd(ax1, target, 'pc_gf', 'red')
    
    #plt.ylim(0.0,max(values)+0.2)
    doShow(fig,target + '_quality')
#end def

def plotStatsTargets():
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    
    plt.title('Submissons per target')

    xtickNames = plt.setp(ax1, xticklabels=results.targets)
    plt.setp(xtickNames, rotation=90, fontsize=12)
    ax1.xaxis.set_ticks(range(1,len(results.targets)+1))
    plt.xlim(0.1, len(results.targets)+1)
    #ax1.xaxis.set_label_text('methods', fontsize=14)

    ax1.yaxis.set_label_text('count', fontsize=14)
    ax1.grid(True)
    
    l = len(results.targets)
    x = np.zeros(l)
    v = np.zeros(l)
    for i,t in enumerate(results.targets):
        x[i] = float(i) + 1
        v[i] = float(len(results.byTarget[t]))
    tmp = ax1.plot(x,v)
    plt.setp(tmp, color='black', label='targets', marker='s', markersize=8)
    
    doShow(fig, 'stats_' + 'targets')
#end def

def plotStatsGroups():
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    
    plt.title('Submissions per group')

    xtickNames = plt.setp(ax1, xticklabels=results.groups)
    plt.setp(xtickNames, rotation=90, fontsize=12)
    ax1.xaxis.set_ticks(range(1,len(results.groups)+1))
    plt.xlim(0.1, len(results.groups)+1)
    #ax1.xaxis.set_label_text('methods', fontsize=14)

    ax1.yaxis.set_label_text('count', fontsize=14)
    ax1.grid(True)
    
    l = len(results.groups)
    x = np.zeros(l)
    v = np.zeros(l)
    for i,t in enumerate(results.groups):
        x[i] = float(i) + 1
        v[i] = float(len(results.byGroup[t]))
    tmp = ax1.plot(x,v)
    plt.setp(tmp, color='black', label='groups', marker='s', markersize=8)
    
    doShow(fig, 'stats_' + 'groups')
#end def

def plotStatsMethods():
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    
    plt.title('Submissions per method')

    xtickNames = plt.setp(ax1, xticklabels=results.methods)
    plt.setp(xtickNames, rotation=90, fontsize=12)
    ax1.xaxis.set_ticks(range(1,len(results.methods)+1))
    plt.xlim(0.1, len(results.methods)+1)
    #ax1.xaxis.set_label_text('methods', fontsize=14)

    ax1.yaxis.set_label_text('count', fontsize=14)
    ax1.grid(True)
    
    l = len(results.methods)
    x = np.zeros(l)
    v = np.zeros(l)
    for i,t in enumerate(results.methods):
        x[i] = float(i) + 1
        v[i] = float(len(results.byMethod[t]))
    tmp = ax1.plot(x,v)
    plt.setp(tmp, color='black', label='methods', marker='s', markersize=8)
    
    doShow(fig, 'stats_' + 'methods')
#end def

def plotByMethodBox(par, title, ylabel):
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    
    _tmp = NTvalue(0.0, 0.0)
    
    values = []
    for method in results.methods:
        l = len(results.byMethod[method])
        v = np.zeros(l)
        for i,e in enumerate(results.byMethod[method]):
            #print par, type(e[par]), type(_tmp)
            if par in e:
                if type(e[par]) == type(_tmp):
                    v[i] = float(e[par].value)
                else:
                    v[i] = float(e[par])
            #end if
        #end for
        values.append( v )
    #end for
        
    bp = ax1.boxplot(values, notch=False, sym='+', vert=True, whis=1.5)
    plt.setp(bp['boxes'], color='black', lw=2)
    plt.setp(bp['whiskers'], color='black', lw=2)
    plt.setp(bp['caps'], color='black', lw=2)
    plt.setp(bp['medians'], color='blue', lw=2)
    plt.setp(bp['fliers'], color='red', marker='D', lw=2,  markersize=8)
    
    plt.title(title)
    xtickNames = plt.setp(ax1, xticklabels=results.methods)
    plt.setp(xtickNames, rotation=90, fontsize=12)
    plt.ylabel(ylabel, fontsize=14)
    ax1.grid(True)
    doShow(fig,'byMethodsBox_'+par)
#end def

def plotQualVrsRmsdWI(allEntries=True):
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    
    _tmp = NTvalue(0.0, 0.0)
    
    l = len(results)
    rmsd = np.zeros(l)
    if allEntries:
        entries = results[10:]
    else:
        entries = []
        for method in ['CYANA', 'UNIO', 'ARIA', 'ASDP-CNS', 'Ponderosa']:
            for e in results.byMethod[method]:
                entries.append(e)
    #end if
    for par,color in [('WI_ramachandran','red'),('WI_janin','blue')]:
        values = np.zeros(l)
        for i,e in enumerate(entries):
            #print i,e
            rmsd[i] = float(e.rmsdToTarget.value)
            values[i] = float(e[par].value)
        #end for
        tmp=ax1.plot(rmsd,values)
        plt.setp(tmp, color=color, label=par, ls=' ', marker='s', markersize=8)        
    #end for
    plt.xlabel('rmsd to target', fontsize=14)
    plt.ylabel('Z-score', fontsize=14)
    ax1.grid(True)
    doShow(fig,'qualVrsRmsd_WI_'+ str(allEntries) )
#end def    

def plotQualVrsRmsdCING(allEntries=True):
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    
    _tmp = NTvalue(0.0, 0.0)
    
    l = len(results)
    rmsd = np.zeros(l)
    if allEntries:
        entries = results[10:]
    else:
        entries = []
        for method in ['CYANA', 'UNIO', 'ARIA', 'ASDP-CNS', 'Ponderosa']:
            for e in results.byMethod[method]:
                entries.append(e)
    #end if
    for par,color in [('cing_red','red'),('cing_green','green')]:
        values = np.zeros(l)
        for i,e in enumerate(entries):
            #print i,e
            rmsd[i] = float(e.rmsdToTarget.value)
            values[i] = float(e[par])
        #end for
        tmp=ax1.plot(rmsd,values)
        plt.setp(tmp, color=color, label=par, ls=' ', marker='s', markersize=8)        
    #end for
    plt.xlabel('rmsd to target', fontsize=14)
    plt.ylabel('fraction (%)', fontsize=14)
    ax1.grid(True)
    doShow(fig,'qualVrsRmsd_CING_'+str(allEntries))
#end def

def plotQualVrsRmsdCINGdiff():
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    
    _tmp = NTvalue(0.0, 0.0)
    
    l = len(results)
    rmsd = np.zeros(l)
    values = np.zeros(l)
    for i,e in enumerate(results[10:]):
            #print i,e
        rmsd[i] = float(e.rmsdToTarget.value)
        values[i] = float(e['cing_green']-e['cing_red'])
    #end for
    tmp=ax1.plot(rmsd,values)
    plt.setp(tmp, color='violet', label='diff', ls=' ', marker='s', markersize=8)        
    #end for
    plt.ylabel('green-red (%)', fontsize=14)
    ax1.grid(True)
    doShow(fig,'qualVrsRmsd_CINGdiff')
#end def

def plotAll():
    global show
    show = False
    
    plotStatsTargets()
    plotStatsGroups()
    plotStatsMethods()
    plotRmsdBoxAll()
    plotByMethodBox(rmsdToTarget, 'RMSDs to target')
    plotMatches()
    plotByMethodBox('WI_ramachandran','WhatIf Ramachandran Z-score', 'Z-score')
    plotByMethodBox('WI_janin','WhatIf Janin Z-score', 'Z-sore')
    plotByMethodBox('cing_red', 'CING red', 'fraction (%)')
    plotByMethodBox('cing_green', 'CING green','fraction (%)')

    
    for target in results.targets:
        print target    
        plotRmsd(target)
        plotRmsdBox(target)
        plotROG(target)
        plotProcheck(target)
        plotQuality(target)
    #end for
    show = True
#end def

def findMatches():
    # find refined/unrefined matches
    matches = []
    for group in results.groups:
        for e1 in results.byGroup[group]:
            for e2 in results.byGroup[group]:
                if (e1 != e2 and
                    e1.group == e2.group and
                    e1.target == e2.target and
                    e1.RDCdata == e2.RDCdata and
                    e1.truncated == e2.truncated and
                    #((e1.peaklist == 'Refined' and e2.peaklist=='Unrefined') or
                    # (e1.peaklist == 'Unrefined' and e2.peaklist=='Refined')
                    #) 
                    (e1.peaklist == 'Refined' and e2.peaklist=='Unrefined') # only take one of the two combinations
                    ):
                    matches.append((e1,e2))
                    #print 'match'
                #end if
            #end for
        #end for
    return matches
#end def

def plotMatches():
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    plt.title('Refined vrs Unrefined peak lists')
    
    m = findMatches()
    l = len(m)
    refined = np.zeros(l)
    refined_errs = np.zeros(l)
    unrefined = np.zeros(l)
    unrefined_errs = np.zeros(l)
    for i,e in enumerate(m):
        refined[i] = e[0].rmsdToTarget.value
        refined_errs[i] = e[0].rmsdToTarget.error
        unrefined[i] = e[1].rmsdToTarget.value
        unrefined_errs[i] = e[1].rmsdToTarget.error
    #end for
    
    plotline, caplines, barlinecols = ax1.errorbar(refined, unrefined, xerr=refined_errs, yerr=unrefined_errs, color='black', lw=2)    
    plt.setp(plotline, color='black', ls=' ')    
#    plt.setp(caplines, color='black', label='rmsd to target')    
#    tmp = ax1.errorbar(refined, unrefined, xerr=refined_errs)    
#    plt.setp(tmp, color='black', label='rmsd to target', ls=' ', marker='s', markersize=8)
    xmax = max(refined)+1.0
    plt.xlim(0, xmax)
    plt.ylim(0, max(unrefined)+1.0)
    
    x=np.arange(0,xmax,0.01)
    y=x
    tmp = ax1.plot(x,y)
    plt.setp(tmp, color='blue', lw=1)    
   
    ax1.grid(True)
    plt.ylabel('rmsd unrefined', fontsize=14)
    plt.xlabel('rmsd refined', fontsize=14)
    doShow(fig,'rmsd_refined_unrefined')
#end def

def mkHtml():
    html = """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
<title>CASD-NMR 2013</title>
<link media="screen" href="cing.css" type="text/css" rel="stylesheet"/>
</head>
<body>
<div id="container">
	<div id="header">
		<h1>Cing reports</h1>
	<!-- end header -->	</div>
%s
<div id="footer">
	<p>Validation reports for CASD-NMR using CING (<a href="http://code.google.com/p/cing/source/detail?r=1240">r1240</a>)	</p>
<!-- end footer --></div>
</body>
</html>
"""
    b = '<h1>Cing reports</h1>\n'
    for target in results.targets:
        b = b + '<h2>%s</h2>\n <ul>' % target
        for entry in results.byTarget[target]:
            path = entry.path(entry.entryName, 'HTML', 'index.html')
            b = b + '<li><a href="%s">%s</a></li>\n' % (path, entry.entryName)
        #end for
        b = b + '</ul>'
    #end for
    code = html % b
    
    f = open( dataPath / 'index.html', 'w')
    f.write( code )
    f.close()
#end def




