# Explanations of external program features #

> ## What If ##
See [Protein structure verification](http://proteins.dyndns.org/Education/Validation/HTML/CheckHelp/index.html) and "A crystallographer's [guide](http://proteins.dyndns.org/Education/Validation/HTML/USF/whatif.html) to interpreting WHATIF output".


> ## Procheck\_NMR ##
See AQUA and PROCHECK-NMR - [Operating manual](http://www.biochem.ucl.ac.uk/~roman/procheck_nmr/manual/index.html).


# Ramachandran and Janin plots #
  * The background shading is for the probability derived from What If’s internal database of high-resolution structures on a 10 by 10 degree grid. The color coding refers to one of three states the secondary structure (by DSSP) was assigned to be in. Blue, green, and yellow are respectively for helix, sheet, and other. The coloring changes linearly from white to e.g. yellow for densities 2 to 20%. They are consequently put on top of each other (blue on top) with some alpha blending. More details in code at [dihedralComboPlot](http://code.google.com/p/cing/source/browse/trunk/cing/python/cing/Libs/NTplot.py).
  * The chi 1 and 2 combination plot is named after [Janin](http://en.wikipedia.org/wiki/Janin_Plot).


# Symbols #
  * <font color='blue'> ◦ <font color='black'> (blue) circular averaged value<br>
<ul><li><font color='green'>+ <font color='black'>(green) non-proline/glycine<br>
</li><li><font color='green'> ▴ <font color='black'>(green) non-cacheable-proline/glycine