# pylint: disable-all
## Automatically adapted for numpy.oldnumeric Dec 01, 2009 by 

#
# Code from Wolfgang! Modified for new dicts, ...
#

import sys, os #@UnusedImport
#from Numeric import *
import numpy.oldnumeric as Numeric #@UnusedImport
from numpy.oldnumeric.mlab import median #@UnusedImport
from statpack import * #@UnusedWildImport

from pdbe2.analysis.Util import getPickledDict, createPickledDict

def erf(x):
    """
    Approximation to the erf-function with fractional error
    everywhere less than 1.2e-7
    """

    if x > 10.: return 1.
    if x < -10.: return -1.
    
    z = abs(x)
    t = 1. / (1. + 0.5 * z)

    r = t * Numeric.exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 + \
        t * (0.09678418 + t * (-0.18628806 + t * (0.27886807 + t * \
        (-1.13520398 + t * (1.48851587 + t * (-0.82215223 + t * \
        0.17087277)))))))))

    if x >= 0.:
        return 1. - r
    else:
        return r - 1.

def z_scores(x, mu, sd):
    return (x-mu)/sd

def _reduce(x):
    return reduce(lambda a,b: list(a)+list(b), x)

def as_tuple(x):

    if type(x) in (list, tuple):
        return x
    else:
        return (x,)

def clipped_exp(x):
    return Numeric.exp(Numeric.clip(x,-709., 709))

def average(x):
    return Numeric.sum(Numeric.array(x)) / len(x)

def variance(x, avg = None):
    if avg is None:
        avg = Numeric.average(x)

    return Numeric.sum(Numeric.power(Numeric.array(x) - avg, 2)) / (len(x) - 1.)

def standardDeviation(x, avg = None):
    return Numeric.sqrt(variance(x, avg))

def stable_sd(x, n_sd=3., min_length=20):

    if len(x) < min_length:
        if len(x) == 1:
            return 0.
        else:
            return standardDeviation(x)

    x = Numeric.array(x)
    _x = x
    _outliers = 0.
    
    i = 0

    while i < 10:

        mu = median(_x)
        sd = standardDeviation(_x, mu)

        outliers = Numeric.greater(abs(x-mu), n_sd*sd)

        if not Numeric.sum(outliers) or Numeric.sum(outliers==_outliers) == len(x):
            break

        _x = Numeric.compress(Numeric.logical_not(outliers), x)
        _outliers = outliers

        i += 1

    return sd

def setMask(itemList,compareItem):
  
  """
  Necessary in numpy - doesn't do string comparisons!
  """
  
  mask = []
  for item in itemList:
    if item == compareItem:
      mask.append(True)
    else:
      mask.append(False)
      
  return mask

def select_entries(data, selection):
    """
    selection: list of 2-tuples (residue, atom). Wildcards are supported.
    """

    S = []

    for s_res, s_atom in selection:

        s_atoms = []

        if not type(s_atom) in (list, tuple):
            S.append((s_res.capitalize(), ((s_atom.upper(),),)))
            continue

        for x in s_atom:
            
            if not type(x) in (list, tuple):
                x = (x.upper(),)
            else:
                x = list(x)
                x.sort()
                x = tuple([a.upper() for a in x])
                
            s_atoms.append(x)

        S.append((s_res.capitalize(), s_atoms))

    selection = S

    all = {}

    for entry, values in data.items():

        d = {}

        for amino_acid, atoms in values.items():

            found = False
            s_atoms = ()

            for s_res, s_atom in selection:

                if s_res == '*' or s_res == amino_acid:
                    found = True
                    s_atoms += s_atom

            if not found:
                continue

            star = [x[0] for x in s_atoms if x[0] == '*']

            if star:
                d[amino_acid] = atoms
                continue

            y = {}
            
            for atom_names, v in atoms.items():

                atom_names = list(atom_names)
                atom_names.sort()
                atom_names = tuple(atom_names)

                if atom_names in s_atoms:
                    y[atom_names] = v

            if y:
                d[amino_acid] = y

        if d:
            all[entry] = d

    return all

