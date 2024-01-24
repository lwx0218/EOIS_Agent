import asyncio
from langchain.prompts import PromptTemplate
from langchain import hub
prompt = hub.pull("hwchase17/react")
print()
async def process_chat():

    prompt = PromptTemplate.from_template("尽力回答问题，你有以下工具可以使用:\n\n{tools}\n\n参照格式来回答问题，格式和顺序需为:\n\nQuestion: 你必须回答的内容\nThought: 每次行动前你都应该时刻思考怎么做然后说出来\nAction: 你要采取的行动，应该是[{tool_names}]其中之一\nAction Input: the input to the action\nObservation:由我根据你的输入调用API得到\nThought:我现在得到了最终答案\nFinal Answer: 对于原始问题的最终答案\n\n开始!\n\n提问: {input}\nThought:{agent_scratchpad}")
    # print(prompt)


    from langchain.agents import AgentExecutor, create_react_agent
    from modules.ToolKit.EnterpriseSearch import EnterpriseSearch
    from modules.LLM.spark import sparkLLM
    from langchain.callbacks.streaming_stdout_final_only import (
        FinalStreamingStdOutCallbackHandler,
    )
    from langchain_core.runnables import RunnableParallel, RunnablePassthrough
    llm = sparkLLM(appid="d0667f0b",
                api_key="4cc48b105db2f0e66766de133131f537", 
                api_secret="ODA0Y2IxMGU2ZTJhOTY4Njk0NWFlMWE2",
                spark_url="ws://spark-api.xf-yun.com/v3.1/chat",
                domain="generalv3",
                streaming=True)
    tool = EnterpriseSearch()
    agent = create_react_agent(llm, [tool], prompt)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools = [tool], 
        verbose=True,
        handle_parsing_errors="格式可能有误，请确保格式和顺序为Thought:\\nAction:\\nAction Input:\\nObservation:\\nThought:\\nFinal Answer:\\n,你只需要补全剩余缺失的部分。",
        )
    
    path_status = {}
    async for chunk in agent_executor.astream_log(
        {"input": "你好，请告诉我交通银行的基本信息"},
    ):
        for op in chunk.ops:
            if op["op"] == "add":
                if op["path"] not in path_status:
                    path_status[op["path"]] = op["value"]
                else:
                    path_status[op["path"]] += op["value"]
        print(op["path"])
        print(path_status.get(op["path"]))
        print("----")

asyncio.run(process_chat())