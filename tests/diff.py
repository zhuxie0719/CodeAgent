import difflib

before_path = 'tests/output/test_python_bad_before.py'
after_path = 'tests/output/test_python_bad_after.py'

with open(before_path, 'r', encoding='utf-8') as f_before, open(after_path, 'r', encoding='utf-8') as f_after:
    before_lines = f_before.readlines()
    after_lines = f_after.readlines()

diff = difflib.unified_diff(
    before_lines, after_lines,
    fromfile='before', tofile='after',
    lineterm=''
)

with open('diff_output.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(diff))
print('Diff 已写入 diff_output.txt')