def collect_stats(data):

    d = {}

    for entry, d_entry in data.items():

        print entry

        for aa, d_aa in d_entry.items():

            for atoms, values in d_aa.items():

                key = aa.lower(), atoms[0].lower()

                if not key in d:
                    d[key] = []

                shift, exposure, ss = values

                for i in range(len(shift)):
                    datum = (exposure[i], ss[i], shift[i])
                    d[key].append(datum)

    return d

def process_secondary(data, referencing=None, n_points=200, atom_type='H', exclude_entries=(), molType='protein'):

    if molType == 'protein':
      second_keys = ('C', 'E', 'H', 'G', 'T')
      second_groups = (('C',), ('E', 'B'), ('H', 'I', 'G'), ('T',)) #@UnusedVariable
    else:
      second_keys = ('X',)
      second_groups = (('X',),) #@UnusedVariable

    stats = {}

    ## decompose with respect to secondary structure

    for entry, val in data.items():

        if exclude_entries and entry in exclude_entries:
            continue

        if referencing is not None:
            ref = referencing.get(entry, None)
            if ref is None:
                continue
            else:
                ref = ref[0]
        else:
            ref = 0.
            
        for amino_acid, res_dict in val.items():

            for atoms, values in res_dict.items():

                if atoms[0][0] <> atom_type:
                    continue

                _shifts, _exposure, _second = values

                for ss_key in second_keys:

                    mask = setMask(_second,ss_key)
                    #mask = Numeric.equal(_second, ss_key)

                    shifts = Numeric.compress(mask, _shifts)

                    if not shifts.any():
                        continue

                    exposure = Numeric.compress(mask, _exposure)

                    key = amino_acid, atoms, ss_key

                    if not key in stats:
                        stats[key] = ([],[])

                    stats[key][0].append(shifts-ref)
                    stats[key][1].append(exposure)

    ## clean up

    for key in stats.keys():

        shifts, exposure = stats[key]

        shifts = _reduce(shifts)

        if len(shifts) < n_points:
            print key, 'too few data', len(shifts)
            del stats[key]
            continue
        
        exposure = _reduce(exposure)

        stats[key] = (Numeric.array(shifts), Numeric.array(exposure))

    return stats

def process_data(data, referencing=None, n_points=200, exposure_cutoff=0.05, atom_type='H',
                 exclude_entries=(),molType='protein'):

    stats = process_secondary(data, referencing, n_points, atom_type, exclude_entries=exclude_entries,molType=molType)

    ## decompose with respect to accessibility

    S = {}
    bounds = {}

    for key, values in stats.items():

        shifts, exposure = values

        ind = Numeric.argsort(exposure)

        shifts = Numeric.take(shifts, ind)
        exposure = Numeric.take(exposure, ind)

        B = []

        mask = Numeric.less(exposure, exposure_cutoff)
        ind = Numeric.nonzero(mask)

        if len(shifts)-len(ind) < n_points:
            ind = range(len(shifts))

        if len(ind) >= n_points:

            print key, 0, len(ind), len(shifts)

            S[key + (0,)] = (Numeric.take(shifts, ind), Numeric.take(exposure, ind))
            B.append(exposure[len(ind)-1])

            shifts = shifts[len(ind):]
            exposure = exposure[len(ind):]

            i = 1
            
        else:
            i = 0

        n_classes = len(exposure) / int(n_points)

        n = int(len(exposure) / float(max(1, n_classes))) + 1

        while len(shifts) > n:

            print key, i, len(shifts[:n]), len(shifts)

            S[key + (i,)] = shifts[:n], exposure[:n]
            
            B.append(exposure[n])

            shifts = shifts[n:]
            exposure = exposure[n:]

            i += 1

        if len(shifts):

            print key, i, len(shifts)

            S[key + (i,)] = shifts, exposure
            B.append(exposure[-1])

        bounds[key] = B

    return S, bounds

def flag_entries(_data, stats, bounds, z_max, atom_type='H',molType='protein'):

    l = []

    for entry, val in _data.items():

        classes = decompose_classes(val, bounds,molType=molType)

        for key, shifts in classes.items():

            if not key in stats:
                print 'no stats', key
                continue

            mean, sd = stats[key][:2]

            Z = z_scores(shifts, mean, sd)
  
            if Numeric.sum(Numeric.greater(abs(Z), z_max)):
                l.append((entry, key))

    return l

