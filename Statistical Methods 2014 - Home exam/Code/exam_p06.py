import numpy as np
import matplotlib.pyplot as mpl
from scipy.stats import chisquare
from scipy.optimize import fmin_powell as fmin

t = np.asfarray([ 300 , 350 , 400 , 450 , 500 , 550 , 600 , 650 , 700 , 750 ])
N = np.asfarray([ 803000 , 581083 , 429666 , 320016 , 242783 , 188487 , 150737 , 124103 , 105397 , 92748])

def getN(parameters,t_values):
	A, L, B = parameters
	delta_t	= 10.0
	return (2.0*A/L)*np.exp(-L*t_values)*np.sinh(L*delta_t/2.0)+B*delta_t

p = fmin(lambda x: np.sum(np.power(N-getN(x,t),2.0)), np.asfarray([5*N[0],0.1,0.0]), disp=False)

bestdata = getN(p,t)
bestA, bestL, bestB = p

chi2	= chisquare(N, bestdata)[0]

bestA_err = np.abs(bestA-fmin(lambda x: np.power(chi2 - chisquare(N, getN([x, bestL, bestB],t))[0]-1,2.0), bestA, disp=False))
bestL_err = np.abs(bestL-fmin(lambda x: np.power(chi2 - chisquare(N, getN([bestA, x, bestB],t))[0]-1,2.0), bestL, disp=False))
bestB_err = np.abs(bestB-fmin(lambda x: np.power(chi2 - chisquare(N, getN([bestA, bestL, x],t))[0]-1,2.0), bestL, disp=False))

bestT		= np.log(2.0)/bestL
bestT_err	= bestT/bestL*bestL_err

print 'Best A: ', bestA, ' Error:', bestA_err
print 'Best L: ', bestL, ' Error:', bestL_err
print 'Best B: ', bestB, ' Error:', bestB_err
print 'Best Tau: ', bestT, ' Error:', bestT_err

mpl.figure(facecolor='white')
mpl.plot(t, N, 'b^', label='Measured N')
mpl.plot(t, bestdata, 'g-', label='Curve fit')
mpl.legend()
mpl.savefig('p06_fit.pdf')
#mpl.show()