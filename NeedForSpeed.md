# Question: #
Can the CING validation be speeded up by speeding up the generation
of the images of the dihedral angles?

# Hypothesis: #
Ramachandran like plots take the longest and can be done faster by
eliminating the generation of the nice shaded areas by caching them.

# Result: #
The Ramachandran like plots are not significantly slower than the simple
1D plot. Below are tables with on each row the number of times a plot was generated
and the time in seconds it took. See cing/Scripts/d1d2plot.py

  * Rama plots
```
Without debugging                                       
#count,time                                            With debugging
1 3.8                                                  1 2.1
2 4.4                                                  2 4.1
10 8.5 	# ~ 0.5 seconds per plot without overhead.     10 21.0
20 13.7                                                
```

  * Regular 1D dihedral plot:
```
Without debuggen                                                   
1 4 
2 4.6
10 9.0 # still about 0.5 seconds per plot without overhead.
20 14.6
```