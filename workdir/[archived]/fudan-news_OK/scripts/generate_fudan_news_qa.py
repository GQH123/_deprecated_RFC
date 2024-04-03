# %%
import unicodedata

from openai import OpenAI

API_KEY = 'sk-jwx9HLq3fDya9Sh4140eFf5cC4D94d4c80963229Ad93018b'

client = OpenAI(
    api_key=API_KEY,
    base_url="https://lonlie.plus7.plus/v1"
)

# %%
import os
import json
import random
from tqdm import tqdm
from datetime import datetime


version = 'v4'
datapath = f'../filtered_news'
n_qa = 1
n_resp = 10


def get_qa_from_openai():
    news_contents = {}
    jsons = [file for file in os.listdir(datapath) if file.endswith('.json') and '_qa' not in file]
    # random.shuffle(jsons)
    for news in jsons:
        news_name = news.split('.')[0]
        news_contents[news_name] = json.load(open(os.path.join(datapath, news)))
    id = 1
    for name, news in tqdm(news_contents.items()):
        if os.path.exists(os.path.join(datapath, f'{name}_qa.json')):
            # print(f'{name}_qa.json exists, skip...')
            continue
        news_body = news['body']
        
        user_prompt_versions = {
            'v1': "请针对如下新闻文本，提出五个有意义的、相关的问题，并给出相应的回答。每组问答格式如下：\n问：{问题}\n答：{回答}\n不要编号。\n新闻如下：\n",
            'v2': "请针对如下新闻文本，提出五个有意义的、相关的问题以及相应回答。这些问题应该包含必要的新闻原文背景，使得在不提供新闻文本时，也能得到同样的回答。每组问答格式如下：\n问：{问题}\n答：{回答}\n不要编号。\n新闻如下：\n",
            'v3': "请针对如下新闻文本，提出五个具体问题，每个问题都要详尽给出必要背景（如时间、地点、事件、活动名称、相关人物等），并给出每个问题的相应回答。每组问答格式如下：\n问：{带有详细背景的问题}\n答：{回答}\n不要编号。\n新闻如下：\n",
            'v4.5': "请针对如下新闻文本，提出一个具体问题，问题要给出详尽必要的背景（如时间、地点、事件、活动名称、相关人物等），并给出相应回答。问答格式如下：\n问：{带有详细背景的问题}\n答：{回答}\n新闻如下：\n",
            'v4': "请针对如下新闻文本，提出一个具体问题，问题要包含详尽必要的背景，并给出回答。格式如下：\n问：{带有完整背景的问题}\n答：{回答}\n不要输出多余内容。\n新闻如下：\n",
            'v5': "请针对如下新闻文本，提出五个具体问题，问题要包含详尽完整的背景，不同问题的背景可以重复，至少要给出具体的时间、地点、事件、活动名称、会议名称、相关单位和人员等，并给出每个问题的相应回答。每组问答格式如下：\n问：{带有完整背景的问题}\n答：{回答}\n不要编号。\n新闻如下：\n",
        }
        user_prompt = user_prompt_versions[version]
        # print('第 %d 条新闻' % id)
        id += 1
        # print('<<<\n'+user_prompt+news_body)  
        
        qa = []
        failed = False
        for _ in range(n_qa):
            try:
                completion = client.chat.completions.create(
                    messages=[
                        # {"role": "system", "content": "You are a helpful assistant. User is asking for some possible questions to ask about the news, you should generate some questions based on the news alongwith the answers. The questions should be open-ended and should not be too specific."},
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": user_prompt+news_body}
                    ],
                    model="gpt-3.5-turbo-1106",
                    n=n_resp,
                    top_p=0.95,
                    temperature=2.0,
                )
            except Exception as e:
                error_report = f'[{type(e).__name__}] {str(e)}'
                print(error_report)
                failed = True
                break
            for i in range(n_resp):
                message = completion.choices[i].message
                content = unicodedata.normalize('NFKC', message.content)
                qa.append(content)
                # print('>>>\n'+content)
        if failed:
            continue
        data = news
        # data['prompt'] = user_prompt
        data['qa'] = qa
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        json.dump(data, open(os.path.join(datapath, f'{name}_qa.json'), 'w'), ensure_ascii=False, indent=4)
        # print('>>>\n'+qa)
        # print('---\n\n')
        # break
        

get_qa_from_openai()
# $0.0826880
# $0.0868800 single
# $0.1075380 *10


