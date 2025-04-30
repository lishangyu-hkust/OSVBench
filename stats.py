
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--output', type=str, default='claude3sonnot_Spec', help='output file name.')
args = parser.parse_args()

output_file = "./outputs/" + args.output

incorrect_pointer_correct = 0
incorrect_privilege_correct = 0
memory_leak_correct = 0
buffer_overflow_correct = 0
bounds_checking_correct = 0
correct_correct = 0

bug_num_1_correct = 0
bug_num_2_correct = 0
bug_num_3_correct = 0
bug_num_4_correct = 0
bug_num_5_correct = 0

all_correct = 0
syntaxError = 0
semanticError = 0

benchmark = ''

with open("./bench_prompts/benchmark.json") as f:
    benchmark = json.load(f)

assert len(benchmark) == 245

# Parse bug correct output.
output_content = ''
with open(output_file) as f:
    output_content = f.read()
output_list = output_content.split("Syscall ")
output_list = output_list[1:]

assert len(output_list) == 245, "Insufficient output: The output file should contain all verification results for all 245 tasks."
for i in range(len(output_list)):
    if ":" not in output_list[i]:
        continue
    if "... ok" not in output_list[i]:
        if "Could not prove, trying to find a minimal ce" in output_list[i] or "Timeout" in output_list[i]:
            semanticError += 1
        else:
            syntaxError += 1

    else:
        all_correct += 1
        bench_record = benchmark[i]
        if "bug_type" not in bench_record and "bug_num" not in bench_record:
            if "... ok" in output_list[i]:
                correct_correct += 1

        if "bug_type" in bench_record:
            if 'incorrect pointer' in bench_record['bug_type']:
                incorrect_pointer_correct += 1
            if 'incorrect privilege' in bench_record['bug_type']:
                incorrect_privilege_correct += 1
            if 'memory leak' in bench_record['bug_type']:
                memory_leak_correct += 1
            if 'buffer overflow' in bench_record['bug_type']:
                buffer_overflow_correct += 1
            if 'bounds checking' in bench_record['bug_type']:
                bounds_checking_correct += 1

        if "bug_num" in bench_record:
            if "1" in bench_record["bug_num"]:
                bug_num_1_correct += 1
            elif "2" in bench_record["bug_num"]:
                bug_num_2_correct += 1
            elif "3" in bench_record["bug_num"]:
                bug_num_3_correct += 1
            elif "4" in bench_record["bug_num"]:
                bug_num_4_correct += 1
            elif "5" in bench_record["bug_num"]:
                bug_num_5_correct += 1

print("Correct number and rate: ", all_correct, "{:.4f}".format(all_correct/245))
print("SyntaxError number and rate: ", syntaxError, "{:.4f}".format(syntaxError/245))
print("SemanticError number and rate: ", semanticError, "{:.4f}".format(semanticError/245))

assert (all_correct + syntaxError + semanticError == 245)

print("Pass number and rate of implementations with incorrect pointer bug: ", incorrect_pointer_correct, "{:.4f}".format(incorrect_pointer_correct/71))
print("Pass number and rate of implementations with incorrect privilege bug: ", incorrect_privilege_correct, "{:.4f}".format(incorrect_privilege_correct/112))
print("Pass number and rate of implementations with memory leak bug: ", memory_leak_correct, "{:.4f}".format(memory_leak_correct/74))
print("Pass number and rate of implementations with buffer overflow bug: ", buffer_overflow_correct, "{:.4f}".format(buffer_overflow_correct/54))
print("Pass number and rate of implementations with bounds checking bug: ", bounds_checking_correct, "{:.4f}".format(bounds_checking_correct/108))
print("Pass number and rate of correct implementations: ", correct_correct, "{:.4f}".format(correct_correct/49))