def compile_statistics(atoms, exclude=()):

    S = {}

    for key, values in atoms.items():

        shifts, exposure = values #@UnusedVariable

        mean = median(shifts)
        sd = stable_sd(shifts)

        S[key] = mean, sd, shifts

    return S

def decompose_classes(entry, bounds, atom_type='H',molType='protein'):
    printDebug = 0
    if molType == 'protein':
      second_keys = ('C', 'E', 'H', 'G', 'T')
    else:
      second_keys = ('X',)

    d = {}

    for amino_acid, shift_dict in entry.items():
        for atoms, values in shift_dict.items():

            if atoms[0][0] <> atom_type:
                continue

            _shifts, _exposure, second = values

            for ss_key in second_keys:

                #if amino_acid == 'Arg' and ss_key == 'C' and atoms[0][:2] == 'HB':
                #  printDebug = True
                #else:
                #  printDebug = False
                
                mask = setMask(second,ss_key)
                
                # Doesn't work with strings
                #mask = Numeric.equal(second, ss_array)
                #print mask
                shifts = Numeric.compress(mask, _shifts)
                
                if not shifts.any():
                    continue
                
                exposure = Numeric.compress(mask, _exposure)
                
                key = amino_acid, atoms, ss_key
                
                #if printDebug:
                #  print mask
                #  print shifts
                #  print exposure
                #  print
                

                ## decompose wrt exposure. this assumes that
                ## exposure and shifts are sorted (ascending) wrt
                ## exposures.
                
                B = bounds.get(key, None)
                
                #if printDebug:
                #  print "B = ",B

                if not B:
                    #if printDebug:
                    #  print key, bounds.keys()
                    continue
                    
                listLastIndex = len(B) - 1

                for i in range(len(B)):
                
                    #if printDebug:
                    #  print i, B[i], exposure
                
                    # Note: this line changed to less_equal, otherwise values were ignored! Wim 01/12/2009
                    #if printDebug:
                    #  tt = Numeric.less_equal(exposure, B[i])
                    #  print tt
                    #  print "DONE1"
                    #  print Numeric.nonzero(tt)
                    #  print "DONE2"
                      
                    ind = Numeric.nonzero(Numeric.less_equal(exposure, B[i]))

                    # Hack - reset to all elements if some of the upper ones are missing. Happens occasionally.
                    if i == listLastIndex and ((not ind.any() and shifts.any()) or (ind[-1] + 1) != len(shifts)):
                      ind = range(len(shifts))
                      if printDebug:
                          print "  Warning: resetting final class to include all values for %s, %s, %s" % (amino_acid,ss_key,atoms)
                    
                    #if printDebug:
                    #  print i, ind

                    if not len(ind):
                        #if printDebug:
                        #  print "Cont"
                        #  print
                        continue
                    
                    d[key + (i,)] = Numeric.take(shifts, ind)

                    shifts = shifts[ind[-1]+1:]
                    exposure = exposure[ind[-1]+1:]
                    
                    #if printDebug:
                    #  print shifts,exposure
                    #  print d[key + (i,)]
                    #  print
                    
                    if not exposure.any():
                        #if printDebug:
                        #  print "Break"
                        #  print
                        break

    return d
        
def estimate_reference_single(entry, stats, bounds, ref=0.0, verbose=False,
                              exclude=None, entry_name=None, atom_type='H',
                              exclude_outliers=False,molType='protein'):

    A = 0.
    B = 0.

    S = 0.
    N = 1

    ## loop through all atom types

    classes = decompose_classes(entry, bounds, atom_type,molType=molType)

    if exclude and not entry_name:
        raise TypeError, 'attribute entry_name needs to be set.'

    n_excluded = 0
    n_total = 0
    for key, shifts in classes.items():

