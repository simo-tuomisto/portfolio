import numpy as np
import matplotlib.pyplot as mpl
import sys

if __name__=="__main__":

	fmt="""
{0} # population per task
{1} # seed
{2} # steps
{3} # printstep
{4} # migration rate
{5} # migration number
{6} # mutation probability
{7} # cities
"""

	population 	= 2000
	seed 		= 0
	steps		= 100000
	printstep	= 1000
	mrate		= 50
	mnumber		= 2
	mprob		= 0.25
	cities		= int(sys.argv[1])
	
	header		= fmt.format(population, seed, steps, printstep, mrate, mnumber, mprob, cities)
	
	# Create square
	coords		= 2*np.random.rand(cities,2)-1
	
	rand		= np.random.rand(cities)
	
	coords[rand<0.5,0]=np.ceil(coords[rand<0.5,0])
	coords[rand>0.5,1]=np.ceil(coords[rand>0.5,1])
	
	coords[coords==0] = -1
		
	np.savetxt('square.cities', coords, delimiter=' ', comments='', header=header)
	
	print coords.shape
	
	# Create circle
	
	rand		= 2*np.pi*np.random.rand(cities)
	coords		= np.asfarray([np.cos(rand), np.sin(rand)]).T
		
	np.savetxt('circle.cities', coords, delimiter=' ', comments='', header=header)