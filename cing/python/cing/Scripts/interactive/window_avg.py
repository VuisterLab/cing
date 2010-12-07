#!/usr/bin/env python
from cing.Libs.NTutils import NTdebug
import cing
import numpy
import pylab
from numpy import * #@UnusedWildImport

cing.verbosity = cing.verbosityDebug


def smoothTriangle(data,degree=1,dropVals=False):
    cvWindowSize = 3
    n = len(data)
    NTdebug("data: %s" % str(data))
    w=ones(cvWindowSize,'d')
    windowAveraged=convolve(w/w.sum(),data,mode='same')
    windowAveraged[0] = data[0]
    windowAveraged[n-1] = data[n-1]
    return windowAveraged

def smoothTriangleOther(data,degree=1,dropVals=False):
    NTdebug("data: %s" % str(data))
    degree = 1 # 1 point on each side except for end points that will be 2:1
    beginAverage = [ 2/3., 1/3. ]
    endAverage = [ 1/3., 2/3. ]
    n =  len(data)
    triangle=numpy.array(range(degree)+[degree]+range(degree)[::-1])+1
    sumTriangle = sum(triangle)
    NTdebug("triangle: %s" % triangle)
    smoothed=[]
    startIdx = degree
    endIdx = n-degree*2
    NTdebug("n, degree, startIdx, endIdx: %s,%s,%s,%s" % (n, degree, startIdx,endIdx))
    for i in range(startIdx,endIdx):
        section = data[i:i+len(triangle)]
        point=section*triangle
        smValue = sum(point)/sumTriangle
        NTdebug("Looking at section i %s: %s smoothed to: %s" % (i,str(section),smValue))
        smoothed.append(smValue)
    if dropVals:
        return smoothed
    NTdebug("smoothed[0]: %s" % smoothed[0])
    NTdebug("smoothed: %s" % str(smoothed))
    smoothedStart = (data[0] * beginAverage[0] + data[1] * beginAverage[1])
    smoothedEnd = (data[n-2] * endAverage[0] + data[n-1] * endAverage[1])
    NTdebug("smoothedStart: %s" % str(smoothedStart))
    NTdebug("smoothedEnd: %s" % str(smoothedEnd))

    smoothed = [smoothedStart] + smoothed + [smoothedEnd]
    while len(smoothed) < n:
        smoothed.append(smoothed[-1])
    return smoothed

def smoothTriangleOld(data,degree,dropVals=False):
        """performs moving triangle smoothing with a variable degree."""
        """note that if dropVals is False, output length will be identical
        to input length, but with copies of data at the flanking regions"""
        triangle=numpy.array(range(degree)+[degree]+range(degree)[::-1])+1
        NTdebug("triangle: %s" % triangle)
        smoothed=[]
        for i in range(degree,len(data)-degree*2):
                point=data[i:i+len(triangle)]*triangle
                smoothed.append(sum(point)/sum(triangle))
        if dropVals:
            return smoothed
        NTdebug("data: %s" % str(data))
        NTdebug("smoothed[0]: %s" % smoothed[0])
        NTdebug("smoothed: %s" % str(smoothed))

        smoothedStart=[smoothed[0]]*(degree+degree/2)
        NTdebug("smoothedStart: %s" % str(smoothedStart))

        smoothed = smoothedStart + smoothed
        while len(smoothed) < len(data):
            smoothed.append(smoothed[-1])
        return smoothed

### CREATE SOME DATA ###
n = 10
data=numpy.random.random(n) #make 100 random numbers from 0-1
data=numpy.array(data*100,dtype=int) #make them integers from 1 to 100
for i in range(n):
        data[i]=data[i]+i**((15-i)/80.0) #give it a funny trend
#data = [ 1, 1, 1, 1 ]
#data = [ 0, 1, 2, 3 ]
data = [ 4, 2, 1, 0, 1, 2, 4 ]
### GRAPH ORIGINAL/SMOOTHED DATA ###
pylab.plot(data,"k.-",label="original data",alpha=.3)
pylab.plot(smoothTriangle(data,1),"bx-",label="smoothed d=1")
#pylab.plot(smoothTriangle(data,3),"-",label="smoothed d=3")
#pylab.plot(smoothTriangle(data,5),"-",label="smoothed d=5")
#pylab.plot(smoothTriangle(data,10),"-",label="smoothed d=10")
pylab.title("Moving Triangle Smoothing")
pylab.grid(alpha=.3)
#pylab.axis([20,80,50,300])
pylab.legend()
pylab.show()