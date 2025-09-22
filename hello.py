import os
import time
import threading
from dotenv import load_dotenv,find_dotenv
from openai import OpenAI

_ = load_dotenv(find_dotenv())
key = os.environ["deepseek_API_KEY"]
response = None
#思考完成标志
over = False

client = OpenAI(api_key= key, base_url="https://api.siliconflow.cn/v1")


def get_response(content:str):
    global response , over
    response = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
    messages=[
        {"role" : "user", "content" : f"{content}"}
    ],
    stream=False
    )
    over = True


content = input("------------------------请输入你的问题-----------------------------\n")

thread = threading.Thread(target=get_response,args=(content,))
thread.start()

print()
for i in range(101):
    if over:
        break
    print(f"\r思考中 {i}s", end='', flush=True)
    time.sleep(1)
print("\n思考完成")

#保证子线程完成
thread.join()
print(response.choices[0].message.content)


