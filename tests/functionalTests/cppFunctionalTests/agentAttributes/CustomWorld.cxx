
#include <CustomWorld.hxx>
#include <CustomAgent.hxx>
#include <Simulation.hxx>

namespace Test 
{

CustomWorld::CustomWorld( const Engine::Simulation & simulation, Engine::Scheduler * scheduler) : World(simulation, scheduler)
{
}

CustomWorld::~CustomWorld()
{
}

void CustomWorld::createAgents()
{
    // 100 agents with random values
	for(int i=0; i<100; i++)
	{
		std::ostringstream oss;
		oss << "CustomAgent_" << i;
		CustomAgent * newAgent = new CustomAgent(oss.str());
        addAgent(newAgent);
        newAgent->setRandomPosition();
        std::stringstream oss2;
        oss2 << "string attribute: " << i;
		newAgent->setStringAttribute(oss2.str());
		newAgent->setIntAttribute(i);
		newAgent->setFloatAttribute(float(i)/100.0f);
	}
}

} // namespace Test
