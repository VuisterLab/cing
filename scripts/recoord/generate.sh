#!/bin/sh

PROGRAM=generate.sh
VERSION=0.1A
AUTHOR="Tsjerk A. Wassenaar, PhD"
YEAR="2008.10"
AFFILIATION="
University of Utrecht\n
Padualaan 8\n
3584CH Utrecht\n
The Netherlands"

DESCRIPTION="\
"

pdb=in.pdb
cns=cns.pdb
psf=cns.psf
log=cns.log
sel=""
sol=1
cnsExec=

OPTIONS="
\t# File options:\n
\t  -f \t $pdb \t Input coordinate file (PDB)\n
\t  -o \t $cns \t Output coordinate file (PDB, CNS)\n
\t  -p \t $psf \t Output CNS topology file (PSF)\n
\t  -g \t $log \t Logfile (TXT)\n
\t  -x \t      \t Executable for processing CNS script (default: cns)\n
"

USAGE="\n$PROGRAM version $VERSION:\n\n$DESCRIPTION\n\n$OPTIONS\n\n(c)$YEAR $AUTHOR\n$AFFILIATION\n"

BAD_OPTION ()
{
  echo
  echo "Unknown option \"$1\" found on command-line"
  echo "It may be a good idea to read the usage:"
  echo -e $USAGE

  exit 1
}

while [ -n "$1" ]; do
  case $1 in
    -h)       echo -e $USAGE       ; exit 0 ;;
    # File options
    -f)       pdb=$2    ; shift; shift; continue ;;
    -c)       cns=$2    ; shift; shift; continue ;;
    -o)       cns=$2    ; shift; shift; continue ;;
    -p)       psf=$2    ; shift; shift; continue ;;
    -g)       log=$2    ; shift; shift; continue ;;
    -s)       sel=$2    ; shift; shift; continue ;;
    -x)       cnsExec=$2; shift 2; continue ;;
    --nosol)  sol=""    ; shift; continue ;;
     *)       BAD_OPTION $1;;
  esac
done

###################
## PREPROCESSING ##
###################

if [[ `grep "^MODEL" BRSV-G.pdb | wc -l` > 0 ]]; then
  # Multi-model PDB file
  mv $pdb ${pdb%.pdb}-multi.pdb
  sed -ne "{/^MODEL *1 /,/ENDMDL/p}" ${pdb%.pdb}-multi.pdb > $pdb 
fi

DNASELECTION=none

CWD=`pwd`
SDIR=$CWD

# Check pdb file for END statement
if [ `sed -e '{/^END \*/!d;q;}' $pdb` ]; then END=""; else END=END; fi

# Try to set the CNS environment if no executable is given
if [ -z $cnsExec ]; then
  source $VO_ENMR_EU_SW_DIR/BCBR/cns/1.2-para/set_cns.bash
  cnsExec=`which cns`
fi

##########################
## DOING THE REAL STUFF ##
##########################

