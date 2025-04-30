from tasks.base import *
import random

class Spec_Task(CodeTask):
    def __init__(self, data_loc='./bench_prompts', task_name='Spec'):
        super().__init__(data_loc, task_name)

    def load_dataset(self, example_path, data_path):
        with open(self.data_loc + "/" + example_path) as example_file:
            self.examples = example_file.read()
        
        with open(self.data_loc + "/" + data_path) as benchmark_file:
            self.benchmarks = json.load(benchmark_file)

        with open(self.data_loc + "/system_assumption_model") as system_description_file:
            self.system_description = system_description_file.read()

    def insert_example(self, id):
        prompt = ""

        prompt += self.system_description + "\n\n"

        prompt += self.examples

        prompt += "\n### Task Question:\nNow, given the system call `" + self.benchmarks[id]["syscall"] + "`. \n" + self.benchmarks[id]["description"] + "\n" + self.benchmarks[id]["code"] + "\n"

        prompt += "[Specification]:\nBased on the detailed functional description and the potentially buggy code implementation of the system call `" + self.benchmarks[id]["syscall"] + "` provided above, the state-machine specification of the system call is deduced as follows:"

        return prompt, self.benchmarks[id]["syscall"]

    def print_dataset(self):

        print(len(self.examples))
        print(len(self.benchmarks))

        for x in self.benchmarks:
            print(x["syscall"])