##         print entry_name, key

        if not key in stats:
            if verbose:
                print key,'no statistics.'
            continue

        if exclude and (entry_name, key) in exclude:
            print entry_name, key, 'excluded from ref estimation.'
            continue

        ## get statistics for current atom type

        mu, sd = stats[key][:2]
        k = 1./sd**2

        if exclude_outliers is not False:

        ## calculate Z scores and exclude shifts with high Z scores from analysis
            
            Z = abs(shifts-mu)/sd

            mask_include = Numeric.less(Z, exclude_outliers)

            shifts = Numeric.compress(mask_include, shifts)

            n_excluded += len(Z)-Numeric.sum(mask_include)
            n_total += len(Z)

        n = len(shifts)
        
        if not n:
            continue

        A += k*n*(median(shifts)-mu)
        B += k*n

        S += -0.5*len(shifts)*Numeric.log(k)+0.5*k*sum((Numeric.array(shifts)-mu-ref)**2)
        N += n

    if B > 0.:

        ref_mu = A/B
        ref_sd = 1./Numeric.sqrt(B)

    else:
        ref_mu = None
        ref_sd = None

    if exclude_outliers is not False and n_excluded == n_total:
        print '%d/%d outliers discarded' % (n_excluded, n_total)

    return ref_mu, ref_sd, S/N

def calculate_reliabilities_single(entry, stats, bounds, ref=0.0, verbose=False,
                                   exclude=None, entry_name=None, atom_type='H',
                                   molType = 'protein'):

    ## loop through all atom types

    classes = decompose_classes(entry, bounds, atom_type,molType=molType)

    if exclude and not entry_name:
        raise TypeError, 'attribute entry_name needs to be set.'

    d = {}

    for key, shifts in classes.items():
    
        #if key[0] == 'Arg' and key[1] == ('HB2',):
          #print "ESTIMATE", key, shifts

##         print key, len(shifts)

        if not key in stats:
            if verbose:
                print key,'no statistics.'
            continue

        if exclude and (entry_name, key) in exclude:
            print entry_name, key, 'excluded from ref estimation.'
            continue

        ## reference shifts

        shifts = Numeric.array(shifts)-ref

        mu, sd = stats[key][:2]

        ## calculate probabilities and Z-scores

        P = [1.-erf(abs(x-mu)/(Numeric.sqrt(2)*sd)) for x in shifts]
        Z = list((shifts-mu)/sd)

        if key in d:
            raise

        d[key] = (list(shifts), P, Z, ref)

    return d

def calculate_reliabilities(data, stats, bounds, ref=None, verbose=False,
                            exclude=None, entry_name=None, atom_type='H',
                            molType='protein'):

    d = {}

    for entry in data.keys():

        if ref is None:
            _ref = 0.0
        else:
            _ref = ref[entry][0]

        if _ref is None:
            print 'No referencing information for', entry
            continue

        result = calculate_reliabilities_single(data[entry], stats, bounds, _ref, verbose,
                                                exclude, entry_name, atom_type,molType=molType)

        if result:
            d[entry] = result

    return d

def estimate_references(data, stats, bounds, refs=None, verbose=None, exclude=None, atom_type='H',
                        exclude_outliers=False,molType='protein'):

    R = {}

    for name, entry in data.items():

        if refs is not None:
            ref = refs.get(name, 0.0)
        else:
            ref = 0.

        R[name] = estimate_reference_single(entry, stats, bounds, ref, verbose, exclude, name, atom_type,
                                            exclude_outliers,molType=molType)

    return R

def normalise_global(ref):

    R = [x[0] for x in ref.values() if x[0] is not None]

    try:
        ref0 = median(R)
    except:
        print R
        print ref
        raise

    d = {}

    for key, value in ref.items():

        if value[0] is not None:
            value = (value[0]-ref0,) + value[1:]

        d[key] = value

    return d, ref0

def rereference_single(data, ref, atom_type='H'):
    """
    loops through all entries and compiles mean and sd for all atom types.
    """

    D = {}

    for amino_acid, shift_dict in data.items():

        d2 = {}

        for atoms, values in shift_dict.items():

            if atoms[0][0] <> atom_type:
                continue

            shifts, exposure, second = values

            shifts = list(Numeric.array(shifts)-ref)

            d2[atoms] = shifts, exposure, second

        D[amino_acid] = d2

    return D

def rereference_data(data, referencing, cutoff=None, atom_type='H'):

    D = {}

    n = 0

    for entry, val in data.items():
        
        if entry in referencing:
            
            ref = referencing[entry][0]

            if ref is not None:

                if cutoff is not None:
                
                    if abs(ref) > cutoff:
                        D[entry] = rereference_single(val, ref, atom_type)
                        n += 1
                    else:
                        D[entry] = val

                else:
                    D[entry] = rereference_single(val, ref, atom_type)

    if cutoff is not None:
        print '#entries re-referenced:', n

    return D

