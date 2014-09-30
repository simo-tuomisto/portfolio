import numpy as np
import matplotlib.pyplot as mpl
import sys
from glob import glob
import re
import os

if __name__=="__main__":

	
	cut			= np.loadtxt('cutfile.csv', skiprows=1, delimiter=';')
	
	cutdict	= dict()
	for r,f,cut_d in cut:
		if r not in cutdict:
			cutdict[r] 	= dict()
		cutdict[r][f]	= cut_d
	
	dumps		= glob('*.dump')
	
	dumpreg		= re.compile('.*-r_(?P<r>.+)-f_(?P<f>.+)-t_(?P<t>.+).dump')
	
	dumparray = []
	for dump in dumps:
		match 	= dumpreg.match(dump)
		groups	= match.groupdict()
		r		= float(groups['r'])
		if r in cutdict:
			f		= float(groups['f'])
			if f in cutdict[r]:
				dumparray.append([r,f,cutdict[r][f], dump])
	
	for r,f,d,dumpfile in sorted(dumparray):
		print 'Working with %s' % dumpfile
		strain 	= []
		stress	= []
		with open(dumpfile, 'r') as f:
			while True:
				try:
					f.readline()
					timestep = int(f.readline())
					if (timestep/1000 == d):
						break
					f.readline()
					natoms = int(f.readline())
					f.readline()
					xlimits = map(float, f.readline().split())
					ylimits = map(float, f.readline().split())
					zlimits = map(float, f.readline().split())
					f.readline()
					data = []
					for i in xrange(0,natoms):
						data.append(f.readline().split())
					data = np.asfarray(data)
					z_stress = np.abs(data[:,-4])
					stress.append(np.average(z_stress))
					strain.append(zlimits[1]-zlimits[0])
				except:
					break
		#print strain
		strain = np.asfarray(strain)
		stress = np.asfarray(stress)
		filename = os.path.splitext(dumpfile)[0]
		np.save(filename+'_strain.npy', strain)
		np.save(filename+'_stress.npy', stress)
		#mpl.plot(stress,strain,'*')
		#pl.show()
		#break