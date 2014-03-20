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

	population 	= 1000
	seed 		= 0
	steps		= 10000
	printstep	= 100
	mrate		= 50
	mnumber		= 2
	mprob		= 0.25
	cities		= int(sys.argv[1])
	output		= sys.argv[2]
	header		= fmt.format(population, seed, steps, printstep, mrate, mnumber, mprob, cities)
	
	coords		= np.random.rand(cities,2)
	
	np.savetxt(output, coords, delimiter=' ', comments='', header=header)