def run_estimation(data, n=1, n_points=200, exclude=None, ref_cutoff=None, atom_type='H',
                   normalise=False, exclude_from_stats=(), exclude_outliers=False,
                   molType = 'protein'):

    ref = None
    data_ref = data

    for i in range(n):

        print 'Round', i

        if ref is not None:
            data_ref = rereference_data(data, ref, ref_cutoff, atom_type)

        processed, bounds = process_data(data_ref, n_points=n_points,
                                         exposure_cutoff=0.05, atom_type=atom_type,
                                         exclude_entries=exclude_from_stats,
                                         molType = molType)
        
        stats = compile_statistics(processed)
        ref = estimate_references(data, stats, bounds, exclude=exclude, atom_type=atom_type,
                                  exclude_outliers=exclude_outliers,molType=molType)

        if normalise:
            ref, ref0 = normalise_global(ref)
            print 'median ref:', ref0

    return ref, stats, bounds, processed

def create_test_set(_data, _min=0., _max=.25, atom_type='H'):

    from random import random #@Reimport

    correct = {}

    test_set = {}

    for name, entry in _data.items():

        D = {}

        err = random()*(_max-_min)

        if random() > 0.5:
            err = -err

        correct[name] = err

        for amino_acid, shift_dict in entry.items():

            d2 = {}

            for atoms, values in shift_dict.items():

                if atoms[0][0] <> atom_type:
                    continue

                shifts, exposure, second = values

                shifts = (Numeric.array(shifts)+err).tolist()

                d2[atoms] = shifts, exposure, second

            D[amino_acid] = d2

        test_set[name] = D

    return test_set, correct

def test_accuracy(_data, stats, bounds, _min=0., _max=0.1, atom_type='H',molType='protein'):

    test_set, correct = create_test_set(_data, _min, _max, atom_type)
    
    refs = estimate_references(test_set, stats, bounds,molType=molType)

    keys = _data.keys()
    keys.sort()

    correct = [correct[k] for k in keys]
    estimate = [refs[k][0] for k in keys]

    return Numeric.array(correct), Numeric.array(estimate)
        
def make_selection(d):

    s = []

    for k, v in d.items():
        s += [(k.lower(), x.lower()) for x in v]


    return s

def make_sel3(stats, others):

    l = []

    for k in stats:

        key = (k[0].lower(), k[1][0].lower())

        if key[1] == 'c':
            continue

        if not key in others and not key in l:
            l.append(key)

    return l

