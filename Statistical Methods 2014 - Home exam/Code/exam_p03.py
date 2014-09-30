import numpy as np
import matplotlib.pyplot as mpl
from scipy.stats import norm

a_data 	= np.loadtxt('exam_sample_cata.txt').T
b_data 	= np.loadtxt('exam_sample_catb.txt').T
"""
mpl.figure(facecolor='white',figsize=(9,9))
mpl.scatter(a_data[0],a_data[1],c='b',label='Sample a')
mpl.scatter(b_data[0],b_data[1],c='r',label='Sample b')
mpl.xlabel('x1')
mpl.ylabel('x2')
mpl.savefig('p03_samples.pdf')
mpl.legend()
#mpl.savefig('samples.pdf')
"""
a_mean		= np.mean(a_data,axis=1).T
b_mean		= np.mean(b_data,axis=1).T
mean_matrix	= np.matrix(np.power(a_mean - b_mean,2.0))

print 'Sample a mean', str(a_mean)
print 'Sample b mean', str(b_mean)

a_var	= np.cov(a_data)
b_var	= np.cov(b_data)

print 'Sample a covariance matrix: ', str(a_var)
print 'Sample b covariance matrix: ', str(b_var)

var_inv	= np.linalg.inv(np.matrix(a_var + b_var))

c		= np.inner(var_inv, mean_matrix)

print 'Weights c for x3: ', str(c)

c		= c/np.linalg.norm(c)

print 'Weights c (normed): ', str(c)

a_x3	= np.sum(c * a_data,axis=0)
b_x3	= np.sum(c * b_data,axis=0)

n = np.arange(1,len(a_x3)+1)

mpl.figure(facecolor='white',figsize=(9,9))
mpl.plot(n,a_x3, 'ob',label='Sample a')
mpl.plot(n,b_x3, 'or',label='Sample b')
mpl.ylabel('x3')
mpl.xlabel('Event')
mpl.legend()
mpl.savefig('p03_x3.pdf')

a_x3	= np.sort(a_x3)
b_x3	= np.sort(b_x3)

a_cum	= np.cumsum(a_x3)/np.sum(a_x3)
b_cum	= np.cumsum(b_x3)/np.sum(b_x3)

a95 = a_x3[a_cum > 0.95][0]

print 'Rejection limit:', a95 

b_eff = float(len(b_x3[b_x3 > a95]))/len(b_x3)

print 'Sample b efficiency:', b_eff

c_ortho = np.array([ -float(1.0/np.sqrt(1+np.power(c[0]/c[1],2.0))) , float(1.0/np.sqrt(1+np.power(c[1]/c[0],2.0)))])

print 'Vector orthogonal to c: ', c_ortho

x=np.linspace(-0.5,0.5,100)

mpl.figure(facecolor='white',figsize=(9,9))
mpl.scatter(a_data[0],a_data[1],c='b',label='Sample a')
mpl.scatter(b_data[0],b_data[1],c='r',label='Sample b')
mpl.plot(c_ortho[0]*x+c[0]*a95,c_ortho[1]*x + c[1]*a95,'k', label='95% a-rejection line')
mpl.xlabel('x1')
mpl.ylabel('x2')
mpl.legend()
mpl.savefig('p03_rejection.pdf')
#mpl.savefig('samples_w_line.pdf')

x1_measured	= 0.50
x2_measured	= 0.25

a_x1m	= np.mean(a_data[0])
a_x2m	= np.mean(a_data[1])
b_x1m	= np.mean(b_data[0])
b_x2m	= np.mean(b_data[1])
a_x1v	= np.std(a_data[0])
a_x2v	= np.std(a_data[1])
b_x1v	= np.std(b_data[0])
b_x2v	= np.std(b_data[1])

p_ax1	= norm.pdf(x1_measured, a_x1m, a_x1v)
p_ax2	= norm.pdf(x2_measured, a_x2m, a_x2v)
p_bx1	= norm.pdf(x1_measured, b_x1m, b_x1v)
p_bx2	= norm.pdf(x2_measured, b_x2m, b_x2v)

p_a		= p_ax1*p_ax2
p_b		= p_bx1*p_bx2

p_sum	= p_a+p_b

print 'Probability of sample a:',p_a/p_sum
print 'Probability of sample b:',p_b/p_sum

#mpl.show()