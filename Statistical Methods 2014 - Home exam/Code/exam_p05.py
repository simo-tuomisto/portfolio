import numpy as np
import matplotlib.pyplot as mpl
from scipy.stats import chisquare
from scipy.optimize import fmin_powell as fmin

def chisq(observed, expected):
	return chisquare(observed[expected>0],expected[expected>0])
	
def getPseudo(background,n_samples):
	back_cum		= np.cumsum(background)/np.sum(background)
	back_pseudo		= np.zeros_like(background)
	for n in np.arange(n_samples):
		random_number 	= np.random.random()
		i				= np.sum(back_cum<random_number)
		back_pseudo[i]	+= 1
	return back_pseudo

measured 		= np.loadtxt('real_mass.dat').T[-1]
back1			= np.loadtxt('MC1_mass.dat').T[-1]
back2			= np.loadtxt('MC2_mass.dat').T[-1]
n			= np.sum(measured)
back_pseudo1	= getPseudo(back1,n)
back_pseudo2	= getPseudo(back2,n)

chi1,p1		= chisq(measured, back1)
chi2,p2		= chisq(measured, back2)

chi_pseudo1,p_pseudo1	= chisq(measured, back_pseudo1)
chi_pseudo2,p_pseudo2	= chisq(measured, back_pseudo2)

print 'Background 1:'
print 'Chi:',chi1,'P-value:',p1
print 'Background 2:'
print 'Chi:',chi2,'P-value:',p2
print 'Background 1 pseudoexperiment:'
print 'Chi:',chi_pseudo1,'P-value:',p_pseudo1
print 'Background 2 pseudoexperiment:'
print 'Chi:',chi_pseudo2,'P-value:',p_pseudo2

a = fmin(lambda x: chisq(measured, x*back1 + (1.0-x)*back2)[0], 0.0, disp=False)

back_optimal						= a*back1+(1-a)*back2
back_pseudo_optimal					= getPseudo(back_optimal,n)

chi_optimal,p_optimal				= chisq(measured, back_optimal)
chi_pseudo_optimal,p_pseudo_optimal	= chisq(measured, back_pseudo_optimal)

print 'Optimal background:'
print 'a:',a
print 'Chi:',chi_optimal,'P-value:',p_optimal
print 'Optimal background pseudoexperiment:'
print 'Chi:',chi_pseudo_optimal,'P-value:',p_pseudo_optimal

mpl.figure(facecolor='white',figsize=(12,9))
mpl.plot(measured,'-b',label='Measured mass')
mpl.plot(back1,'-r',label='Background 1')
mpl.plot(back2,'-g',label='Background 2')
mpl.legend(loc=4)
mpl.savefig('p05_back.pdf')

mpl.figure(facecolor='white',figsize=(12,9))
mpl.plot(measured,'-b',label='Measured mass')
mpl.plot(back_pseudo1,'-r',label='Pseudoexperiment from background 1')
mpl.plot(back_pseudo2,'-g',label='Pseudoexperiment from background 2')
mpl.legend(loc=4)
mpl.savefig('p05_pseudo.pdf')

mpl.figure(facecolor='white',figsize=(12,9))
mpl.plot(measured,'-b',label='Measured mass')
mpl.plot(back_optimal,'-r',label='Optimal background')
mpl.plot(back_pseudo_optimal,'-g',label='Pseudoexperiment from optimal background')
mpl.legend(loc=4)
mpl.savefig('p05_optimal.pdf')

#mpl.show()