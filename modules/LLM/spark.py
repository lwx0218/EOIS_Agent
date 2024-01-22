from typing import Any, List, Mapping, Optional, Iterator
import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
from urllib.parse import urlparse
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time

import websocket  # 使用websocket_client

from langchain.llms.base import LLM, BaseLLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.schema.output import GenerationChunk
# from langchain_core.language_models.llms import LLM
from langchain_core.language_models.base import LanguageModelInput
from langchain_core.runnables import RunnableConfig, ensure_config
from langchain_core.callbacks import CallbackManager
from langchain_core.load import dumpd
from langchain_core.outputs import LLMResult

from collections import deque
from threading import Thread, Condition

class CallbackToIterator:
    def __init__(self):
        self.queue = deque()
        self.cond = Condition()
        self.finished = False

    def callback(self, result):
        with self.cond:
            self.queue.append(result)
            self.cond.notify()  # Wake up the generator.

    def __iter__(self):
        return self

    def __next__(self):
        with self.cond:
            # Wait for a value to be added to the queue.
            while not self.queue and not self.finished:
                self.cond.wait()
            if not self.queue:
                raise StopIteration()
            return self.queue.popleft()

    def finish(self):
        with self.cond:
            self.finished = True
            self.cond.notify()  # Wake up the generator if it's waiting.

