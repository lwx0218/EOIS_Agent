from operator import itemgetter

from langchain.agents import AgentExecutor, tool
from langchain.agents.output_parsers import XMLAgentOutputParser
from modules.LLM.spark import sparkLLM

model = sparkLLM(appid="d0667f0b",
            api_key="4cc48b105db2f0e66766de133131f537", 
            api_secret="ODA0Y2IxMGU2ZTJhOTY4Njk0NWFlMWE2",
            spark_url="ws://spark-api.xf-yun.com/v3.1/chat",
            domain="generalv3")

@tool
def search(query: str) -> str:
    """Search things about current events."""
    return "32 degrees"

tool_list = [search]

from langchain import hub
# Get the prompt to use - you can modify this!
prompt = hub.pull("hwchase17/xml-agent-convo")

def convert_intermediate_steps(intermediate_steps):
    log = ""
    for action, observation in intermediate_steps:
        log += (
            f"<tool>{action.tool}</tool><tool_input>{action.tool_input}"
            f"</tool_input><observation>{observation}</observation>"
        )
    return log

def convert_tools(tools):
    return "\n".join([f"{tool.name}: {tool.description}" for tool in tools])

agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: convert_intermediate_steps(
            x["intermediate_steps"]
        ),
    }
    | prompt.partial(tools=convert_tools(tool_list))
    | model.bind(stop=["</tool_input>", "</final_answer>"])
    | XMLAgentOutputParser()
)
agent_executor = AgentExecutor(agent=agent, tools=tool_list, verbose=True)
agent_executor.invoke({"input": "whats the weather in New york?"})