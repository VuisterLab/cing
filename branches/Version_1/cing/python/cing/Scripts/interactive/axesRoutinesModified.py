#@PydevCodeAnalysisIgnore # pylint: disable-all

# next lines to be indented.





def boxplot(self, x, notch=0, sym='b+', vert=1, whis=1.5,
                positions=None, widths=None, patch_artist=False,
                bootstrap=None):
        """
        call signature::

          boxplot(x, notch=0, sym='+', vert=1, whis=1.5,
                  positions=None, widths=None, patch_artist=False)

        Make a box and whisker plot for each column of *x* or each
        vector in sequence *x*.  The box extends from the lower to
        upper quartile values of the data, with a line at the median.
        The whiskers extend from the box to show the range of the
        data.  Flier points are those past the end of the whiskers.

        *x* is an array or a sequence of vectors.

        - *notch* = 0 (default) produces a rectangular box plot.
        - *notch* = 1 will produce a notched box plot

        *sym* (default 'b+') is the default symbol for flier points.
        Enter an empty string ('') if you don't want to show fliers.

        - *vert* = 1 (default) makes the boxes vertical.
        - *vert* = 0 makes horizontal boxes.  This seems goofy, but
          that's how MATLAB did it.

        *whis* (default 1.5) defines the length of the whiskers as
        a function of the inner quartile range.  They extend to the
        most extreme data point within ( ``whis*(75%-25%)`` ) data range.

        *bootstrap* (default None) specifies whether to bootstrap the
        confidence intervals around the median for notched
        boxplots. If bootstrap==None, no bootstrapping is performed,
        and notches are calculated using a Gaussian-based asymptotic
        approximation (see McGill, R., Tukey, J.W., and Larsen, W.A.,
        1978, and Kendall and Stuart, 1967). Otherwise, bootstrap
        specifies the number of times to bootstrap the median to
        determine it's 95% confidence intervals. Values between 1000
        and 10000 are recommended.

        *positions* (default 1,2,...,n) sets the horizontal positions of
        the boxes. The ticks and limits are automatically set to match
        the positions.

        *widths* is either a scalar or a vector and sets the width of
        each box. The default is 0.5, or ``0.15*(distance between extreme
        positions)`` if that is smaller.

        - *patch_artist* = False (default) produces boxes with the Line2D artist
        - *patch_artist* = True produces boxes with the Patch artist

        Returns a dictionary mapping each component of the boxplot
        to a list of the :class:`matplotlib.lines.Line2D`
        instances created.

        **Example:**

        .. plot:: pyplots/boxplot_demo.py
        """

        print "notch %s sym %s whis %s" % ( notch, sym, whis)
        wiskLoL = []

        if not self._hold: self.cla()
        holdStatus = self._hold
        whiskers, caps, boxes, medians, fliers = [], [], [], [], []

        # convert x to a list of vectors
        if hasattr(x, 'shape'):
            if len(x.shape) == 1:
                if hasattr(x[0], 'shape'):
                    x = list(x)
                else:
                    x = [x,]
            elif len(x.shape) == 2:
                nr, nc = x.shape
                if nr == 1:
                    x = [x]
                elif nc == 1:
                    x = [x.ravel()]
                else:
                    x = [x[:,i] for i in xrange(nc)]
            else:
                raise ValueError, "input x can have no more than 2 dimensions"
        if not hasattr(x[0], '__len__'):
            x = [x]
        col = len(x)
        # get some plot info
        if positions is None:
            positions = range(1, col + 1)
        if widths is None:
            distance = max(positions) - min(positions)
            widths = min(0.15*max(distance,1.0), 0.5)
        if isinstance(widths, float) or isinstance(widths, int):
            widths = np.ones((col,), float) * widths

        # loop through columns, adding each to plot
        self.hold(True)
        print "Number of columns: %s" % col
        for i,pos in enumerate(positions):
            d = np.ravel(x[i])
            row = len(d)
            print "Working on serie i %s at pos %s with length %s" % (i,pos,row)
            if row==0:
                # no data, skip this position
                continue
            # get median and quartiles
            p10, q1, med, q3, p90 = mlab.prctile(d,[10,25,50,75,90])
            print "p10, q1, med, q3, p90 %s %s %s %s %s" % (p10, q1, med, q3, p90 )
            wisk_lo, wisk_hi = p10, p90
            wiskLoL.append( [wisk_lo, wisk_hi] )
            # get high extreme
#            iq = q3 - q1
#            hi_val = q3 + whis*iq
#            wisk_hi = np.compress( d <= hi_val , d )
#            print "iq, hi_val, wisk_hi  %s %s %s" % (iq, hi_val, wisk_hi )
#            if len(wisk_hi) == 0:
#                wisk_hi = q3
#            else:
#                wisk_hi = max(wisk_hi)
            # get low extreme
#            lo_val = q1 - whis*iq
#            wisk_lo = np.compress( d >= lo_val, d )
#            if len(wisk_lo) == 0:
#                wisk_lo = q1
#            else:
#                wisk_lo = min(wisk_lo)
            print "wisk_lo, wisk_hi %s %s" % (wisk_lo, wisk_hi)
            # get fliers - if we are showing them
            flier_hi = []
            flier_lo = []
            flier_hi_x = []
            flier_lo_x = []
            if len(sym) != 0:
                print "Adding fliers"
                flier_hi = np.compress( d > wisk_hi, d )
                flier_lo = np.compress( d < wisk_lo, d )
                flier_hi_x = [pos for _i in range(flier_hi.shape[0])]
                flier_lo_x = [pos for _i in range(flier_lo.shape[0])]
