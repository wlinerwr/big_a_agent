
import tushare
import json
import os
import mcp
from datetime import datetime
from zoneinfo import ZoneInfo
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv,find_dotenv
from typing import TypedDict,Any



mcp = FastMCP("tushare_mcp_server")

#注意python环境不同，当被客户端启动时使用的是客户端所在的环境
_ = load_dotenv(find_dotenv())

token = os.environ["tushare_token1"]

#创建代表北京时区对象
shanghai_tz = ZoneInfo("Asia/Shanghai")

ts = tushare.pro_api(token)





@mcp.tool()
def get_stock_basic(exchange:str="",list_statues:str = "L",name:str="",limit:int="2",fields:str="ts_code,symbol,name,area,industry,list_date") -> str:
    """
    调用工具可以获取获取上市股票基本信息.
    参数输入说明:
    :param exchange 交易所, 可选值有:SSE上交所 SZSE深交所 BSE北交所,为空是全选,当用户未指定时使用默认值
    :param list_status: 上市状态, 可选值有： L上市 D退市 P暂停上市,当用户未指定时使用默认值
    :param name:股票名字 传入的参入示例: "平安银行" ,为空是不指定.当用户需要获取由股票名所指定股票的时，可以使用该参数获取股票信息。其他情况使用使用默认值
    :param limit : 获取返回数据条目的数目,当用户未指定时使用默认值,值最大不能超过10
    :param fields :规定返回的信息样式,可选字符串有:
        ts_code:TS股票代码,是数据接口中的唯一标识。
        symbol:股票代码.
        name:股票简称.
        area:公司注册的地域.
        industry:所属行业.
        fullname:股票全称.
        enname:公司的英文全称。
        cnspell:股票名称的中文拼音缩写.
        market:市场类型.
        exchange:交易所代码.
        curr_type:交易货币.
        list_status:上市状态。
        list_date:上市日期.
        delist_date:退市日期，
        is_hs:是否为沪深港通标的。
        act_name:实际控制人名称。
        act_ent_type:实际控制人企业性质。
        传入参数示例："ts_code,symbol,name,area,industry,list_date"
        当用户没有明确指定返回的信息样式时使用默认的值，当默认的值没有用户需要的信息时在默认值后追加字符串，比如:
        "ts_code,symbol,name,area,industry,list_date,delist_date"   在默认值后追加退市日期.
        返回结果说明:
        1.结果正常
        2.待定
    """
    try:
        respon = ts.stock_basic(exchange=exchange,limit=limit,name=name ,list_status=list_statues, fields=fields)
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





# @mcp.tool()
# def get_stk_premarket()





@mcp.tool()
def get_daily_data(ts_code:str,trade_date:str,start_date:str="",end_date:str="",limit:int="2",fields:str="ts_code,trade_date,vol,amount"):
    """
    获取指定日期的历史日线
    参数输入说明:
    :param ts_code 股票代码
        说明:当ts_code未指定时(传入参数为空),会查寻规定日期中的所有股票相关的数据
    :param trade_date:交易日期  
    :param start_date 开始时间  
    :param end_date 结束时间
        时间参数输入格式:YYYYMMDD格式 比如20180120
        说明:若用户未指定时间,使用当天作为交易日期。开始时间与结束时间使用默认参数,查询当天的全部历史.
        也可以使用该方式查询指定日期的历史日线
    :param limit : 获取返回数据条目的数目,当用户未指定时使用默认值,值最大不能超过10
    :param fields :规定返回的信息样式,可选字符串有:
        ts_code:股票代码 
        trade_date:交易日期
        open:开盘价
        high:最高价
        low:最低价
        close:收盘价
        pre_close:昨收价
        change:涨跌额
        pct_chg:涨跌幅
        vol:成交量 (单位:手) 
        amount:成交额(单位：千元)
        传入参数示例："ts_code,trade_date,vol,amount"
        当用户没有明确指定返回的信息样式时使用默认的值，当默认的值没有用户需要的信息时在默认值后追加字符串，比如:
        "ts_code,trade_date,vol,amount,open"   在默认值后追加开盘价.
        返回结果说明:
        1.结果正常
        2.返回空值 ("[]"): 所查询的记录不存在.
        3.待定

    """
    try:
        respon = ts.daily(ts_code=ts_code,trade_date=trade_date,start_date=start_date,end_date=end_date,limit=limit,fields=fields)
        return respon.to_json(orient='records',force_ascii=False)
    except Exception as e:
        return json.dumps({"error" : str(e)})





@mcp.tool()
def get_financial_indicator(ts_code:str,period:str="20250101"):
    """
    获取指定股票指定日期的财务指标数据
    :param ts_code:标识股票代码
    :param period:指定日期
    """
    try:
        respon = ts.fina_indicator(ts_code=ts_code,period=period)
        return respon.to_json(orient='records',force_ascii=False)
    except Exception as e:
        return json.dumps({"error" : str(e)})





@mcp.tool()
def get_stock_company(ts_code:str,exchange:str,limit:int="5",fields:str="ts_code,chairman,manager,secretary,reg_capital,setup_date,province"):
    """
    获取交易所中上市公司基础信息
    :param ts_code:标识股票代码 精确查找时使用该参数,其他情况都为空
    :param exchange:交易所,可选参数 SSE上交所 SZSE深交所 BSE北交所,为空是全选
    :param limit:返回数据条目的数目
    :param fields :规定返回的信息样式,可选字符串有:
        ts_code:股票代码
        com_name:公司全称
        com_id:统一社会信用代码
        exchange:交易所代码
        chairman:法人代表
        manager:总经理
        secretary:董秘
        reg_capital:注册资本(万元)
        setup_date:注册日期 (格式: 'YYYYMMDD')
        province:所在省份
        city:所在城市
        introduction:公司介绍
        website:公司主页
        email:电子邮件
        office:办公室(可能为空)
        employees:员工人数
        main_business:主要业务及产品(可能为空)
        business_scope:经营范围(可能为空)
        当用户没有明确指定返回的信息样式时使用默认的值，当默认的值没有用户需要的信息时在默认值后追加字符串，比如:
        "s_code,chairman,manager,secretary,reg_capital,setup_date,province,website"   在默认值后追加开盘价.
        返回结果说明:
        1.结果正常(参数的返回值部分可能为空,代表这该公司暂时没有对应的信息。)
    """
    try:
        respon = ts.stock_company(ts_code=ts_code,exchange=exchange,limit=limit)
        return respon.to_json(orient='records',force_ascii=False)
    except Exception as e:
        return json.dumps({"error" : str(e)})

@mcp.tool()
def get_current_time():
    """
    获取当前系统的时间
    输入说明:
    当用户未指定时区时使用北京时区,用户指定其他时区时使用北京时区，并说明只能返回北京时区的当前时间。
    返回结果说明:
    只返回北京时区的当前时间
    示例:2023-09-20 10:27:21,表示2023年9月20日10时27分21秒
    """
    try:
        return datetime.now(shanghai_tz)
    except Exception as e:
        return json.dumps({"error" : str(e)})




    
#程序执行入口
#当当文件被直接运行时执行代码

if __name__ == "__main__":
    
    #？？？
    mcp.run(transport='stdio')