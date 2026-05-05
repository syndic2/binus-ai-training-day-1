from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import FileReadTool

from pydantic import BaseModel

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

class InsightItem(BaseModel):
    insight: str
    indicator: str

class OutputTextAnalyzer(BaseModel):
    insights: list[InsightItem]

@CrewBase
class FileAnalyzer():
    """FileAnalyzer crew"""

    agents: list[BaseAgent]
    tasks: list[Task]
    file_read_tool = FileReadTool()
        
    @agent
    def file_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['file_analyzer'], # type: ignore[index]
            verbose=True,
            tools=[self.file_read_tool]
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def file_analyzer_task(self) -> Task:
        return Task(
            config=self.tasks_config['file_analyzer_task'], # type: ignore[index]
            output_json=OutputTextAnalyzer
        )

    @crew
    def crew(self) -> Crew:
        """Creates the FileAnalyzer crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