$cnsExec > $log << EOF

   set message=on echo=on end
   evaluate (\$par_nonbonded="PROLSQ")
  
   topology
       @@topallhdg5.3.pro
      ! @@dna-rna-allatom.top
       @@topallhdg5.3.sol
       @@carbohydrate.top
   end
  
   parameter
       @@parallhdg5.3.pro
     !  @@dna-rna-allatom.param
       @@parallhdg5.3.sol
       @@carbohydrate.param
   end
  
   segment
     chain
       convert=true
       separate=true
       @@topallhdg5.3.pep
       !@@dna-rna.link
       coordinates @@$pdb $END
     end
   end
  
   coordinates convert=true @@$pdb $END
  
   ! cis peptide patch, based on cis_peptide.inp, 
   ! added by Aart Nederveen, May 27 2003 
   for \$id in id ( known and name ca ) loop main
  
     show (segid)   (id \$id) evaluate (\$segid=\$result)
     show (resid)   (id \$id) evaluate (\$resid=\$result)
     show (resname) (id \$id) evaluate (\$resname=\$result)
  
     identity (store1) ( known and ( name c and bondedto ( name n and resid \$resid and segid \$segid ) ) )
     if ( \$select = 1 ) then
       show element (store1) (attribute store1 > 0) evaluate (\$id_prev=\$result)
       show (segid)   (id \$id_prev) evaluate (\$segid_prev=\$result)
       show (resid)   (id \$id_prev) evaluate (\$resid_prev=\$result)
       show (resname) (id \$id_prev) evaluate (\$resname_prev=\$result)
   
       pick dihedral
         (name ca and segid \$segid_prev and resid \$resid_prev)
         (name  c and segid \$segid_prev and resid \$resid_prev)
         (name  n and segid \$segid and resid \$resid)
         (name ca and segid \$segid and resid \$resid)
         geometry
         
       evaluate ( \$absdih = abs(mod(\$result+180,360)-180) ) 

       set display=OUTPUT end
       display \$absdih
       if ( \$absdih < 25 ) then
         patch cisp reference=NIL=(segid \$segid_prev and resid \$resid_prev) end
       end if
       set display=OUTPUT end
     end if
   end loop main ! end cis peptide patch

   ! There used to be an auto-break detection here --TAW--
  
   evaluate (\$disu=0)
  
   for \$id1 in id ( resname CYS and name SG ) loop dis1
     show (segid) (id \$id1) evaluate (\$segid1=\$result)
     show (resid) (id \$id1) evaluate (\$resid1=\$result)
  
     identity (store1) (all)
  
     for \$id2 in id ( resname CYS and name SG and ( attr store1 > \$id1 ) ) loop dis2
       show (segid) (id \$id2) evaluate (\$segid2=\$result)
       show (resid) (id \$id2) evaluate (\$resid2=\$result)
  
       pick bond (id \$id1) (id \$id2) geometry
  
       if ( \$result <= 2.5 ) then
         evaluate (\$disu=\$disu+1)
         evaluate (\$seg1.\$disu=\$segid1)
         evaluate (\$seg2.\$disu=\$segid2)
         evaluate (\$res1.\$disu=\$resid1) 
         evaluate (\$res2.\$disu=\$resid2)
       end if
     end loop dis2  
   end loop dis1
  
   evaluate (\$counter=1)
   while ( \$counter <= \$disu ) loop disu
     patch disu
       reference=1=(segid \$seg1.\$counter and resid \$res1.\$counter)
       reference=2=(segid \$seg2.\$counter and resid \$res2.\$counter)
     end
     buffer message
       display disulphide added: from \$seg1.\$counter[a4] \$res1.\$counter[a4] to \$seg2.\$counter[a4] \$res2.\$counter[a4]
     end
     evaluate (\$counter=\$counter+1)
   end loop disu
  
   {- patching of RNA to DNA -}
   evaluate (\$counter=0)
   for \$id in id ( tag and ( $DNASELECTION ) ) loop dna
     evaluate (\$counter=\$counter+1)
     show (segid) (id \$id)
     evaluate (\$dna.segid.\$counter=\$result)
     show (resid) (id \$id)
     evaluate (\$dna.resid.\$counter=\$result)
   end loop dna
   evaluate (\$dna.num=\$counter)
  
   evaluate (\$counter=0)
   while (\$counter < \$dna.num) loop dnap
     evaluate (\$counter=\$counter+1)
     patch deox reference=nil=(segid \$dna.segid.\$counter and resid \$dna.resid.\$counter) end
   end loop dnap
  
   identity (store1) (none)  
   identity (store1) ((not known) or hydrogen)
  
   show sum(1) (store1)
   evaluate (\$moving=\$result)
  
   if ( \$moving > 0 ) then
     fix selection=( not(store1) ) end
  
     for \$id in id (tag and byres(store1)) loop avco
  
       show ave(x) (byres(id \$id) and known) evaluate (\$ave_x=\$result)
       show ave(y) (byres(id \$id) and known) evaluate (\$ave_y=\$result)
       show ave(z) (byres(id \$id) and known) evaluate (\$ave_z=\$result)
  
       do (x=\$ave_x) (byres(id \$id) and store1)
       do (y=\$ave_y) (byres(id \$id) and store1)
       do (z=\$ave_z) (byres(id \$id) and store1)
   
     end loop avco 
  
     do (x=x+random(2.0)) (store1)
     do (y=y+random(2.0)) (store1)
     do (z=z+random(2.0)) (store1)
  
     {- start parameter for the side chain building -}
     parameter
       nbonds
         rcon=20. nbxmod=-2 repel=0.9  wmin=0.1 tolerance=1.
         rexp=2 irexp=2 inhibit=0.25
       end
     end
  
     {- Friction coefficient, in 1/ps. -}
     do (fbeta=100) (store1)
  
     evaluate (\$bath=300.0)
     evaluate (\$nstep=500)
     evaluate (\$timestep=0.0005)
  
     do (refy=mass) (store1)
     do (mass=20) (store1)
  
     igroup interaction (store1) (store1 or known) end
  
     {- turn on initial energy terms -}
     flags exclude * include bond angle vdw end
   
     minimize powell nstep=50  nprint=10 end
  
     do (vx=maxwell(\$bath)) (store1)
     do (vy=maxwell(\$bath)) (store1)
     do (vz=maxwell(\$bath)) (store1)
  
     flags exclude vdw include impr end
  
     dynamics cartesian
       nstep=\$nstep
       timestep=\$timestep
       tcoupling=true temperature=\$bath
       nprint=\$nstep
       cmremove=false
     end
  
     flags include vdw end
  
     minimize powell nstep=50 nprint=10 end
  
     do (vx=maxwell(\$bath)) (store1)
     do (vy=maxwell(\$bath)) (store1)
     do (vz=maxwell(\$bath)) (store1)
  
     dynamics cartesian
       nstep=\$nstep
       timestep=\$timestep
       tcoupling=true temperature=\$bath
       nprint=\$nstep
       cmremove=false
     end
  
     parameter
       nbonds
         rcon=2. nbxmod=-3 repel=0.75
       end
     end
  
     minimize powell nstep=100 nprint=25 end
  
     do (vx=maxwell(\$bath)) (store1)
     do (vy=maxwell(\$bath)) (store1)
     do (vz=maxwell(\$bath)) (store1)
  
     dynamics cartesian
       nstep=\$nstep
       timestep=\$timestep
       tcoupling=true temperature=\$bath
       nprint=\$nstep
       cmremove=false
     end
  
     {- turn on all energy terms -}
     flags include dihe ? end
  
     {- set repel to ~vdw radii -}
     parameter
       nbonds
         repel=0.89
       end
     end
  
     minimize powell nstep=500 nprint=50 end
  
     flags exclude * include bond angl impr dihe vdw end
  
     {- return masses to something sensible -}
     do (mass=refy) (store1)
  
     do (vx=maxwell(\$bath)) (store1)
     do (vy=maxwell(\$bath)) (store1)
     do (vz=maxwell(\$bath)) (store1)
  
     dynamics cartesian
       nstep=\$nstep
       timestep=\$timestep
       tcoupling=true temperature=\$bath
       nprint=\$nstep
       cmremove=false
     end
  
     {- some final minimisation -}
     minimize powell
       nstep=500
       drop=40.0
       nprint=50
     end
  
     print thres=0.02 bonds
     print thres=5. angles
   end if

   fix selection=( none ) end
  
   show ave(b) (known and not(store1))
   do (b=\$result) (store1 and (attr b < 0.01))
  
   set echo=false end
   show sum(1) (store1)
   if ( \$result < 100 ) then
     for \$id in id (store1) loop print
       show (segid) (id \$id)
       evaluate (\$segid=\$result)
       show (resname) (id \$id)
       evaluate (\$resname=\$result)
       show (resid) (id \$id)
       evaluate (\$resid=\$result)
       show (name) (id \$id)
       evaluate (\$name=\$result)
       buffer message
         display coordinates built for atom: \$segid[a4] \$resname[a4] \$resid[a4] \$name[a4]
       end 
     end loop print
   else
     buffer message
       display coordinates built for more than 100 hundred atoms
     end
   end if
   set echo=true end
  
   set remarks=reset end
  
   buffer message
     to=remarks
     dump
   end
  
   write structure   output=$psf end  
   write coordinates output=$cns end
  
  ! make table with equivalent protons and swapped protons:
  set display methyls.tbl end
  display do (store1 = 0) (all)
  ident (store9) (bondedto (name h*))
  for \$loopid in id (store9) loop meth
    coor select (bondedto (id \$loopid) and name h*) end
    if (\$select eq 3) then
      display do (store1 = 1) (id \$loopid)
    end if
  end loop meth
  close methyls.tbl end

  @@methyls.tbl

  aria
     analyse_restraints
        equivalent
           initialize
           for \$loopid in id (store1) loop meth
              select (bondedt(id \$loopid) and name h*)
           end loop meth
           for \$loopid in id ((resn phe or resn tyr) and name cd1) loop arom
              select (byres(id \$loopid) and (name hd#))
              select (byres(id \$loopid) and (name he#))
           end loop arom
        end
     end
  end

  
  set display setup_swap_list.tbl end

  display do (q = 0) (all)
  display do (store1 = 0) (all)
  { nomenclature: 
      store1=1 methylene/ nh2
      store1=2 isopropyle
      store1=3 guanidino
  }
  
  display   do (store1 = 2) (resn leu and name cd1)
  display   do (store1 = 2) (resn val and name cg1)
  display   do (store1 = 3) (resn arg and name nh1)
  
  for \$id in id (not store1 and (
    (resn gly and name ha2)
    or (resn ile and name hg12)
    or (resn leu and name hb2)
    or (resn phe and name hb2)
    or (resn pro and (name hb2 or name hg2 or name hd2))
    or (resn met and (name hb2 or name hg2))
    or (resn trp and name hb2)
    or (resn cys and name hb2)
    or (resn ser and name hb2)
    or (resn asn and name hb2)
    or (resn gln and (name hb2 or name hg2))
    or (resn tyr and name hb2)
    or (resn his and name hb2)
    or (resn asp and name hb2)
    or (resn glu and (name hb2 or name hg2))
    or (resn lys and (name hb2 or name hg2 or name hd2 or name he2))
    or (resn arg and (name hb2 or name hg2 or name hd2))))
  loop meth   
     coor sele= (bondedto(bondedto(id \$id)) and name h*) end
     if (\$select = 2) then
       display do (store1 = 1) (id \$id)
     end if
  end loop meth
  
  for \$id in id (not store1 and (resn gln and name he22))
  loop meth   
     coor sele= (bondedto(bondedto(id \$id)) and name h*) end
     if (\$select = 2) then
        display do (store1 = 1) (id \$id)
     end if   
  end loop meth
  
  for \$id in id (not store1 and (resn asn and name hd22))
  loop meth   
     coor sele= (bondedto(bondedto(id \$id)) and name h*) end
     if (\$select = 2) then
        display do (store1 = 1) (id \$id)
     end if   
  end loop meth
  
  for \$id in id (not store1 and (resn arg and (name hh12 or name hh22)))
  loop meth   
     coor sele= (bondedto(bondedto(id \$id)) and name h*) end
     if (\$select = 2) then
        display do (store1 = 1) (id \$id)
     end if   
  end loop meth
  
  close setup_swap_list.tbl end

  stop

EOF

