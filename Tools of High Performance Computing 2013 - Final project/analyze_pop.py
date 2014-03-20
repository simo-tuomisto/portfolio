import numpy as np
import matplotlib.pyplot as mpl
import sys
from glob import glob
import os.path
import re

if __name__=="__main__":

	cityfile 	= sys.argv[1]
	routefolder	= sys.argv[2]
	
	namereg		= re.compile('pop\_(?P<pop>\d+)-seed\_(?P<seed>\d+)\.route')
	
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
			pop	= int(groups['pop'])
			if not pop in routedict:
				routedict[pop] = []
				timedict[pop] = []
								
			with open(route, 'r') as f:
				lines = f.readlines()
			routeline = lines[-1].strip().replace('  ',' ',1).split()
			try:
				time = float(lines[-3])
				timedict[pop].append(time)
			except:
				pass
			
			route = np.asarray(routeline,dtype=int)-1
			
			routedict[pop].append(route)
							
	pop_arr		= []
	length_arr	= []
	nplots		= 1
	for pop, routes in sorted(routedict.items()):
		if nplots > 0:
			figure = mpl.figure(facecolor='white',figsize=(12,9))
		
		routelen	= len(routes[0])
		if nplots > 0:
			mpl.plot(x[:routelen],y[:routelen],'k*',label='Cities')
		length = 0.0
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
		length_arr.append(length)
		pop_arr.append(pop)
		if nplots > 0:
			mpl.legend()
			mpl.title('Population per task: %d, avg(L): %f' % (pop,length))
			mpl.savefig(os.path.join(routefolder, 'pop_%d.pdf' % pop))
			nplots -= 1
	
	pop_arr = np.asfarray(pop_arr)
	length_arr = np.asfarray(length_arr)
	figure = mpl.figure(facecolor='white',figsize=(12,9))
	mpl.plot(pop_arr, length_arr, 'r^')
	mpl.plot(pop_arr, length_arr, 'k-')
	mpl.xlabel('Population')
	mpl.ylabel('Length of best route')
	mpl.savefig(os.path.join(routefolder, 'pop_vs_length.pdf'))
	
	time_arr	= []
	for pop, times in sorted(timedict.items()):
		if len(times)>0:
			time = np.average(times)
			time_arr.append(time)
		
	if len(time_arr) > 0:
		time_arr = np.asfarray(time_arr)
		figure = mpl.figure(facecolor='white',figsize=(9,6))
		mpl.plot(pop_arr, time_arr, 'r^')
		mpl.plot(pop_arr, time_arr, 'k-')
		mpl.xlabel('Population')
		mpl.ylabel('Time taken')
		mpl.savefig(os.path.join(routefolder, 'pop_vs_time.pdf'))
		
	mpl.show()