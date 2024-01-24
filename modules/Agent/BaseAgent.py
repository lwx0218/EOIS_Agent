from langchain.llms.base import LLM
from langchain.tools import BaseTool
from typing import List, Sequence
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from pydantic import BaseModel, PrivateAttr

class BaseAgent(AgentExecutor):
    _history : List[str] = PrivateAttr()
    _model : LLM = PrivateAttr()
    _toolkit: Sequence[BaseTool] = PrivateAttr()
    def __init__(
        self, 
        model: LLM, 
        toolkit: Sequence[BaseTool],
        prompt: PromptTemplate
    ) -> None:
        agent = create_react_agent(model, toolkit, prompt)
        self._history = []
        self._model = model
        self._toolkit = toolkit 
        super().__init__(
            agent = agent, 
            tools = toolkit,
            verbose = True,
            )

    def predict(
            self,
            question: str
    ) -> str:
        return self.invoke({"input":question})
    

from modules.LLM.spark import sparkLLM
# from ..spark import sparkLLM
from modules.ToolKit.EnterpriseSearch import EnterpriseSearch
if __name__ == "__main__":
    prompt = PromptTemplate.from_template("Answer the following questions as best you can. You have access to the following tools:\n\n{tools}\n\nUse the following format:\n\nQuestion: the input question you must answer\nThought: you should always think about what to do\nAction: the action to take, should be one of [{tool_names}]\nAction Input: the input to the action\nObservation: the result of the action\n... (this Thought/Action/Action Input/Observation can repeat N times)\nThought: I now know the final answer\nFinal Answer: the final answer to the original input question\n\nBegin!\n\nQuestion: {input}\nThought:{agent_scratchpad}")
    llm = sparkLLM(appid="d0667f0b",
                api_key="4cc48b105db2f0e66766de133131f537", 
                api_secret="ODA0Y2IxMGU2ZTJhOTY4Njk0NWFlMWE2",
                spark_url="ws://spark-api.xf-yun.com/v3.1/chat",
                domain="generalv3")
    toolkit = [EnterpriseSearch()]
    agent_executor = BaseAgent(llm,toolkit,prompt)
    # deprecated
    '''agent = initialize_agent(
        EnterpriseSearch(),
        sparkLLM(
            appid="d0667f0b",
            api_key="4cc48b105db2f0e66766de133131f537", 
            api_secret="ODA0Y2IxMGU2ZTJhOTY4Njk0NWFlMWE2",
            spark_url="ws://spark-api.xf-yun.com/v3.1/chat",
            domain="generalv3"),
        agent="zero-shot-react-description",
        verbose=True,
        max_iterations=5,
        handle_parsing_errors="""格式可能有误，请确保格式和顺序为Thought:\\nAction:\\nAction Input:\\nObservation:\\nThought:\\nFinal Answer:\\n,你只需要补全剩余缺失的部分。""",
        #  handle_parsing_errors=parse_errors,
        #handle_parsing_errors=True,
        return_intermediate_steps=True,
    )'''

    # TODO - New method to initialize the agent
    agent_executor.predict("你好，请告诉我交通银行的基本信息")
    # agent = AgentExecutor()


    # agent("请告诉我交通银行的涉诉信息")
