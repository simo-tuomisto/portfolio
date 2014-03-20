import numpy as np
import matplotlib.pyplot as mpl
import sys
from glob import glob
import os.path
import re

if __name__=="__main__":

	cityfile 	= sys.argv[1]
	routefolder	= sys.argv[2]
	
	namereg		= re.compile('.*ntasks\_(?P<ntasks>\d+)-seed\_(?P<seed>\d+)\.route')
	
	routefiles	= glob(os.path.join(routefolder,'*.route'))
			
	cities = np.loadtxt(cityfile, skiprows=9, delimiter=' ').T
	
	x	= cities[0]
	y	= cities[1]
	
	routedict	= dict()
	timedict	= dict()
	
	for route in sorted(routefiles):
		match = namereg.match(os.path.basename(route))
		if match != None:
			groups	= match.groupdict()
			ntasks	= int(groups['ntasks'])
			if not ntasks in routedict:
				routedict[ntasks] = []
				timedict[ntasks] = []
								
			with open(route, 'r') as f:
				lines = f.readlines()
			routeline = lines[-1].strip().replace('  ',' ',1).split()
			try:
				time = float(lines[-3])
				timedict[ntasks].append(time)
			except:
				pass
			
			route = np.asarray(routeline,dtype=int)-1
			
			routedict[ntasks].append(route)
				
	ntasks_arr	= []
	length_arr	= []
	nplots		= 10
	for ntasks, routes in sorted(routedict.items()):
		if nplots > 0:
			figure = mpl.figure(facecolor='white',figsize=(9,6))
		
		length = 0.0
		routelen	= len(routes[0])
		mpl.plot(x[:routelen],y[:routelen],'k*',label='Cities')
		for route,n in zip(routes,xrange(100)):
			routex	= x[route]
			routey	= y[route]
			routex	= np.append(routex, routex[0])
			routey	= np.append(routey, routey[0])
			for i in range(0, len(routex)-1):
				j = np.mod(i+1,len(routex)-1)
				length += np.power(routex[i]-routex[j],2.0)
				length += np.power(routey[i]-routey[j],2.0)
			if nplots > 0:
				mpl.plot(routex,routey)
		length = length/float(len(routes))
		ntasks_arr.append(ntasks)
		length_arr.append(length)
		if nplots > 0:
			mpl.legend()
			mpl.title('Number of tasks: %d, avg(L): %f' % (ntasks,length))
			mpl.savefig(os.path.join(routefolder, 'ntasks_%d.pdf' % ntasks))
			nplots -= 1
	
	ntasks_arr = np.asfarray(ntasks_arr)
	length_arr = np.asfarray(length_arr)
	figure = mpl.figure(facecolor='white',figsize=(9,6))
	mpl.plot(ntasks_arr, length_arr, 'r^')
	mpl.plot(ntasks_arr, length_arr, 'k-')
	mpl.xlabel('Number of tasks')
	mpl.ylabel('Length of best route')
	mpl.savefig(os.path.join(routefolder, 'ntasks_vs_length.pdf'))
	
	time_arr	= []
	for ntasks, times in sorted(timedict.items()):
		if len(times) > 0:
			time = np.average(times)
			time_arr.append(time)
					
	if len(time_arr) == len(ntasks_arr):
		time_arr = np.asfarray(time_arr)
		figure = mpl.figure(facecolor='white',figsize=(9,6))
		mpl.plot(ntasks_arr, time_arr, 'r^')
		mpl.plot(ntasks_arr, time_arr, 'k-')
		mpl.xlabel('Number of tasks')
		mpl.ylabel('Time taken')
		mpl.savefig(os.path.join(routefolder, 'ntasks_vs_time.pdf'))
	
	mpl.show()