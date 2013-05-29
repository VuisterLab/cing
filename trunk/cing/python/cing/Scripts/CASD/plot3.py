def plotRmsd(target):
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    
    x,rmsd=results.getValues(target, 'rmsd')
    rmsds = ax1.plot(x,rmsd)
    plt.setp(rmsds, color='blue', label='blue', marker='s', markersize=8)
    
    x2,rmsdToTarget=results.getValues(target, 'rmsdToTarget')
    rmsdToTargets = ax1.plot(x2,rmsdToTarget)
    plt.setp(rmsdToTargets, color='red', label='red', marker='s', markersize=8)
    
    #plt.title(target)
    #plt.xlabel('group id', fontsize=14)
    #plt.ylabel('pairwise bb rmsd', fontsize=14)
    #plt.axis([0,13,0,max(rmsdToTarget)+0.2])
    #plt.grid(True)
    #plt.show()
    
    xtickNames = plt.setp(ax1, xticklabels=results.groups)
    plt.setp(xtickNames, rotation=45, fontsize=12)
    ax1.xaxis.set_ticks(range(1,13))
    ax1.xaxis.set_label_text('groups', fontsize=14)
    ax1.yaxis.set_label_text('pairwise bb rmsd', fontsize=14)
    ax1.axis([0.1,13,0,max(rmsdToTarget)+0.2])
    ax1.grid(True)
    plt.tight_layout()
    plt.show()
#end def

def plotRmsdBox(target):
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    x,rmsd=results.getValues(target, 'rmsd')    
    x2,rmsdToTarget=results.getValues(target, 'rmsdToTarget')
    bp = ax1.boxplot([rmsd,rmsdToTarget], notch=0, sym='+', vert=1, whis=2.5)
    plt.setp(bp['boxes'], color='black', lw=2)
    plt.setp(bp['whiskers'], color='black', lw=2)
    plt.setp(bp['fliers'], color='red', marker='+', lw=2,  markersize=8)
    
    plt.title(target)
    xtickNames = plt.setp(ax1, xticklabels=['ensemble','toTarget'])
    plt.ylabel('pairwise bb rmsd', fontsize=14)
    ax1.axis([0.5,2.5,0,max(rmsdToTarget)+0.2])
    ax1.grid(True)
    plt.show()
#end def

def plotROG(target):
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    
    x,red=results.getValues(target, 'cing_red')
    reds = ax1.plot(x,red)
    plt.setp(reds, color='red', label='red', marker='s', markersize=8)
    
    x2,orange=results.getValues(target, 'cing_orange')
    oranges = ax1.plot(x2,orange)
    plt.setp(oranges, color='orange', label='orange', marker='s', markersize=8)
   
    x3,green=results.getValues(target, 'cing_green')
    greens = ax1.plot(x3,green)
    plt.setp(greens, color='green', label='green', marker='s', markersize=8)

    plt.title(target)

    xtickNames = plt.setp(ax1, xticklabels=results.methods)
    plt.setp(xtickNames, rotation=90, fontsize=12)
    ax1.xaxis.set_ticks(range(1,len(results.methods)+1))
    ax1.xaxis.set_label_text('methods', fontsize=14)
    ax1.yaxis.set_label_text('ROG (%)', fontsize=14)
    ax1.axis([0.1,len(results.methods)+1,0,100])
    ax1.grid(True)
    plt.tight_layout()
    plt.show()
#end def


plotROG('OR36')

