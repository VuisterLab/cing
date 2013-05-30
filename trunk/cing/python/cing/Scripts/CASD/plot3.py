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
    bp = ax1.boxplot([rmsd,rmsdToTarget], notch=False, sym='+', vert=True, whis=1.5)
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
        values.append( rmsdToTarget )
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

def plotAll():
    global show
    show = False
    
    plotStatsTargets()
    plotStatsGroups()
    plotStatsMethods()
    plotRmsdBoxAll()
    
    for t in results.targets:
        print t    
        plotRmsd(target)
        plotRmsdBox(target)
        plotROG(target)
        plotProcheck(target)
        plotQuality(target)
    #end for
    show = True
#end def




