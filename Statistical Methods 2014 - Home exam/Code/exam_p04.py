import numpy as np
import matplotlib.pyplot as mpl
from scipy.optimize import fmin_powell as fmin
from scipy.odr import *
from scipy.stats import chi2

t 		= np.asfarray([ 352 , 701 , 1048 , 1398 , 1751 , 2099 , 2446 , 2805 ])

t_err	= np.asfarray([ 5 , 9 , 9 , 9 , 9 , 15 , 15 , 15 ])

dT 		= np.asfarray([ 10.0 , 19.7 , 30.2 , 40.4 , 49.9 , 60.5 , 70.4 , 80.0 ])

dT_err	= np.asfarray([ 0.1 , 0.2 , 0.2 , 0.2 , 0.3 , 0.3 , 0.4 , 0.4 ])

U		= 12
I		= 10
m		= 1000.0

RCFbound	= 2.0/(np.sum(np.power(m/(t_err*U*I),2.0)*(np.power(dT,2.0)+np.power(dT_err,2.0))))

def t_value_odr(C,delta_T):
	U		= 12
	I		= 10
	m		= 1000.0
	return (m*delta_T*C[0])/(U*I)
model	= Model(t_value_odr)
data	= RealData(dT, t, sx=dT_err, sy=t_err)

odrfit	= ODR(data, model, beta0=[1.0])

odrfit.set_job(fit_type=2)
output1	= odrfit.run()
C_val1	= output1.beta[0]
chisq1	= output1.sum_square
pval1	= chi2.cdf(chisq1,1)
C_err1	= output1.sd_beta[0]

odrfit.set_job(fit_type=0)
output2	= odrfit.run()
C_val2	= output2.beta[0]
chisq2	= output2.sum_square
pval2	= chi2.cdf(chisq2,1)
C_err2	= output2.sd_beta[0]

# I wrote the commented sections of code to make sure the odrfit matches with least squares code written by me. It does.
"""
def t_value(C,delta_T):
	U		= 12
	I		= 10
	m		= 1000.0
	return (m*delta_T*C)/(U*I)
	
def chisquare(t_obs, sigma_t, C, delta_T):
	t_exp	= t_value(C,delta_T)
	return	np.sum(np.power((t_obs-t_exp)/sigma_t, 2.0))
C_val_old, chisq_old = fmin(lambda x: chisquare(t, t_err, x, dT), np.asfarray([1.0]), full_output=True, disp=False)[0:2]
C_err_old = np.abs(C_val_old - fmin(lambda x: np.power(chisquare(t, t_err, x, dT)-chisq_old-1,2.0), np.asfarray([C_val_old]),disp=False))

print 'Difference between manual least squares minimization and ODR-packages:',C_val_old-C_val1
"""

print 'Least squares with t-errors only:'
print 'C:',C_val1, ' sigma_C:', C_err1,' Chi2:', chisq1, ' P-value:',pval1
print 'Least squares with both errors:'
print 'C:',C_val2, ' sigma_C:', C_err2,' Chi2:', chisq2, ' P-value:',pval2
print 'RFC-bound for std:',np.sqrt(RCFbound)
