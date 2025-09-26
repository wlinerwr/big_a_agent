from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.tools import BaseTool
from langchain_core.messages import BaseMessage
from langchain_core.messages import HumanMessage

from langgraph.graph import StateGraph,START,END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages

from langchain_deepseek import ChatDeepSeek

from langchain_mcp_adapters.client import MultiServerMCPClient

from dotenv import load_dotenv,find_dotenv
from IPython.display import Image, display
import asyncio
import os

#创建StateGraph
class StockState(TypedDict):
    #Annotated类型注解工具,为类型添加的元数据
    #list类型，指定更新规则
    #add_messages ： 追加模式
    #add ： 相加
    #空 ： 覆盖
    messages : Annotated[list,add_messages]


#加载配置文件
_ = load_dotenv(find_dotenv())
deepseek_key = os.environ["deepseek_API_KEY"]

message_history:list[BaseMessage] = []

#配置MCP服务器
async def initialize_mcp_server() -> any:
    try:
        client = MultiServerMCPClient(
            {
                "tushare_mcp_server" : {
                    "command" : "D:/Big_Agent/.venv/Scripts/python.exe",
                    "args" : ["D:/Big_Agent/tushare_mcp_server.py"],
                    "transport" : "stdio",
                }
            }
        )
        tool = await client.get_tools()
        #print(f"服务器可用工具：{tool}")
        return tool
    except Exception as e:
        print(f"服务器初始化错误    {e}")




def create_agent_graph(tool : list[BaseTool]) -> any:
    try:
        #初始化DeepSeek
        llm = ChatDeepSeek(
            model="deepseek-chat",
            api_key=deepseek_key
        )
        llm_with_tool  = llm.bind_tools(tools=tool)
    except:
        print("大模型初始化错误")


    def chatnode(state:StockState):
        """该用于与用户进行交互聊天"""
        #调用 DeepSeek 大模型生成回复
        #返回大模型回答结果，节点结束后，LangGraph内部自动处理状态合并
        print(f"-------"*10 + "聊天节点调用" +"-------"*10)
        print(state["messages"])
        return{"messages":[llm_with_tool.invoke(state["messages"])]}

    try:
        tool_node = ToolNode(tool)
    except Exception as e:
        print(f"工具节点构建失败 : {e}")

    #边的判断条件
    def should_continue(state: StockState):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END

    #构建图
    graph = StateGraph(StockState)
    graph.add_node("chat",chatnode)
    graph.add_node("tool",tool_node)
    graph.add_edge(START,"chat")
    graph.add_conditional_edges(
        "chat",
        should_continue,
        {
            "tools" : "tool",
            END : END
        }
    )
    graph.add_edge("tool","chat")
    app = graph.compile()
    # try:
    #     png_data =app.get_graph().draw_mermaid_png()
    #     with open("agent_graph.png", "wb") as f:
    #         f.write(png_data)
    #     print("图的可视化已保存为 agent_graph.png")
    # except Exception as e:
    #     print(f"图生成错误: {e}")

    return app

    


#提交输入
async def stream_graph_updates(user_input:HumanMessage ,app:any):
    #？？？？
    try:
        async for event in app.astream({"messages": user_input}):
            #items()方法获得键，值
            for node_name,value in event.items():
                ai_message = value["messages"][-1]
                message_history.append(ai_message)
                #检查value中是否有messages字段
                if node_name == "chat" and "messages" in value:
                    if ai_message.tool_calls:
                        #需要tool节点
                        print()
                        for tool_call in ai_message.tool_calls:
                            print(f"DeeSeek请求调用工具 : {tool_call['name']}")
                            print(f" -参数 : {tool_call['args']}")
                    else:
                        print(f"DeepSeek: {ai_message.content}")
                if node_name == "tool" and "messages" in value:
                    for tool_messages in value["messages"]:
                        print("----工具执行成----")
                        print(f"工具名称 : {tool_messages.name}")
                        print("----------------------------------------")
    except Exception as e:
        print(f"输入错误:{e}")



#交互   
async def main():
    #没有await到的是一个“协程对象”
    tool = await initialize_mcp_server()
    app = create_agent_graph(tool=tool)
    print("="*50)
    while True:
        try:
            user_input = input("用户:")
            if user_input.lower() in ["quit","exit","q"]:
                print("再见")
                break
            message_history.append(HumanMessage(content=user_input))
            #每次调用会创建全新messages列表，导致多次时交互messages只能记录一次交互的信息
            await stream_graph_updates(user_input,app)
        except Exception as e:
            print("main错误 : " + e )
            break


if __name__ == "__main__":
    asyncio.run(main())
