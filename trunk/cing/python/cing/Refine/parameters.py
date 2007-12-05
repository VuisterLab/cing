from cing.Libs.NTutils import NTdict

params = NTdict(

      baseName          = 'H2_AD_EDTA%03d.pdb',
      models            = range( 0, 20 ),		# any python list here allows to select the model(s) to refine
                                                # can also be modified as command-line argument

      overwrite         = True,                 # Overwrite existing files
      verbose           = True,                 # verbose on/off
      useCluster        = False,                # use cluster; not yet implemented     

      # PSF generation
      psfFile           = 'H2_EDTA.psf',            
      patchHISD         = [501, 513, 640], 		# HISD patches are needed for CYANA->XPLOR compatibility.
                                                # enter your residue numbers here
      patchHISE         = [],

      patchCISP         = [],                   # Cis prolines
      
      # initial analysis
      minimizeProtons   = False,
            
      # NOE restraints
      noeMaxRestraints  = 30000,
      noeCeiling        = 100,    
      noeRestraints     = [
                           NTdict(
                                    name      = 'HH',
                                    averaging = 'sum',
                                    scale     = 50,
                                    accept    = 0.5,
                                    fileName  = 'final.tbl' # should be in the Tables directory
                                   ),
#                            NTdict(
#                                     name      = 'Ca',
#                                     averaging = 'sum',
#                                     accept    = 0.5,
#                                     fileName  = 'Ca.tbl' # should be in the Tables directory
#                                    ),
                          ],
      # dihedral restraints
      dihedralMaxRestraints = 10000,
      dihedralScale      = 200,
      dihedralRestraints = [
                            NTdict(
                                     name      = 'talos',
                                     accept    = 5.0,
                                     fileName  = 'talos.tbl' # should be in the Tables directory
                                    ),
                          ],
                          

      # water refinement protocol
      
      # type of non-bonded parameters: "PROLSQ" "PARMALLH6" "PARALLHDG" "OPLSX" 
      # The water refinement uses the OPLSX parameters 
      nonBonded         = 'OPLSX',
      temp              = 500,                          # temperature (K); 500 initially
      mdheat            = NTdict( # 100,0.003 initially with Chris
                                    nstep  = 100,       # number of MD steps
                                    timest = 0.003,     # timestep of MD (ps)
                                  ),
      mdhot             = NTdict( # 2000, 0.004 initially with Chris
                                    nstep  = 2000,      # number of MD steps
                                    timest = 0.004,     # timestep of MD (ps)
                                  ),
      mdcool            = NTdict( # 200, 0.004 initially with Chris
                                    nstep  = 200,       # number of MD steps
                                    timest = 0.004,     # timestep of MD (ps)
                                  ),

)

params.keysformat()