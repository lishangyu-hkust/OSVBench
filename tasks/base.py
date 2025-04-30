import pickle
import json

class CodeTask(object):
    def __init__(self, data_loc='./source', task_name='Test'):
        self.data_loc = data_loc
        self.task_name = task_name
        self.problem_set = []
        
    def generate_dataset(self):
        raise NotImplementedError

    def check_solution(self):
        raise NotImplementedError
    
    def save_dataset(self, difficulty=None):
        if difficulty:
            pickle.dump(self.problem_set, open(f'{self.data_loc}/{self.task_name}_{difficulty}.pkl', 'wb'))
        else:
            pickle.dump(self.problem_set, open(f'{self.data_loc}/{self.task_name}.pkl', 'wb'))
        if len(self.examples) > 0:
            pickle.dump(self.examples, open(f'{self.data_loc}/{self.task_name}_examples.pkl', 'wb'))
            print(f'{len(self.examples)} examples generated.')

        print(f'{len(self.problem_set)} problems generated.')

    def load_dataset(self):
        with open(self.data_loc + '/' + self.task_name + 'Task/' + self.task_name + 'Prompts.json') as file:
            self.prompts = json.load(file)
            self.prompts_len = len(self.prompts)

    def insert_example(self, id, num=2):
        print("Prompts: " + str(self.prompts))
        prompt = self.prompts[str(id)]

        print("Self.prompts: " + prompt)

        # selected_examples = random.sample(self.examples, num)
        # marker_position = prompt.find('\n**Problem to Solve**')
        # for i in range(num):
        # # for i, example in enumerate(selected_examples):
        #     prompt = prompt[:marker_position] + f'\n**Example {num-i}**\n\n' + self.examples[(id+i)%100] + '\n' + prompt[marker_position:]
        return prompt

    def get_syscall(self, syscall_name):
        return -1
