import subprocess as sp
import os
import numpy as np

if __name__=="__main__":
	stretchfmt = """
log	     	cylinder-stretch-r_{0}-f_{2}-t_{3}.log

units		metal
atom_style	atomic

read_restart cylinder_{0}.restart

change_box	all boundary p p s

region      TOPREG block  -99999 99999   -99999 99999   {1} 99999
region      BOTREG block  -99999 99999   -99999 99999   -99999 -{1}
group		TOPAT region TOPREG
group		BOTAT region BOTREG
variable	TOPSTRESS equal {2}
variable	BOTSTRESS equal -{2}

pair_style	eam
pair_coeff	1 1 Cu_u3.eam

neighbor	0.3 bin
neigh_modify	every 20 delay 0 check yes

timestep	0.0005

compute		ep all pe/atom
compute		st all stress/atom
dump		mydump all custom 1000 cylinder-stretch-r_{0}-f_{2}-t_{3}.dump type x y z c_ep c_st[1] c_st[2] c_st[3] c_st[4] c_st[5] c_st[6] 
dump_modify	mydump append yes

thermo		100
thermo_style	custom step temp pe etotal press vol
thermo_modify 	line one flush yes format 1 "ec %8lu" format float "%20.10g"

fix MYFIX all nve
fix MYTFIX all temp/berendsen 300.0 300.0 0.1
fix MYCMASS all recenter INIT INIT INIT

fix MYTOPFFIX TOPAT addforce 0.0 0.0 v_TOPSTRESS
fix MYBOTFFIX BOTAT addforce 0.0 0.0 v_BOTSTRESS

run {3}
"""

	filenamefmt	= "cylinder-stretch-r_{0}-f_{1}-t_{2}.{3}"

	forces		= [0.001,0.005,0.009,0.013,0.017]
	forcedist	= 100.0
	time		= 100000
	
	lammps_program	= 'lammps-daily'

	#delta		= (lenmult - 1.0)/nsteps
	#stretch		= stretchfmt.format(1.0+delta, 45)

	for r in np.arange(5,31,5):
		for force in forces:
			print 'Running %d timesteps of stretch for cylinder with r=%d nm with f=%f.' % (time,r,force)
			filename 	= filenamefmt.format(r,force,time,'in')
			dumpfile	= filenamefmt.format(r,force,time,'dump')
			if os.path.exists(dumpfile):
				print 'Dumpfile exists, will not run.'
			else:
				config		= stretchfmt.format(r, forcedist, force, time)
				with open(filename, 'w') as f:
					f.write(config)
					#for i in range(0,nsteps):
				#		f.write(stretch)
				stdout		= filenamefmt.format(r,force,time,'stdout')
		
				with open(filename, 'r') as f:
					with open(stdout, 'w') as g:
						cmd2	= sp.call(lammps_program, stdin=f, stdout=g)
