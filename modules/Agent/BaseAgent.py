from langchain.llms.base import LLM
from langchain.tools import BaseTool
from typing import List, Sequence

from langchain.agents.agent import AgentExecutor

class BaseAgent:
    def __init__(
            self, 
            model: LLM, 
            toolkit: Sequence[BaseTool]
    ) -> None:

        self.history = []
        self.model = model
        self.toolKit = toolkit

    def predict(
            self,
            question: str
    ) -> str:

        return question
    


if __name__ == "__main__":
    from ..LLM.spark import sparkLLM
    from ..ToolKit import EnterpriseSearch

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
    agent = AgentExecutor()


    agent("请告诉我交通银行的涉诉信息")
