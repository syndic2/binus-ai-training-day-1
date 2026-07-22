from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from src.crew_ai_flow_trial.tools.helmet_detection_tool import HelmetDetectionTool
from src.crew_ai_flow_trial.tools.save_to_db_tool import SaveToDbTool

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

from pydantic import BaseModel
from typing import Optional

class SafetyDetectionOutput(BaseModel):
    head: Optional[int] = None
    helmet: Optional[int] = None
    person: Optional[int] = None
    message: Optional[str] = None

@CrewBase
class SafetyDetector():
    """SafetyDetector crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def helmet_detector(self) -> Agent:
        return Agent(
            config=self.agents_config['helmet_detector'], # type: ignore[index]
            verbose=True,
            tools=[HelmetDetectionTool()]
        )

    @agent
    def helmet_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['helmet_analyzer'], # type: ignore[index]
            verbose=True,
            tools=[SaveToDbTool()]
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def helmet_detection_task(self) -> Task:
        return Task(
            config=self.tasks_config['helmet_detection_task'], # type: ignore[index]
        )

    @task
    def helmet_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['helmet_analysis_task'], # type: ignore[index]
            output_json=SafetyDetectionOutput
        )

    @crew
    def crew(self) -> Crew:
        """Creates the SafetyDetector crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
