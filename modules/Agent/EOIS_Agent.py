#TODO 集成BaseAgent的初始化及基础功能，开发具体场景的子Agent

from modules.Agent.BaseAgent import BaseAgent
from langchain.llms.base import LLM
from langchain.tools import BaseTool
from typing import List, Sequence
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent
from pydantic import BaseModel, PrivateAttr
import json 

class EOIS_agent(BaseAgent):

    def __init__(        
        self, 
        model: LLM, 
        toolkit: Sequence[BaseTool],
        ):
        prompt = PromptTemplate.from_template("尽力回答问题，你有以下工具可以使用:\n\n{tools}\n\n参照格式来回答问题，格式和顺序需为:\n\nQuestion: 你必须回答的内容\nThought: 每次行动前你都应该时刻思考怎么做然后说出来\nAction: 你要采取的行动，应该是[{tool_names}]其中之一\nAction Input: the input to the action\nObservation:由我根据你的输入调用API得到\nThought:我现在得到了最终答案\nFinal Answer: 对于原始问题的最终答案\n\n开始!\n\n提问: {input}\nThought:{agent_scratchpad}")
        super().__init__(
            model = model,
            toolkit = toolkit, 
            prompt = prompt)

    def predict(
            self,
            question: str
    ) -> str:
        history = json.dumps(self._history, indent=4, ensure_ascii=False)
        pre_search = self._model._call(
            prompt="下面是一段聊天记录:\n" +
            history +    
            f"""\n针对问题:{question}\n在聊天记录里寻找答案，如果不包含答案，你只需要返回'No'；否则返回问题的答案。""")
        
        if pre_search == 'No':
            history_summary = self._model._call(
                input = "为下面的内容写一段简要的总结,如果没有提供有效内容，直接返回'无':\n" + history
            )
            result = self.invoke({"input":question})
            self._history.append({"question": question,
                                "result": result})
            return result
        else : 
            return pre_search


from modules.LLM.spark import sparkLLM
# from ..spark import sparkLLM
from modules.ToolKit.EnterpriseSearch import EnterpriseSearch
if __name__=='__main__':
    print(1)
    llm = sparkLLM(appid="d0667f0b",
                api_key="4cc48b105db2f0e66766de133131f537", 
                api_secret="ODA0Y2IxMGU2ZTJhOTY4Njk0NWFlMWE2",
                spark_url="ws://spark-api.xf-yun.com/v3.1/chat",
                domain="generalv3")
    toolkit = [EnterpriseSearch()]
    eAgent = EOIS_agent(llm,toolkit)
    eAgent.predict("你好，请告诉我交通银行的基本信息")

