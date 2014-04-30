#!/bin/tcsh -f
# the first argument ($1) is the directory where the analysis is run
# the second argument ($2) is the baseName


# Step 1: Find the base pairs is done with find_pair, this creates an input file for the program analyze
find_pair $2.pdb $2.inp

# Step 2: The program analyze then creates a file with a detailed analysis of the structure:

analyze $2.inp 

# Output
# $2.out    # Contains all parameters (propeller, slide, roll, twist, backbone torsions etc.)
#			# we can make plots from the values on a per bp basis, as well as H-bonding images
# additional output
# auxiliary.par  	# not clear yet
# bp_step.par		# Base pair step parameters, can be used for rendering
# bp_helical.par	# Base pair helical parameters, can be used for rendering
# Both can be used with rebuild to create Calladine-Drew schematic images 
# The trick here is to create the proper orientation for display
# We can use frame_mol for this.....?
# First create an alchemy file
rebuild bp_step.par $2_bp_step_rebuild_1.alc #[for one block per base-pair] 
rebuild -block2 bp_step.par $2_bp_step_rebuild_2.alc #[for one block per base] 
# Now create an image, use s as scale factor
alc2img -al -s=18 $2_bp_step_rebuild_1.alc $2_bp_step_rebuild_1.ps 	# postscript
alc2img -ral -s=50 $2_bp_step_rebuild_2.alc $2_bp_step_rebuild_2.r3d	# Raster3D


# pdb2img  # tried it, but gives some errors
# Rendering in Raster3D (not sure if this is needed...)
# cat temp2.r3d | render -png temp2.png
#cf_7methods.par  # PArameters derived using older methods, not needed for our purposes
#ref_frames.dat
#poc_haxis.r3d    # NOt created
#stacking.pdb     # PDB file containing stacked basepairs
# can be used to create images using
#mstack2img '-tlcdo -s=25' stacking.pdb 1 11 bdl084_
# hstacking.pdb  # NO clue yet
# dcmnfile # removes all the auxiliary files from the file system


