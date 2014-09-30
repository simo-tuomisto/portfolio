import numpy as np
import matplotlib.pyplot as mpl
from matplotlib.ticker import NullFormatter
import sys
from glob import glob
import re
import os

if __name__=="__main__":

	# Plot these ranges
	plotranges = {
	5.0	:	[0.009	,	0.011],
	10.0:	[0.007	,	0.011],
	15.0:	[0.005	,	0.010],
	20.0:	[0.005	,	0.010],
	25.0:	[0.005	,	0.010],
	30.0:	[0.005	,	0.010]
	}
	
	colormap_f={
	0.005 	: 'b',
	0.006	: 'c',
	0.007	: 'g',
	0.008	: 'y',
	0.009	: 'r',
	0.010	: 'm'
	}
	
	colormap_r={
	5 	: 'b',
	10	: 'c',
	15	: 'g',
	20	: 'y',
	25	: 'r',
	30	: 'm'
	}

	strainreg	= re.compile('.*-r_(?P<r>.+)-f_(?P<f>.+)-t_(?P<t>.+)_strain.npy')
	
	strainfiles = glob('*_strain.npy')
	
	avglen = 3
	
	rdict = dict()
	
	for strainfile in strainfiles:
		match	= strainreg.match(strainfile)
		if match != None:
			stressfile = strainfile[:-10] + 'stress.npy'
			if os.path.exists(stressfile):
				groups 		= match.groupdict()
				r			= float(groups['r'])
				if r not in rdict:
					rdict[r] = []
				f			= float(groups['f'])
				t			= int(groups['t'])
				straindata	= np.load(strainfile)
				stressdata	= np.load(stressfile)
				rdict[r].append([f,t,straindata,stressdata])
				
	measured_data	= []
				
	for r,dataarrays in rdict.items():
		
		if r not in plotranges:
			continue
		
		lowlimit 	= plotranges[r][0]
		highlimit 	= plotranges[r][1]
		
		fig1 = mpl.figure(facecolor='white',figsize=(12,9))
		fig2 = mpl.figure(facecolor='white',figsize=(12,9))
		fig3 = mpl.figure(facecolor='white',figsize=(12,9))
		for dataarray in dataarrays:
			f,t,straindata,stressdata = dataarray
			stressdata = stressdata/(np.pi*np.power(r,2))
			if ((f<lowlimit) or (f>highlimit)):
				continue
			avgstress	= np.zeros_like(stressdata)
			for i in np.arange(avglen,len(stressdata)-avglen-1):
				avgstress[i] = np.average(stressdata[i-avglen:i+avglen+1])
			#mpl.loglog(straindata, stressdata)
			stressmax	= np.amax(stressdata)
			strain = (straindata - straindata[0])/straindata[0]
			strainmax	= np.amax(strain)
			strainrate	= strainmax/len(strain)
			measured_data.append([r,f,stressmax,strainmax,strainrate])
			mpl.figure(fig1.number)
			mpl.plot(strain[avglen:-avglen-1], avgstress[avglen:-avglen-1], label='f=%f' % f, color=colormap_f.get(f,'k'))

			mpl.figure(fig2.number)
			mpl.plot(0.5*np.arange(0, len(strain)),strain, label='f=%f' % f, color=colormap_f.get(f,'k'))
			
			if (f == 0.008):
				mpl.figure(fig3.number)
				t = 0.5*np.arange(avglen, len(avgstress)+avglen)
				mpl.plot(t[avgstress>0],avgstress[avgstress>0],label='f=%f' % f, color=colormap_f.get(f,'k'))
		mpl.figure(fig1.number)
		mpl.title('r=%d' % int(r))
		mpl.xlabel('strain')
		mpl.ylabel('stress')
		mpl.gca().yaxis.set_major_formatter(NullFormatter())
		mpl.legend(loc=1)
		mpl.savefig('strain_vs_stress-r_%d.pdf' % int(r))
		
		mpl.figure(fig2.number)
		mpl.title('r=%d' % int(r))
		mpl.xlabel('time')
		mpl.ylabel('strain')
		#mpl.gca().yaxis.set_major_formatter(NullFormatter())
		mpl.legend(loc=3)
		mpl.savefig('time_vs_strain-r_%d.pdf' % int(r))
		
		mpl.figure(fig3.number)
		mpl.title('r=%d' % int(r))
		mpl.xlabel('time')
		mpl.ylabel('strain')
		mpl.gca().yaxis.set_major_formatter(NullFormatter())
		#mpl.legend(loc=3)
		mpl.savefig('time_vs_stress-r_%d.pdf' % int(r))
		#break
		
	measured_data = np.asfarray(measured_data)
	
	
	mpl.figure(facecolor='white',figsize=(12,9))
	for f in np.unique(measured_data[:,1]):
		r = measured_data[measured_data[:,1] == f,0]
		stressmax = measured_data[measured_data[:,1] == f,2]
		if (f==0.009):
			fit 	= np.polyfit(np.log(r), np.log(stressmax), deg=1)
			fitr 	= r
		mpl.plot(r,stressmax,'^', color=colormap_f.get(f,'k'),label='f=%f' % f)
		mpl.plot(r,stressmax,linestyle='--', color=colormap_f.get(f,'k'))
	mpl.plot(fitr,np.exp(np.polyval(fit,np.log(fitr))), label='Fit with exponent %f' % fit[0])
	mpl.xlabel('r')
	mpl.ylabel('Maximum stress')
	mpl.legend(loc=1)
	#mpl.gca().yaxis.set_major_formatter(NullFormatter())
	mpl.savefig('r_vs_stressmax.pdf')
	mpl.figure(facecolor='white',figsize=(12,9))
	
	for f in np.unique(measured_data[:,1]):
		r = measured_data[measured_data[:,1] == f,0]
		stressmax = measured_data[measured_data[:,1] == f,2]
		mpl.loglog(r,stressmax,'^', color=colormap_f.get(f,'k'),label='f=%f' % f)
		mpl.loglog(r,stressmax,linestyle='--', color=colormap_f.get(f,'k'))
	mpl.xlabel('r')
	mpl.ylabel('Maximum stress')
	mpl.legend(loc=4)
	mpl.gca().yaxis.set_major_formatter(NullFormatter())
	mpl.savefig('r_vs_stressmax_loglog.pdf')
	
	mpl.figure(facecolor='white',figsize=(12,9))
	for r in np.unique(measured_data[:,0]):
		f = measured_data[measured_data[:,0] == r,1]
		stressmax = measured_data[measured_data[:,0] == r,2]
		mpl.plot(f,stressmax,'^', color=colormap_r.get(r,'k'),label='r=%d' % r)
		mpl.plot(f,stressmax,linestyle='--', color=colormap_r.get(r,'k'))
		mpl.xlabel('f')
		mpl.ylabel('Maximum stress')
	mpl.gca().yaxis.set_major_formatter(NullFormatter())
	mpl.legend(loc=4)
	mpl.savefig('f_vs_stressmax.pdf')
	
	mpl.figure(facecolor='white',figsize=(12,9))
	for f in np.unique(measured_data[:,1]):
		r = measured_data[measured_data[:,1] == f,0]
		strainmax = measured_data[measured_data[:,1] == f,3]
		mpl.plot(r,strainmax,'^', color=colormap_f.get(f,'k'),label='f=%f' % f)
		mpl.plot(r,strainmax,linestyle='--', color=colormap_f.get(f,'k'))
	mpl.xlabel('r')
	mpl.ylabel('Strain at the time of failure')
	mpl.legend(loc=0)
	#mpl.gca().yaxis.set_major_formatter(NullFormatter())
	mpl.savefig('r_vs_strainmax.pdf')
	
	mpl.figure(facecolor='white',figsize=(12,9))
	for r in np.unique(measured_data[:,0]):
		f = measured_data[measured_data[:,0] == r,1]
		strainmax = measured_data[measured_data[:,0] == r,3]
		mpl.plot(f,strainmax,'^', color=colormap_r.get(r,'k'),label='r=%d' % r)
		mpl.plot(f,strainmax,linestyle='--', color=colormap_r.get(r,'k'))
		mpl.xlabel('f')
		mpl.ylabel('Strain at the time of failure')
	#mpl.gca().yaxis.set_major_formatter(NullFormatter())
	mpl.legend(loc=0)
	mpl.savefig('f_vs_strainmax.pdf')
	
	mpl.figure(facecolor='white',figsize=(12,9))
	for f in np.unique(measured_data[:,1]):
		r = measured_data[measured_data[:,1] == f,0]
		strainrate = measured_data[measured_data[:,1] == f,4]
		if (f==0.010):
			fit 	= np.polyfit(np.log(r), np.log(strainrate), deg=1)
			fitr 	= r
		mpl.plot(r,strainrate,'^', color=colormap_f.get(f,'k'),label='f=%f' % f)
		mpl.plot(r,strainrate,linestyle='--', color=colormap_f.get(f,'k'))
	mpl.plot(fitr,np.exp(np.polyval(fit,np.log(fitr))), label='Fit with exponent %f' % fit[0])
	mpl.xlabel('r')
	mpl.ylabel('Strain rate')
	mpl.legend(loc=0)
	mpl.gca().yaxis.set_major_formatter(NullFormatter())
	mpl.savefig('r_vs_strainrate.pdf')
	
	mpl.figure(facecolor='white',figsize=(12,9))
	for r in np.unique(measured_data[:,0]):
		f = measured_data[measured_data[:,0] == r,1]
		strainrate = measured_data[measured_data[:,0] == r,4]
		mpl.plot(f,strainrate,'^', color=colormap_r.get(r,'k'),label='r=%d' % r)
		mpl.plot(f,strainrate,linestyle='--', color=colormap_r.get(r,'k'))
		mpl.xlabel('f')
		mpl.ylabel('Strain rate')
	mpl.gca().yaxis.set_major_formatter(NullFormatter())
	mpl.legend(loc=3)
	mpl.savefig('f_vs_strainrate.pdf')
	