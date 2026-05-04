from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class TaxResearcher():
    """TaxResearcher crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def tax_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['tax_researcher'],
            verbose=True
        )

    @task
    def research_tax_updates(self) -> Task:
        return Task(
            config=self.tasks_config['research_tax_updates'],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
