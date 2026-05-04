from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class TaxAdvisor():
    """TaxAdvisor crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def tax_corporate_advisor(self) -> Agent:
        return Agent(
            config=self.agents_config['tax_corporate_advisor'],
            verbose=True
        )

    @task
    def compliance_impact_analysis(self) -> Task:
        return Task(
            config=self.tasks_config['compliance_impact_analysis'],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