#                flier_lo_x = np.ones(flier_lo.shape[0]) * pos
#                flier_lo_x = np.ones(flier_lo.shape[0]) * pos
            print "flier_lo, flier_hi %s %s" % (flier_lo, flier_hi)

            # get x locations for fliers, whisker, whisker cap and box sides
            halfWidth =  datetime.timedelta(183)
            quartWidth =  datetime.timedelta(92)
            box_x_min = pos - halfWidth
            box_x_max = pos + halfWidth

#            wisk_x = np.ones(2) * pos
            wisk_x = [pos, pos]

            cap_x_min = pos - quartWidth
            cap_x_max = pos + quartWidth
            cap_x = [cap_x_min, cap_x_max]

            # get y location for median
            med_y = [med, med]

            # calculate 'regular' plot
            if notch == 0:
                # make our box vectors
                box_x = [box_x_min, box_x_max, box_x_max, box_x_min, box_x_min ]
                box_y = [q1, q1, q3, q3, q1 ]
                # make our median line vectors
                med_x = [box_x_min, box_x_max]
            # calculate 'notch' plot
            else:
                if bootstrap is not None:
                    # Do a bootstrap estimate of notch locations.
                    def bootstrapMedian(data, N=5000):
                        # determine 95% confidence intervals of the median
                        M = len(data)
                        percentile = [2.5,97.5]
                        estimate = np.zeros(N)
                        for n in range(N):
                            bsIndex = np.random.random_integers(0,M-1,M)
                            bsData = data[bsIndex]
                            estimate[n] = mlab.prctile(bsData, 50)
                        CI = mlab.prctile(estimate, percentile)
                        return CI

                    # get conf. intervals around median
                    CI = bootstrapMedian(d, N=bootstrap)
                    notch_max = CI[1]
                    notch_min = CI[0]
                else:
                    # Estimate notch locations using Gaussian-based
                    # asymptotic approximation.
                    #
                    # For discussion: McGill, R., Tukey, J.W.,
                    # and Larsen, W.A. (1978) "Variations of
                    # Boxplots", The American Statistician, 32:12-16.
                    notch_max = med + 1.57*iq/np.sqrt(row)
                    notch_min = med - 1.57*iq/np.sqrt(row)
                # make our notched box vectors
                box_x = [box_x_min, box_x_max, box_x_max, cap_x_max, box_x_max,
                         box_x_max, box_x_min, box_x_min, cap_x_min, box_x_min,
                         box_x_min ]
                box_y = [q1, q1, notch_min, med, notch_max, q3, q3, notch_max,
                         med, notch_min, q1]
                # make our median line vectors
                med_x = [cap_x_min, cap_x_max]
                med_y = [med, med]

            def to_vc(xs,ys):
                # convert arguments to verts and codes
                verts = []
                #codes = []
                for xi,yi in zip(xs,ys):
                    verts.append( (xi,yi) )
                verts.append( (0,0) ) # ignored
                codes = [mpath.Path.MOVETO] + \
                        [mpath.Path.LINETO]*(len(verts)-2) + \
                        [mpath.Path.CLOSEPOLY]
                return verts,codes

            def patch_list(xs,ys):
                verts,codes = to_vc(xs,ys)
                path = mpath.Path( verts, codes )
                patch = mpatches.PathPatch(path)
                self.add_artist(patch)
                return [patch]

            # vertical or horizontal plot?
            if vert:
                def doplot(*args):
                    return self.plot(*args)
                def dopatch(xs,ys):
                    return patch_list(xs,ys)
            else:
                def doplot(*args):
                    shuffled = []
                    for i in xrange(0, len(args), 3):
                        shuffled.extend([args[i+1], args[i], args[i+2]])
                    return self.plot(*shuffled)
                def dopatch(xs,ys):
                    xs,ys = ys,xs # flip X, Y
                    return patch_list(xs,ys)

            if patch_artist:
                median_color = 'k'
            else:
                median_color = 'r'
#                median_color = 'k'
# JFD mods:
            whiskers.extend(doplot(wisk_x, [q1, wisk_lo], 'b--',
                                   wisk_x, [q3, wisk_hi], 'b--'))
#            whiskers.extend(doplot(wisk_x, [q1, wisk_lo], 'k--',
#                                   wisk_x, [q3, wisk_hi], 'k--'))
            caps.extend(doplot(cap_x, [wisk_hi, wisk_hi], 'k-',
                               cap_x, [wisk_lo, wisk_lo], 'k-'))
            if patch_artist:
                boxes.extend(dopatch(box_x, box_y))
            else:
                boxes.extend(doplot(box_x, box_y, 'b-'))
#                boxes.extend(doplot(box_x, box_y, 'k-'))
            medians.extend(doplot(med_x, med_y, median_color+'-'))
            fliers.extend(doplot(flier_hi_x, flier_hi, sym,
                                 flier_lo_x, flier_lo, sym))

        # fix our axes/ticks up a little
        if 1 == vert:
            setticks, setlim = self.set_xticks, self.set_xlim
        else:
            setticks, setlim = self.set_yticks, self.set_ylim

        differenceAday = datetime.timedelta(1)
        newlimits = min(positions)-differenceAday, max(positions)+differenceAday
        setlim(newlimits)
#        setticks(positions)

        # reset hold status
        self.hold(holdStatus)
#        if returnWhiskers:
        return wiskLoL
#        return dict(whiskers=whiskers, caps=caps, boxes=boxes,
#                    medians=medians, fliers=fliers)





