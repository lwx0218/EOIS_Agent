# EOIS_Agent
 AI Agent for retrieval information system  
 
ChatAgent/  
├── app/	  
│   ├── __init__.py  
│   └── routes/  
│       ├── __init__.py  
│       └── router.py  
├── memory/	 	            #[存储模块] 当下考虑用Redis，也可用文件、cache、ES、database  
│   ├── __init__.py  
│   └── recoder.py		        #用于存储和读取历史数据，提供 cache,对应原先 ChatAgent\modules\models\ChatAgent\ChatAgent.py 里的class ChatRecordExecutor  
├── modules/     #[CoT模块]   整个CoT链路在modules里完成
│   ├── __init__.py  
│   └── LLM/		    #[LLM模块]  将接入的LLM_API，对齐langChain的LLM框架。（OPENAI的LLM可以直接AK接入，其他的OPENAPI的LLM需要一定的改造）
│   │   ├── __init__.py                 #[LLM]模块，来自langchain.base的Class LLM，由其他子类LLM继承，例如：Class SparkLLM(LLM)，主要提供LLM的接口访问（stream/block）
│   │   ├── langchainLLM.py      #待确定  
│   │   ├── spark.py                   #星火LLM  
│   │   └── qwen.py                   #千问LLM  
│   └── Agent/		    #[Agent模块]  
│   │   ├── __init__.py  
│   │   ├── baseAgent.py  	    #[baseAgent]模块，由其他子类Agent继承,代表不同场景下的agent（agent的流式返回待确定），参考langchain.agent的AgentExecutor  
│   │   └── eoisAgent.py            # 针对 外数查 场景下的Agent  
│   └── ToolKit/		    #[Toolkit模块]，子类继承langchain.tools的Class BaseTool，例如：Class enterpriseSearch(basetool)  
│   │   ├── __init__.py  
│   │   ├── enterpriseSearch.py                                 #企业查询  
│   │   └── enterpriseLitigationInquiry.py                  #企业涉诉  
│   └── other/                             #其他辅助功能，如OCR，语音识别等  
├── config/  
│   ├── __init__.py  
│   └── config.py                        #用于处理配置信息  
└── main.py  # 初始化modules的agent并开始CoT