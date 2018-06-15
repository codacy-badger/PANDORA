
#include <RandomWorld.hxx>

#include <RandomWorldConfig.hxx>
#include <Bug.hxx>
#include <Predator.hxx>
#include <DynamicRaster.hxx>
#include <Point2D.hxx>
#include <GeneralState.hxx>
#include <Scheduler.hxx>
#include <Logger.hxx>

namespace Examples  
{

RandomWorld::RandomWorld(Engine::Config * config, Engine::Scheduler * scheduler ) : World(config, scheduler, false) {}

RandomWorld::~RandomWorld() {}

void RandomWorld::createRasters() {
	const RandomWorldConfig & randomConfig = (const RandomWorldConfig&)getConfig();
	registerDynamicRaster("food", true);
	getDynamicRaster("food").setInitValues(0,100,0);
	setMaxProductionRate(randomConfig._maxFoodProduction);
}

void RandomWorld::createAgents() {
    std::stringstream logName;
	logName << "agents_" << getId();
    const RandomWorldConfig & randomConfig = (const RandomWorldConfig&)getConfig();
	for (int i = 0; i < randomConfig._numBugs; i++) {
		if ((i%getNumTasks()) == getId()) {
			std::ostringstream oss;
			oss << "Bug_" << i;
			float size = Engine::GeneralState::statistics().getNormalDistValue((float)randomConfig._initialBugSizeMean,randomConfig._initialBugSizeSD);
			if (size < 0.0) size = 0.0;
			Bug * bug = new Bug(oss.str(),randomConfig._bugMaxConsumptionRate,(int)size);
			addAgent(bug);
			bug->setRandomPosition();
	        log_INFO(logName.str(), getWallTime() << " new bug: " << bug);
		}
	}
	for (int i = 0; i < 200; i++) {
		if ((i%getNumTasks()) == getId()) {
			std::ostringstream oss;
			oss << "Predator_" << i;
			Predator * predator = new Predator(oss.str());
			addAgent(predator);
			predator->setRandomPosition();
			log_INFO(logName.str(), getWallTime() << " new predator: " << predator);
		}
		
	}
}

void RandomWorld::step() {
	std::stringstream logName;
	logName << "simulation_" << getId();
	log_INFO(logName.str(), getWallTime() << " executing step: " << _step);
	
	if (_step%_config->getSerializeResolution() == 0) {
		_scheduler->serializeRasters(_step);
		_scheduler->serializeAgents(_step);
		log_DEBUG(logName.str(), getWallTime() << " step: " << step_ << " serialization done");
	}
	stepEnvironment();
	log_DEBUG(logName.str(), getWallTime() << " step: " << _step << " has executed step enviroment");
	
	_scheduler->executeAgents();
	_scheduler->removeAgents();
	log_INFO(logName.str(), getWallTime() << " finished step: " << _step);
}

void RandomWorld::stepEnvironment() {
	for(auto index : getBoundaries()) {
		float oldFood = getValue("food",index);
		float foodProduced = Engine::GeneralState::statistics().getUniformDistValue(0,_maxProductionRate);
		setValue("food",index,oldFood + foodProduced);
	}
}

int RandomWorld::getMaxProductionRate() const {
	return _maxProductionRate;
}

void RandomWorld::setMaxProductionRate(const int& maxProductionRate) {
	_maxProductionRate = maxProductionRate;
}


} // namespace Examples
