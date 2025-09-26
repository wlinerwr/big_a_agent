
import tushare
import json
import os
import mcp
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv,find_dotenv
from typing import TypedDict,Any



mcp = FastMCP("tushare_mcp_server")

#注意python环境不同，当被客户端启动时使用的是客户端所在的环境
_ = load_dotenv(find_dotenv())

token = os.environ["tushare_token"]

ts = tushare.pro_api(token)




# 权限不够
# @mcp.tool()
def get_stock_basic(exchange:str="",list_statues:str = "L") -> str:
    """
    获取上市股票基本信息（股票列表）
    :param exchange 交易所,SSE上交所 SZSE深交所 BSE北交所,为空是全选
    :param list_status: 上市状态, L上市 D退市 P暂停上市
    :param fields 规定返回的信息样式。
    """
    try:
        respon = ts.stock_basic(exchange=exchange, list_status=list_statues, fields='ts_code,symbol,name,area,industry,list_date')
        #orient控制转化的JSON结构格式，force_ascii控制字符编码.
        return respon.to_json(orient='records',force_ascii=False)
    except Exception as e:
        # 在Agent中调用时，我需要改写JSON的格式或者里面的内容吗？
        # 不需要,MCP协议希望工具返回的是结构化数据
        # mcp响应结构(json)results包括toolCallId，result（api返回的数据）
        # 当Agent调用时：
        # 1.Agent向MCP服务器发送一个带有toolCallId的请求
        # 2.MCP服务器接收请求并执行函数
        # 3.将结果组装成一个符合MCP规范的完整JSON响应，再发送回Agent
        # 思考：在这一过程中MCP协议有什么体现？
        return json.dumps({"error" : str(e)})
    
@mcp.tool()
def get_daily_data(ts_code:str,start_date:str,end_date:str):
    """
    获取指定日期的历史日线
    :param ts_code 标识股票代码
    :param start_date 开始时间
    :param end_date 结束时间
    """
    try:
        respon = ts.daily(ts_code=ts_code,start_date=start_date,end_date=end_date)
        return respon.to_json(orient='records',force_ascii=False)
    except Exception as e:
        return json.dumps({"error" : str(e)})
    
@mcp.tool()
def get_financial_indicator(ts_code:str,period:str="20250101"):
    """
    获取指定股票指定日期的财务指标数据
    :param ts_code:标识股票代码
    :param period:指定的日期
    """
    try:
        respon = ts.fina_indicator(ts_code=ts_code,period=period)
        return respon.to_json(orient='records',force_ascii=False)
    except Exception as e:
        return json.dumps({"error" : str(e)})

@mcp.tool()
def get_stock_company(exchange:str,limit:int="10"):
    """
    获取交易所中上市公司基础信息
    :param exchange:交易所,SSE上交所 SZSE深交所 BSE北交所,为空是全选
    :param limit:返回数据条目的数目
    """
    try:
        respon = ts.stock_company(exchange=exchange,limit=limit)
        return respon.to_json(orient='records',force_ascii=False)
    except Exception as e:
        return json.dumps({"error" : str(e)})


    
#程序执行入口
#当当文件被直接运行时执行代码

if __name__ == "__main__":
    
    #？？？
    mcp.run(transport='stdio')