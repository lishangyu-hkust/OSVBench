from tasks import *
from openai import OpenAI
from collections import defaultdict
import pickle
import argparse
import json
import datetime
from time import sleep
import os
import time
import sys
import re

llm_to_api = {
    "gpt": "gpt-4", 
    "claude": "claude-3-5-haiku-20241022",
    "mixtral": "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "deepseekCoder": "deepseek-coder",
    "deepseekCoder33b": "deepseek-ai/deepseek-coder-33b-instruct",
    "deepseek2": "deepseek-ai/DeepSeek-V2-Chat",
    "llama8b": "meta-llama/Llama-3-8b-chat-hf",
    "llama": "meta-llama/Llama-3-70b-chat-hf",
    "qwen7b": "qwen1.5-7b-chat",
    "qwen": "qwen1.5-72b-chat",
    "gemma": "gemma-7b-it",
    "o1m": "o1-mini",
    "gpt4om": "gpt-4o-mini",
    "gpto1all": "o1-all",
    "gpto1": "o1-2024-12-17",
    "gpto3m": "o3-mini",
    "gpto1p": "o1-preview",
    "gpt4o": "gpt-4o",
    "claude3sonnet": "claude-3-5-sonnet-20241022",
    "deepseekR1": "DeepSeek-R1",
    "deepseek": "deepseek-chat",
    "qwenqwq": "Qwen/QwQ-32B-Preview",
    "qwen2_72": "qwen2.5-72b-instruct",
    "qwen2coder": "Qwen/Qwen2.5-Coder-7B-Instruct",
}

def find_spec(spec_string):
    pattern = r'```python.*?```'
    m = re.search(pattern, spec_string, re.DOTALL)
    if m:
        print("Matched:", m.group())
        return True, m.group()
    else:
        print("No match")
        return False, ''

if __name__ == '__main__':
    start = time.time()

    parser = argparse.ArgumentParser()
    parser.add_argument('--llm', type=str, default='gpt4', help='llm model name')
    parser.add_argument('--task', type=str, default='Test', help='task name')
    parser.add_argument('--problem_num', type=int, default=1, help='number of problems')
    parser.add_argument('--resume', type=bool, default=False, help='resume from last checkpoint')
    parser.add_argument('--results', type=str, default='tmp', help='results location')
    parser.add_argument('--sleep', type=int, default=5, help='sleep seconds between API calls')
    parser.add_argument('--example', type=str, help='few shots examples')
    parser.add_argument('--data', type=str, help='the path of the benchmark file')
    parser.add_argument('--restart', type=int, default=0, help='single syscall number in the benchmark file to resume')
    parser.add_argument('--end', type=int, default=-1, help='single syscall number in the benchmark file to end')
    parser.add_argument('--task_number', type=int, default=-1, help='single syscall number')
    parser.add_argument('--pass_n', type=int, default=-1, help='pass n')
    args = parser.parse_args()

    classname = args.task + '_Task'
    task = globals()[classname]()
    task.load_dataset(args.example, args.data)
    error_knt = 0
    
    response_dict = defaultdict(dict)
    
    for llm in args.llm.split('-'):
        if 'gpt' in llm:
            client = OpenAI(
                base_url = "https://api.openai.com/v1/chat/completions", # Replace it to other API endpoint (e.g., AIMLAPI) if OpenAI is unavailable.
                api_key = 'YOUR_API_KEY', # Replace the API key with your own
            )
        elif 'deepseek' in llm:
            client = OpenAI(
                base_url = "https://api.deepseek.com",
                api_key="YOUR_API_KEY"
            )
        elif 'qwen' in llm:
            client = OpenAI(
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                api_key="YOUR_API_KEY",
            )
        else:
            client = OpenAI(
                base_url = "https://api.aimlapi.com/",
                api_key = 'YOUR_API_KEY'
            )

        if args.resume and os.path.exists(f"results/tmp_{args.results}/{args.llm}_{args.task}.json"):
            with open(f"results/tmp_{args.results}/{args.llm}_{args.task}.json", 'r') as f:
                response_dict = json.load(f)
                print(f"Continue")

        if not os.path.exists(f"results/tmp_{args.results}"):
            os.makedirs(f"results/tmp_{args.results}")

        passN = args.pass_n

        for i in range(0, args.problem_num - args.restart):
            system_prompt = """
You are an expert specializing in operating system kernel verification. Please provide only the state-machine specification code, strictly encapsulated within the format ```python\n{code}\n```, without including any additional text or commentary. Please act as an expert in operating system kernel verification. Your job is to synthesize the state-machine specification to verify the functional correctness of a given system call based on its given functional description and code implementation that may contain bugs.
"""

            if args.resume and i in response_dict and llm in response_dict[i] and response_dict[i][llm]:
                if response_dict[i][llm] != 'Error!':
                    print(i)
                    continue
            response_dict[i] = {}

            syscall_name = ''
            try:
                example_number = int(i) + args.restart
                if args.task_number != -1:
                    example_number = args.task_number
                if example_number >= 245:
                    raise ValueError("Syscall exists.")
                if args.end != -1 and example_number != -1 and example_number > args.end:
                    raise ValueError("Syscall exists.")

                x, syscall_name = task.insert_example(example_number)

                chat_completion = client.chat.completions.create(
                    model=llm_to_api[llm],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": x},
                    ],
                    seed=42,
                    timeout=3600,
                    max_tokens=4096,
                    n=passN
                )
                spec_list = []
                spec_result = False
                spec_string = ''
                for j in range(passN):
                    if j >= len(chat_completion.choices):
                        break
                    spec_result, spec_string = find_spec(chat_completion.choices[j].message.content)
                    if spec_result:
                        spec_list.append(spec_string[9:-3])
                response_dict[i][syscall_name] = spec_list
            except Exception as e:
                print('Call API failed! ', e)
                sleep(1)
                error_knt += 1
                response_dict[i][llm] = 'Error!'
            with open(f"results/tmp_{args.results}/{args.llm}_{args.task}.json", 'w') as f:
                json.dump(response_dict, f)
            sleep(args.sleep)
    print('error_knt:', error_knt) # if error_knt > 0, please check the API key and endpoint and run again. The script will continue from prevoiusly failed samples.
    now = datetime.datetime.now()
    if not os.path.exists(f"results/{args.results}"):
        os.makedirs(f"results/{args.results}")
    with open(f"results/{args.results}/{args.llm}_{args.task}_{now.strftime('%d_%H-%M')}.json", 'w') as f:
        json.dump(response_dict, f)
    
    end = time.time()
    execution_time = end - start
    print(f"Time elapsed: {execution_time:.2f}s")
