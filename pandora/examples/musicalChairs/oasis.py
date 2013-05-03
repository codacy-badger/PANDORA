#!/usr/bin/python

import sys
import random
import argparse
import xml.etree.ElementTree

sys.path.append('../../pyPandora/')
sys.path.append('../../')

from pyPandora import Simulation, Agent, World, Point2DInt

def enum(**enums):
	""" converts a sequence of values to an C++ style enum """
	return type('Enum', (), enums)

terrainTypes = enum(ePastures=0, eFields=1)

class OasisConfig():
	_size = 0
	_numSteps = 0

	# farmer config
	_initFarmers = 0
	_farmersStrength = 0.0
	_farmersGrowthRate = 0.0
	_farmersImmigrationRate = 0.0

	_initHerders = 0
	_herdersRelativeStrength = 0.0
	_herdersGrowthRate = 0.0
	_herdersImmigrationRate = 0.0

	def __init__(self):
		return

#	Config.__init__(self)
	
	def deserialize(self, xmlFile):
		tree = xml.etree.ElementTree.parse(xmlFile)
		root = tree.getroot()

		self._size = int(root.find('size').get('value'))
		self._numSteps = int(root.find('numSteps').get('value'))

		agents = root.find('agents')
		farmers = agents.find('farmers')
		self._numFarmers = int(farmers.get('init'))
		self._farmersStrength = float(farmers.get('strength'))
		self._farmersGrowthRate = float(farmers.get('growthRate'))
		self._farmersImmigrationRate = float(farmers.get('immigrationRate'))

		herders = agents.find('herders')
		self._initHerders = int(herders.get('init'))
		self._herdersRelativeStrength = float(herders.get('relativeStrength'))
		self._herdersGrowthRate = float(herders.get('growthRate'))
		self._herdersImmigrationRate = float(herders.get('immigrationRate'))

class OasisAgent(Agent):
	""" Base class for the Musical Chairs model """
	_aggressiveness = 0.0
	_strength = 0.0
	_naturalGrowth = 0.0
	_numChildren = 0

	def __init__(self, id):
		Agent.__init__( self, id)

	def naturalGrowth(self):
		# check natural growth
		randomValue = random.random()
		print 'random value: '+str(randomValue)
		if randomValue >= _naturalGrowth:
			return
		newAgent = duplicateAgent()
		if newAgent == 0:
			return
		self._numChildren += 1
		newAgent._strength = self._strength
		newAgent._aggressiveness = self._aggressiveness

class Herder(OasisAgent):
	def __init__(self, id):
		OasisAgent.__init__( self, id)

	def updateState(self):
		self.naturalGrowth()

	def getNewHerderPosition(self):
		for i in range(getWorld().getSize()-1, 0, -1):
			for j in range(getWorld().getSize()-1, 0, -1):
				possiblePosition = Point2DInt(i,j)
				if getWorld().getValue('herders', possiblePosition)==0:
					return possiblePosition
		return Point2DInt(-1,-1) 

	def duplicateAgent(self):
		newAgent = Herder(_id+str(_self._numChildren))
		newAgent.position = self.getNewHerderPosition()
		# all occupied by farmers
		if(newAgent.position._x == -1):
			return 0
		getWorld().setValue('herders', newAgent.position, 1) 
		getWorld().addAgent(newAgent)
		return newAgent

class Farmer(OasisAgent):
	def __init__(self, id):
		OasisAgent.__init__( self, id)

	def updateState(self):
		self.naturalGrowth()

	def getNewFarmerPosition(self):
		for i in range(0,getWorld().getSize()):
			for j in range(0, getWorld().getSize()):
				possiblePosition = Point2DInt(i,j)
				if getWorld().getValue('farmers', possiblePosition)==0:
					return possiblePosition
		return Point2DInt(-1,-1) 

	def duplicateAgent(self):		
		newAgent = Herder(_id+str(_self._numChildren))
		newAgent.position = self.getNewFarmerPosition()
		# all occupied by farmers
		if(newAgent.position._x == -1):
			return 0
		getWorld().setValue('farmers', newAgent.position, 1) 
		getWorld().addAgent(newAgent)
		return newAgent

	def serialize(self):
		return

class Oasis(World):
	_numFields = 0
	_herdersOut = 0
	_farmersOut = 0
	_aggressions = 0
	_invasions = 0

	_config	= OasisConfig()

	def __init__(self, simulation, config ):
		World.__init__( self, simulation)
		self._config = config

	def createRasters(self):		
		self.registerDynamicRaster("farmers", 1)
		self.registerDynamicRaster("herders", 1)
		self.getDynamicRaster("farmers").setInitValues(0, 1, 0)
		self.getDynamicRaster("herders").setInitValues(0, 1, 0)

	def createAgents(self):
		for i in range (0, self._config._initFarmers):
			newAgent = Farmer('id_'+str(i))
			self.addAgent(newAgent)
			newAgent.setRandomPosition()

		for i in range (0, self._config._initHerders):
			newAgent = Herder('id_'+str(i))
			self.addAgent(newAgent)
			newAgent.setRandomPosition()

	def farmersMigration(self):
		return	
			
	def herdersMigration(self):
		return
	
	def resolveConflicts( self, position ):
		indexOfOpportunity = _numFields / self._config._size*self._config._size
		# just one of each per cell
		herder = getAgent(position, 'Herder').at(0)
		farmer = getAgent(position, 'Farmer').at(0)
		ratioOfStrengths = herder._strength/(herder._strength+farmer._strength)
		incentiveForMigration = 1 - ratioOfStrengths*indexOfOpportunity
		if incentiveForMigration>herder._aggressiveness:
			removeAgent(herder)
			setValue('herders', position, 0)
			_herdersOut += 1

		# invasion attempt
		_aggressions += 1
		randomValue = random.random()
		if herder._aggressiveness > randomValue:
			removeAgent(farmer)
			setValue('farmers', position, 0)
			_invasions += 1
		else:
			removeAgent(herder)
			setValue('herders', position, 0)

	def updateNumFields(self):
		_numFields = 0
		for i in range(0,self._config._size):
			for j in range(0,self._config._size):
				position = Point2DInt(i,j)
				if getValue('farmers', position)==1 :
					_numFields += 1
				
	def checkConflicts(self):
		self.updateNumFields()
		_aggressions = 0
		_invasions = 0
		for i in range(0,self._config._size):
			for j in range(0,self._config._size):
				position = Point2DInt(i,j)
				if getValue('herders', position)==1 and getValue('farmers', position)==1:
					resolveConflicts(position)

	def stepEnvironment(self):
#		self.farmersMigration()
#		self.herdersMigration()
#		self.checkConflicts()
		return

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-x', '--config', default='config.xml', help='config file')
	args = parser.parse_args()
	config = OasisConfig()
	config.deserialize(args.config)

	print('size: '+str(config._size)+' num steps:'+str(config._numSteps))
	mySimulation = Simulation(config._size, config._numSteps)
	oasis = Oasis(mySimulation, config)
	oasis.initialize()
	oasis.run()
 
if __name__ == "__main__":
	main()

