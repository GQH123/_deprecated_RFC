import os
import json
import jsonlines


submit_json_path = '../submits/fudan_news_qa_full_filtered/fudan_news_qa.json'


def convert():
    data = json.load(open(submit_json_path, 'r'))
    
    def wrap_into_template(q, a):
        return {"tools": ["python", "text2img", "retrival", "Weather.get_weather", "search"], "chat": [{"role": "user", "content": q}, {"role": "assistant", "content": a}]}
    
    converted_data = []
    for item in data:
        converted_item = wrap_into_template(item[0], item[1])
        converted_data.append(converted_item)
    # json.dump(converted_data, open(os.path.join(os.path.dirname(submit_json_path), 'fudan_news_qa_sft.json'), 'w'), indent=4)
    with jsonlines.open(os.path.join(os.path.dirname(submit_json_path), 'fudan_news_qa_sft.jsonl'), 'w') as writer:
        for item in converted_data:
            writer.write(item)


convert()