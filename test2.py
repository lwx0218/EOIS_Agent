from langchain.prompts import PromptTemplate
prompt = PromptTemplate.from_template("Answer the following questions as best you can. You have access to the following tools:\n\n{tools}\n\nUse the following format:\n\nQuestion: the input question you must answer\nThought: you should always think about what to do\nAction: the action to take, should be one of [{tool_names}]\nAction Input: the input to the action\nObservation: the result of the action\n... (this Thought/Action/Action Input/Observation can repeat N times)\nThought: I now know the final answer\nFinal Answer: the final answer to the original input question\n\nBegin!\n\nQuestion: {input}\nThought:{agent_scratchpad}")
# print(prompt)


from langchain.agents import AgentExecutor, create_react_agent
from modules.ToolKit.EnterpriseSearch import EnterpriseSearch
from modules.LLM.spark import sparkLLM

llm = sparkLLM(appid="d0667f0b",
            api_key="4cc48b105db2f0e66766de133131f537", 
            api_secret="ODA0Y2IxMGU2ZTJhOTY4Njk0NWFlMWE2",
            spark_url="ws://spark-api.xf-yun.com/v3.1/chat",
            domain="generalv3")
tool = EnterpriseSearch()
agent = create_react_agent(llm, [tool], prompt)
agent_executor = AgentExecutor(agent=agent, tools = [tool], verbose=True)
agent_executor.invoke({"input":"你好，请告诉我交通银行的基本信息"})
# for chunk in agent_executor.stream({"input": "你好，请告诉我交通银行的基本信息"}):
#     print(chunk)
print()