class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, Spark_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(Spark_url).netloc
        self.path = urlparse(Spark_url).path
        self.Spark_url = Spark_url

    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.Spark_url + '?' + urlencode(v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        return url

def gen_params(appid, domain,question):
    """
    通过appid和用户的提问来生成请参数
    """
    data = {
        "header": {
            "app_id": appid,
            "uid": "1234"
        },
        "parameter": {
            "chat": 
            # {
            #     "domain": domain,
            #     "random_threshold": 0.5,
            #     "max_tokens": 2048,
            #     "auditing": "default"
            # }
            {
                "domain": domain,
                "temperature": 0.01,
                # "random_threshold": 0.5,
                "max_tokens": 8192,
                "auditing": "default",
                # "stop": ["Observation:","Observation","\nObservation","\tObservation"],
            }
        },
        "payload": {
            "message": {
                "text": question
            }
        }
    }
    return data

def getText(role,content):
    text =[]
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    text.append(jsoncon)
    return text

def getlength(text):
    length = 0
    for content in text:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length

def checklen(text):
    while (getlength(text) > 8000):
        del text[0]
    return text

class sparkLLM(LLM):
    appid : str = None
    api_key : str = None
    api_secret : str = None
    endpoint_url : str = None
    domain : str = None
    content : str = None
    def __init__(self, appid, api_key, api_secret, spark_url, domain, **kwargs) -> None:
        super().__init__()
        self.appid = appid
        self.api_key = api_key
        self.api_secret = api_secret
        self.endpoint_url = spark_url
        self.domain = domain
        # self.spark_url = "ws://spark-api.xf-yun.com/v3.1/chat"
        # self.domain = "generalv3"

    @property
    def _llm_type(self) -> str:
        return "SparkLLM"
    
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        # _model_kwargs = self.model_kwargs or {}
        _model_kwargs = None
        return {
            **{"endpoint_url": self.endpoint_url},
            **{"model_kwargs": _model_kwargs},
        }

    def _stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
    # called by stream
        input = checklen(getText("user", prompt))

        # 收到websocket错误的处理
        def on_error(ws, error):
            ws.iterator.callback("出现了错误:" + error)

        # 收到websocket关闭的处理
        def on_close(ws,one,two):
            pass

        # 收到websocket连接建立的处理
        def on_open(ws):
            thread.start_new_thread(run, (ws,))

        def run(ws, *args):
            data = json.dumps(gen_params(appid=ws.appid, domain= ws.domain,question=ws.question))
            ws.send(data)

        # 收到websocket消息的处理
        def on_message(ws, message):
            ws.iterator.callback(message)

        wsParam = Ws_Param(self.appid, self.api_key, self.api_secret, self.endpoint_url)
        websocket.enableTrace(False)
        wsUrl = wsParam.create_url()
        ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
        ws.appid = self.appid
        ws.question = input
        ws.domain = self.domain
        # Initialize the CallbackToIterator 
        ws.iterator = CallbackToIterator()
        # Start the WebSocket connection in a separate thread
        thread.start_new_thread(
            ws.run_forever, (), {"sslopt": {"cert_reqs": ssl.CERT_NONE}}
        )
        # Iterate over the CallbackToIterator instance
        total_tokens = 0
        chunk_list = []
        for message in ws.iterator:
            data = json.loads(message)
            code = data["header"]["code"]
            if code != 0:
                ws.close()
                raise Exception(f"请求错误: {code}, {data}")
            else:
                choices = data["payload"]["choices"]
                status = choices["status"]
                content = choices["text"][0]["content"]
                if "usage" in data["payload"]:
                    total_tokens = data["payload"]["usage"]["text"]["total_tokens"]
                if status == 2:
                    ws.iterator.finish()  # Finish the iterator when the status is 2
                    ws.close()

                chunk = GenerationChunk(
                        **{
                        "text": content,
                        "generation_info": {"tokens_usage":total_tokens}
                    }
                )

                # 滑动窗口检查stop
                if len(chunk_list) < 2:
                    chunk_list.append(chunk)
                else:
                    combined_text = ''.join([chunk.text for chunk in chunk_list])
                    if stop[0] in combined_text:
                        index =combined_text.index(stop[0])
                        if index + 1 <= len(chunk_list[0].text):
                        # stop开始出现在第一个chunk
                            chunk_list[0].text = chunk_list[0].text[:index] # 截取stop之前内容
                        chunk_list.pop(1)
                        break
                    yield chunk_list[0]
                    chunk_list.pop(0)
                    chunk_list.append(chunk)
        # 返回剩余chunk
        yield from chunk_list

        
                        
                

    # def stream(
    #     self,
    #     input: LanguageModelInput,
    #     config: Optional[RunnableConfig] = None,
    #     *,
    #     stop: Optional[List[str]] = None,
    #     **kwargs: Any,
    # ) -> Iterator[str]:
    #     # 重写该方法以适应不支持stop的LLM，主动截取
    #     if type(self)._stream == BaseLLM._stream:
    #         # model doesn't implement streaming, so use default implementation
    #         yield self.invoke(input, config=config, stop=stop, **kwargs)
    #     else:
    #         prompt = self._convert_input(input).to_string()
    #         config = ensure_config(config)
    #         params = self.dict()
    #         params["stop"] = stop
    #         params = {**params, **kwargs}
    #         options = {"stop": stop}
    #         callback_manager = CallbackManager.configure(
    #             config.get("callbacks"),
    #             self.callbacks,
    #             self.verbose,
    #             config.get("tags"),
    #             self.tags,
    #             config.get("metadata"),
    #             self.metadata,
    #         )
    #         (run_manager,) = callback_manager.on_llm_start(
    #             dumpd(self),
    #             [prompt],
    #             invocation_params=params,
    #             options=options,
    #             name=config.get("run_name"),
    #             batch_size=1,
    #         )
    #         generation: Optional[GenerationChunk] = None
    #         try:
    #             for chunk in self._stream(
    #                 prompt, stop=stop, run_manager=run_manager, **kwargs
    #             ):
    #                 yield chunk.text
    #                 if generation is None:
    #                     generation = chunk
    #                 else:
    #                     generation += chunk
    #                 # 添加了stop的检查
    #                 stop_tag = False
    #                 for s in stop:
    #                     if s in generation.text:
    #                         index =generation.text.index(s)
    #                         generation.text = generation.text[:index]
    #                         stop_tag = True
    #                         break
    #                 if stop_tag: break
    #             assert generation is not None
    #         except BaseException as e:
    #             run_manager.on_llm_error(
    #                 e,
    #                 response=LLMResult(
    #                     generations=[[generation]] if generation else []
    #                 ),
    #             )
    #             raise e
    #         else:
    #             run_manager.on_llm_end(LLMResult(generations=[[generation]]))

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
    # called by invoke
        input = checklen(getText("user",prompt))
        self.content = ""
        # 收到websocket错误的处理
        def on_error(ws, error):
            print("### error:", error)

        # 收到websocket关闭的处理
        def on_close(ws,one,two):
            print(" ")

        # 收到websocket连接建立的处理
        def on_open(ws):
            thread.start_new_thread(run, (ws,))

        def run(ws, *args):
            data = json.dumps(gen_params(appid=ws.appid, domain= ws.domain,question=ws.question))
            ws.send(data)

        # 收到websocket消息的处理
        def on_message(ws, message):
            # print(message)
            data = json.loads(message)
            code = data['header']['code']
            if code != 0:
                print(f'请求错误: {code}, {data}')
                ws.close()
            else:
                choices = data["payload"]["choices"]
                status = choices["status"]
                self.content += choices["text"][0]["content"]
                if status == 2:
                    ws.close()

        wsParam = Ws_Param(self.appid, self.api_key, self.api_secret, self.endpoint_url)
        websocket.enableTrace(False)
        wsUrl = wsParam.create_url()
        ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
        ws.appid = self.appid
        ws.question = input
        ws.domain = self.domain
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

        return self.content
    
if __name__ == "__main__":
    llm = sparkLLM(appid="d0667f0b",
             api_key="4cc48b105db2f0e66766de133131f537", 
             api_secret="ODA0Y2IxMGU2ZTJhOTY4Njk0NWFlMWE2",
             spark_url="ws://spark-api.xf-yun.com/v3.1/chat",
             domain="generalv3")
    # iter = llm.stream(input="你好")
    # for i in iter:
    #     print(i)
    # print()
    from langchain.globals import set_llm_cache
    import time
    from langchain.cache import InMemoryCache

    set_llm_cache(InMemoryCache())
    a = time.time()
    print(llm.predict("你好，你是？"))
    b = time.time() - a
    print(b)
    print(llm.predict("你好？"))
    
    print(time.time() - a - b)