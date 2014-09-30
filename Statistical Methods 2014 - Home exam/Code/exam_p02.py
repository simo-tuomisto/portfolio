import numpy as np
import string
import random
import matplotlib.pyplot as mpl

class Passenger:

	def __init__(self, rowNumber, seatLetter):
		self.rowNumber 	= float(rowNumber)
		self.seatLetter = seatLetter
		self.hasWaited	= False
	
	def checkPosition(self, position):
		return position == self.rowNumber
	
	def __repr__(self):
		return 'Passenger %d%s' % (int(self.rowNumber), self.seatLetter)
	
class Plane:

	def __init__(self, rows, aisleTime=20, seatTime=0, walkSpeed=0.5):
		self.rows		= rows
		self.aisle		= dict()
		self.seated		= dict()
		self.aisleTime	= aisleTime
		self.seatTime	= seatTime
		self.walkSpeed	= walkSpeed
		self.positions	= np.arange(-15.0,rows+walkSpeed,walkSpeed)[::-1]
		self.wait		= np.zeros_like(self.positions)
		self.time		= 0
		self.times		= np.zeros(rows)
		
	def movePassengers(self):
		
		for index in np.arange(0,self.positions.shape[0]):
			position = self.positions[index]
			if self.wait[index] > 0:
				self.wait[index] -= 1
				if self.wait[index] > 0:
					continue
			if position in self.aisle:
				passenger = self.aisle[position]
				if passenger.checkPosition(position):
					if not passenger.hasWaited:
						if position not in self.seated:
							self.seated[position] = []
						self.seated[position].append(passenger.seatLetter)
						self.wait[index] = self.aisleTime
						if (passenger.seatLetter == 'A' and 'C' in self.seated[position]) or (passenger.seatLetter == 'F' and 'D' in self.seated[position]):
							self.wait[index] += self.seatTime
						passenger.hasWaited = True
					else:
						self.times[position-1] = self.times[position-1] + self.time - passenger.time
						del self.aisle[position]
				elif position+self.walkSpeed not in self.aisle:
					self.aisle[position+self.walkSpeed] = self.aisle.pop(position)
		self.time += 1
		
	def addPassenger(self, passenger):
		if self.positions[-1] not in self.aisle:
			passenger.time = self.time
			self.aisle[self.positions[-1]] = passenger
			return True
		else:
			return False
		
class Simulator:

	def __init__(self, rows=25, aisleTime=10, seatTime=0):
		self.rows		= rows
		self.aisleTime	= aisleTime
		self.seatTime	= seatTime
		
	def getPassengers(self):
		passengers	= dict()
		for seating in ['A','C','D','F']:
			passlist = []
			for row in np.arange(1,self.rows+1):
				passlist.append(Passenger(row, seating))
			passengers[seating] = passlist
		return passengers
	
	def simulateOutsideIn(self, verbose=0):
		passengers	= self.getPassengers()
		passengers1	= passengers['A'] + passengers['F']
		passengers2	= passengers['C'] + passengers['D']
		passengers	= random.sample(passengers1,2*self.rows) + random.sample(passengers2,2*self.rows)
		return self.simulate(passengers,verbose)
		
	def simulateRandom(self, verbose=0):
		passengers	= self.getPassengers()
		passengers	= passengers['A'] + passengers['C'] + passengers['D'] + passengers['F']
		passengers	= random.sample(passengers,4*self.rows)
		return self.simulate(passengers,verbose)
		
	def simulate(self,passengers,verbose):
		plane 		= Plane(self.rows, self.aisleTime, self.seatTime)
		for passenger in passengers:
			added 	= False
			while not added:
				added 	= plane.addPassenger(passenger)
				if verbose >= 2:
					self.printSituation(plane)
				plane.movePassengers()
		while len(plane.aisle) > 0:
			if verbose >= 2:
				self.printSituation(plane)
			plane.movePassengers()
			
		if verbose >= 2:
			self.printSituation(plane)
		if verbose >= 1:
			print plane.seated
			#self.printSituation(plane)
		return plane.times, plane.time
		
	def printSituation(self, plane):
		pos = plane.positions
		aisle 	= []
		for key in sorted(plane.aisle.keys()):
			aisle.append('%s : %s' % (str(key) , repr(plane.aisle[key])))
		aisle = '{ ' + string.join(aisle,' , ') + ' }'
		wait	= []
		for position, waittime in zip(pos[plane.wait > 0], plane.wait[plane.wait > 0]):
			wait.append('%s : %s' % (str(position) , str(waittime)))
		wait = '{ ' + string.join(wait,' , ') + ' }'
		
		print plane.time,aisle,wait,plane.seated
		
if __name__=="__main__":
	sim 		= Simulator(rows=25,seatTime=10,aisleTime=20)
	nsamples	= 50
	# Times contains individual passenger times
	times1 		= []
	# Time contains overall time taken
	time1 		= []
	for i in range(1,nsamples+1):
		print 'Simulating Outside-In %d' % i
		times,time = sim.simulateOutsideIn(verbose=0)
		times1.append(times)
		time1.append(time)
	times1		= np.asfarray(times1)
	times_avg1	= np.average(times1,axis=0)
	time_avg1	= np.average(time1,axis=0)
	time_std1	= np.std(time1,axis=0)
	
	times2 		= []
	time2 		= []
	for i in range(1,nsamples+1):
		print 'Simulating Random %d' % i
		times,time = sim.simulateRandom(verbose=0)
		times2.append(times)
		time2.append(time)
	times2		= np.asfarray(times2)
	times_avg2	= np.average(times2,axis=0)
	time_avg2	= np.average(time2,axis=0)
	time_std2	= np.std(time2,axis=0)
	
	print 'Outside-In boarding:'
	print 'Average time taken:',time_avg1,' Std:',time_std1
	print 'Random boarding:'
	print 'Average time taken:',time_avg2,' Std:',time_std2
	
	bins = np.linspace(np.amin(time1),np.amax(time2),25)
	
	timehist1 = np.histogram(time1, bins=bins)[0]
	timehist2 = np.histogram(time2, bins=bins)[0]
	
	mpl.figure(facecolor='white', figsize=(12,9))
	mpl.plot(bins[:-1], timehist1,'b^',label='Outside-In boarding')
	mpl.plot(bins[:-1], timehist1,'b-')
	mpl.plot(bins[:-1], timehist2,'r^',label='Random boarding')
	mpl.plot(bins[:-1], timehist2,'r-')
	mpl.xlabel('t')
	mpl.ylabel('N')
	mpl.legend(loc=4)
	mpl.savefig('p02_distributions.pdf')
	#mpl.show()
		