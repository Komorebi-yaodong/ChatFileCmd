import asyncio
from openai import AsyncOpenAI
import os
from FileTransform import file_transform
import ChatFileConfig
import json
import shutil


config = ChatFileConfig.Config("./config.json")
config.get_init()
storage = []

## ChatGPT参数设置

client = AsyncOpenAI(
    base_url = config.base_url,
    api_key = config.api_key,
)

# 发送请求给 OpenAI GPT
async def chatmd(message,dialogue_history,model=config.model,temperature=config.temperature,max_tokens=config.max_tokens):
    # 将当前消息添加到对话历史中
    dialogue_history.append(message)
    # 发送请求给 OpenAI GPT
    response = await client.chat.completions.create(
        model=model,
        messages=dialogue_history,
        temperature=temperature, # 控制模型输出的随机程度
        max_tokens=max_tokens,  # 控制生成回复的最大长度
        stream=True, # 是否是流式生成
    )

    print("\nGPT>> ",end="")
    assistant_message = ""
    async for part in response:
        w = part.choices[0].delta.content or ""
        assistant_message += w
        print(w,end="")
    print("\n")
    dialogue_history.append({'role':'assistant','content':assistant_message})


## 让GPT读取文章
async def gpt_read_content(content,dialogue_file):

    ## 获得对话历史
    if os.path.exists(dialogue_file):
        with open(dialogue_file, 'r', encoding='utf-8') as f:
            dialogue_history = json.load(f)
        # 将读文章指令发送给他
        end_message = "文章已发送完毕，接下来我将提出一些与文章相关的问题，请根据内容以markdown格式进行回答，我的第一个问题是'Summarize the main content of the article.'"
        end_message = {'role':'user','content':end_message}
        await chatmd(end_message,dialogue_history)
    else:
        if content is None:
            print(f"not exists {dialogue_file}")
        dialogue_history = [
            {'role':'system','content':config.sys_content}
        ]

        ## 字符串切分
        def ContentSplit(string,length):
            return [string[i:i+length] for i in range(0, len(string), length)]

        contents = ContentSplit(content,1000) # 分段内容
        pages = len(contents) # 分段数

        ## 分段输入
        # start
        start_message = f"我现在会将文章的内容分 {pages} 部分发送给你。请确保你已经准备好接收，接收到文章发送完毕的指令后，请准备回答我的问题。"
        dialogue_history.append({'role':'user','content':start_message})
        # 文章
        for i in range(pages):
            content_message = {'role':'user','content':contents[i]}
            dialogue_history.append(content_message)
        # end
        end_message = "文章已发送完毕，接下来我将提出一些与文章相关的问题，请你使用中文，根据内容以markdown格式进行回复，我的第一个问题是'Summarize the main content of the article.'"
        end_message = {'role':'user','content':end_message}
        await chatmd(end_message,dialogue_history)

        ## 保存阅读会话
        with open(dialogue_file,"w",encoding="utf-8") as f:
            json.dump(dialogue_history,f)
    return dialogue_history


## 交流循环
async def main_loop(file_path):    
    print("##SYS: 正在处理文件...")
    content,dialogue_file,floder_name = file_transform(file_path)
    print(floder_name.center(75,'='))
    print("##SYS: 正在分析文件...")
    dialogue_history = await gpt_read_content(content,dialogue_file)

    while True:
        user_input = input("User: ")
        if user_input == "quit":
            return True
        message = {'role':'user','content':user_input.strip()}
        await chatmd(message,dialogue_history)


async def main_loop2(floder_name,dialogue_file):
    print(floder_name.center(75,'='))
    print("##SYS: 正在分析文件...")
    dialogue_history = await gpt_read_content(None,dialogue_file)

    while True:
        user_input = input("Usr>> ")
        if user_input == "quit":
            return True
        message = {'role':'user','content':user_input.strip()}
        await chatmd(message,dialogue_history)


def get_dir(path):
    return os.listdir(path)


async def main():
    while True:
        storage = get_dir(config.data_path)
        user_input = input("\n##SYS: 请输入指令(ls, edit, del <FloderName>, <FloderName>, <FilePath>):\n\nUsr>> ").strip().lstrip()
        if user_input == "ls":  
            print(*storage)
        elif user_input in storage:
            dialogue_file = config.data_path + "/" + user_input + "/dialogue.json"
            await main_loop2(user_input,dialogue_file)
        elif user_input[0:3] == "del":
            floder = user_input[3:]
            del_path = config.data_path + '/' + floder.strip().lstrip()
            print(f"##SYS: you will delete {del_path}")
            if os.path.exists(del_path):
                shutil.rmtree(del_path)
            else:
                print("\n##SYS: Wrong FloderName...")
        elif user_input == "edit":
            print(" Edit(enter to pass) ".center(75,'='))
            with open("./config.json",'r',encoding="utf-8") as f:
                config_ = json.load(f)
                url_base = input(f"##SYS: url_base({config_['base_url']}):").strip().lstrip()
                if url_base != "":
                    config_['base_url'] = url_base
                api_key = input(f"##SYS: api_key({config_['api_key']}):").strip().lstrip()
                if api_key != "":
                    config_['api_key'] = api_key
                model = input(f"##SYS: model({config_['model']}):").strip().lstrip()
                if model != "":
                    config_['model'] = model
            with open("./config.json",'w',encoding="utf-8") as f:
                json.dump(config_,f,ensure_ascii = False)
            config.get_init()
        else:
            if os.path.exists(user_input):
                await main_loop(user_input)
            else:
                print("\n##SYS: Wrong file path...")


if __name__ == "__main__":
    asyncio.run(main())