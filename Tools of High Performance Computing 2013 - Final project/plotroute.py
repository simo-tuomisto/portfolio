import numpy as np
import matplotlib.pyplot as mpl
import sys

if __name__=="__main__":

	cityfile	= sys.argv[1]
	routefile 	= sys.argv[2]
	
	with open(routefile, 'r') as f:
		lines = f.readlines()
	
	routeline = lines[-1].strip().replace('  ',' ',1).split()
	
	route = np.asarray(routeline,dtype=int)-1
	
	print route+1
	
	cities = np.loadtxt(cityfile, skiprows=9, delimiter=' ').T
	
	x	= cities[0][route]
	x	= np.append(x, x[0])
	y	= cities[1][route]
	y	= np.append(y, y[0])
	
	fig = mpl.figure(figsize=(12,9), facecolor='white')
	ax	= fig.gca()
	
	ax.plot(x,y,'r*')
	ax.plot(x,y,'k-')
	for city, xcoord, ycoord in zip(route, x, y):
		annotation = '%d' % (city+1)
		#print annotation, xcoord, ycoord
		ax.annotate(annotation, xy=(xcoord,ycoord),xytext=(xcoord+0.01,ycoord+0.01))
	
	print cities[:,:10]
	
	length = 0.0
	for i in range(0, len(x)-1):
		j = np.mod(i+1,len(x)-1)
		length += np.power(x[i]-x[j],2.0)
		length += np.power(y[i]-y[j],2.0)
		print x[i], y[i]
		
	print length
	
	mpl.show()