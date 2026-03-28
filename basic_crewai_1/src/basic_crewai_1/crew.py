from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

web_search = SerperDevTool()


@CrewBase
class BasicCrewai1:
    @agent
    def data_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["data_analyst"],
            tools=[],
            max_iter=3,
            verbose=True
        )

    @agent
    def policy_strategy_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["policy_strategy_analyst"],
            tools=[web_search],
            max_iter=3,
            verbose=True
        )

    @agent
    def answer_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["answer_writer"],
            max_iter=2,
            verbose=True
        )

    @task
    def gather_data_task(self) -> Task:
        return Task(config=self.tasks_config["gather_data_task"])

    @task
    def interpret_task(self) -> Task:
        return Task(config=self.tasks_config["interpret_task"])

    @task
    def write_answer_task(self) -> Task:
        return Task(config=self.tasks_config["write_answer_task"])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            planning=False,
            verbose=True
        )
