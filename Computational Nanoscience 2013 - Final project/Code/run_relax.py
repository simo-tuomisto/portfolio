import subprocess as sp

if __name__=="__main__":
	relaxfmt = """
log	     	cylinder_relax_{0}.log

units		metal
atom_style	atomic
boundary	p p p

lattice		fcc 3.61
region		mybox block -50 50 -50 50 -50 50
create_box	1 mybox
region		mycylinder cylinder z 0 0 {0} EDGE EDGE
create_atoms	1 region mycylinder
mass		1 63.55

pair_style	eam
pair_coeff	1 1 Cu_u3.eam

neighbor	0.3 bin
neigh_modify	every 20 delay 0 check yes

timestep	0.0005

compute		ep all pe/atom
dump		mydump all custom 100 cylinder_{0}.dump type x y z c_ep
dump_modify	mydump append yes

thermo		100
thermo_style	custom step temp pe etotal press vol
thermo_modify 	line one flush yes format 1 "ec %8lu" format float "%20.10g"

fix MYFIX all nve
fix MYTFIX all temp/berendsen 300.0 300.0 0.1

velocity	all create 300.0 87287

run		3000

write_restart cylinder_{0}.restart
"""

	lammps_program	= 'lammps-daily'

	filenamefmt	= "cylinder_relax_{0}.{1}"

	for r in range(5,31,5):
		print 'Running relax for cylinder with %d nm.' % r
		filename 	= filenamefmt.format(r,'in')
		config		= relaxfmt.format(r)
		with open(filename, 'w') as f:
			f.write(config)
		stdout		= filenamefmt.format(r,'stdout')
		
		with open(filename, 'r') as f:
			with open(stdout, 'w') as g:
				cmd2	= sp.call(lammps_program, stdin=f, stdout=g)