if __name__ == '__main__':

  import time

  ref = {}
  stats = {}
  bounds = {}
  processed = {}

  reliabilities_before = {}
  reliabilities_after = {}    
  
  timeStamp = time.strftime("%Y%m%d")

  #database = 'atomExposedWithSs_070926.pp'
  #database = 'atomExposedWithSs_080312.pp'
  #database = 'whatIfAtomExposed_090416.pp'
  database = 'whatIfAtomExposed_100225.pp'
  
  for molType in ('protein','RNA'):

    if molType == 'protein':
      group0 = {'arg': ('cz',),
                'asn': ('cg',),
                'asp': ('cg',),
                'gln': ('cd',),
                'glu': ('cd',),
                'his': ('cg'),
                'phe': ('cg',),
                'trp': ('cd2','ce2'),
                'tyr': ('cg', 'cz')}

      group1 = {'arg': ('cz',),
                'asn': ('cg',),
                'asp': ('cg',),
                'gln': ('cd',),
                'glu': ('cd',),
                'his': ('cg'),
                'phe': ('cg',),
                'trp': ('cd2','ce2'),
                'tyr': ('cg', 'cz'),
                '*': ('c',)}

      group2 = {'his': ('cd2', 'ce1'),
                'phe': ('cd1', 'cd2', 'ce1', 'ce2', 'cz'),
                'trp': ('cd1', 'ce3', 'ch2', 'cz2', 'cz3'),
                'tyr': ('cd1', 'cd2', 'ce1', 'ce2')}

      group4 = {'*': ('c',)}

    if molType == 'protein':
      n_points = 200
    else:
      # Less critical for DNA, RNA, ...
      n_points = 100

    for atom_type in ('H','C','N'):

      #atom_type = 'H'
      ref_cutoff = None
      normalise = True
      exclude_outliers = 4.
      n_iterations = 1

      print 'Reading raw data...'
      full_set = getPickledDict(os.path.join("../originalData/results/",database))

      for entry in full_set.keys():
        if full_set[entry].has_key(molType):
          full_set[entry] = full_set[entry][molType]
        else:
          del(full_set[entry])

      print 'Running estimation for full set...'     
      full_ref, full_stats, full_bounds, full_processed = run_estimation(full_set, n=1, n_points=n_points,
                                                                             ref_cutoff=ref_cutoff,
                                                                             atom_type=atom_type,
                                                                             molType = molType)

      if atom_type == 'C' and molType == 'protein':

        sel0 = make_selection(group0)
        sel1 = make_selection(group1)
        sel2 = make_selection(group2)
        sel3 = make_sel3(full_stats, sel1+sel2)
        sel4 = make_selection(group4)

        set_group0 = select_entries(full_set, sel0)
        set_group1 = select_entries(full_set, sel1)
        set_group2 = select_entries(full_set, sel2)
        set_group3 = select_entries(full_set, sel3)
        set_group4 = select_entries(full_set, sel4)

        groups = {1: set_group1, 2: set_group2, 3: set_group3, 4: set_group4}

      else:
        groups = {None: full_set}

      ref[atom_type] = {}
      stats[atom_type] = {}
      bounds[atom_type] = {}
      processed[atom_type] = {}

      reliabilities_before[atom_type] = {}
      reliabilities_after[atom_type] = {}    

      for i, group in groups.items():

          print 'Group', i

          _ref, _stats, _bounds, _processed = run_estimation(group, n=n_iterations, n_points=n_points,
                                                             ref_cutoff=ref_cutoff,
                                                             atom_type=atom_type,
                                                             normalise=normalise,
                                                             exclude_outliers=exclude_outliers,
                                                             molType = molType)

          if i != None:
            ref[atom_type][i] = _ref
            stats[atom_type][i] = _stats
            bounds[atom_type][i] = _bounds
            processed[atom_type][i] = _processed
          else:
            ref[atom_type] = _ref
            stats[atom_type] = _stats
            bounds[atom_type] = _bounds
            processed[atom_type] = _processed

          _reliabilities_before = calculate_reliabilities(group, _stats, _bounds,
                                                            ref=None, atom_type=atom_type,
                                                            molType = molType)

          if i != None:
            _ref = ref[atom_type][i]
          else:
            _ref = ref[atom_type]  

          _reliabilities_after = calculate_reliabilities(group, _stats, _bounds,
                                                           ref=_ref, atom_type=atom_type,
                                                           molType = molType)

          if i != None:
            reliabilities_before[atom_type][i] = _reliabilities_before
            reliabilities_after[atom_type][i] = _reliabilities_after
          else:
            reliabilities_before[atom_type] = _reliabilities_before
            reliabilities_after[atom_type] = _reliabilities_after



    if molType == 'protein':
      suffix = ""
    else:
      suffix = "%s_" % molType

    createPickledDict(os.path.join('data','ref_%s%s.pp' % (suffix,timeStamp)),ref)
    createPickledDict(os.path.join('data','stats_%s%s.pp' % (suffix,timeStamp)),stats)
    createPickledDict(os.path.join('data','bounds_%s%s.pp' % (suffix,timeStamp)),bounds)
    createPickledDict(os.path.join('data','processed_%s%s.pp' % (suffix,timeStamp)),processed)
    createPickledDict(os.path.join('data','reliabilities_before_%s%s.pp' % (suffix,timeStamp)),reliabilities_before)
    createPickledDict(os.path.join('data','reliabilities_after_%s%s.pp' % (suffix,timeStamp)),reliabilities_after)

    """
    estimate_reference_single: is to estimate reref for a single entry

    stats classes: each has mean, take standard deviation from this, then this is used to compare for a single entry,
    so ALL exposure classes are used!!!

    When to ignore entries: use re-ref value, and uncertainty. If re-ref smaller than uncertainty, then IGNORE!

    Can use calculate_reliabilities_single() for getting shift specific info!

    """
