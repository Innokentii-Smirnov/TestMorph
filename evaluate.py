import os, shutil
from os import path
from sys import argv
from package.util import split, join
from package.eval import is_correct
def postprocess(morpholex: str) -> str:
	return morpholex.replace('\u0301', '').replace('|', '')
predfile, corrfile, target = argv[1:]
source = os.getcwd()
os.makedirs(target, exist_ok=True)
os.chdir(target)
if path.exists('correct.txt'):
	with open('correct.txt', 'r', encoding='utf-8') as fin:
		old_correct = set(map(str.rstrip, fin))
else:
	old_correct = set()
if path.exists('errors.txt'):
	with open('errors.txt', 'r', encoding='utf-8') as fin:
		old_errors = set(map(str.rstrip, fin))
else:
	old_errors = set()
if path.exists('missing.txt'):
	with open('missing.txt', 'r', encoding='utf-8') as fin:
		old_missing = set(map(str.rstrip, fin))
else:
	old_missing = set()
correct = set()
errors = set()
missing = set()
n_correct = 0
n_equal = 0
total = 0
with (open(path.join(source, predfile), 'r', encoding='utf-8') as fin,
	  open(path.join(source, corrfile), 'r', encoding='utf-8') as ref,
	  open('correct.txt', 'w', encoding='utf-8') as corrf,
	  open('errors.txt', 'w', encoding='utf-8') as errf,
	  open('missing.txt', 'w', encoding='utf-8') as mf,
	  open('incomplete.txt', 'w', encoding='utf-8') as incompf,
	  open('extra.txt', 'w', encoding='utf-8') as extraf):
	for corr_line in ref:
		total += 1
		joined_corr = corr_line.rstrip()
		corr: set[str] = split(joined_corr)
		pred = set[str]()
		while ((line := fin.readline().rstrip()) != ''):
			spl = line.split('\t')
			if len(spl) == 2:
				morpholex, generated = spl
				pred.add(generated)
			else:
				morpholex, _, mark = spl
				assert mark == '+?', morpholex
				line = fin.readline().rstrip()
				assert line == ''
				break
		joined_pred = join(pred)
		postprocessed = set(map(postprocess, pred))
		correctness = is_correct(postprocessed, corr)
		equality = (postprocessed == corr)
		if correctness:
			n_correct += 1
			if equality:
				n_equal += 1
				string = '{0:30} {1}'.format(morpholex, joined_pred)
			else:
				extra = postprocessed - corr
				if len(extra) > 0:
					string = '{0:30} {1:30} {2}'.format(
						morpholex, join(extra), joined_corr)
					extraf.write(string + '\n')
				incomp = corr - postprocessed
				if len(incomp) > 0:
					string = '{0:30} {1:30} {2}'.format(
						morpholex, joined_pred, join(incomp))
					incompf.write(string + '\n')
				else:
					if postprocessed.issubset(corr):
						string = '{0:30} {1}'.format(morpholex, joined_pred)
					else:
						string = '{0:30} {1:30} {2}'.format(
						morpholex, joined_pred, joined_corr)
			corrf.write(string + '\n')
			correct.add(string)
		elif len(pred) > 0:
			string = '{0:30} {1:50} {2}'.format(morpholex, joined_pred, joined_corr)
			errf.write(string + '\n')
			errors.add(string)
		else:
			string = '{0:30} {1}'.format(morpholex, joined_corr)
			mf.write(string + '\n')
			missing.add(string)
new_correct = sorted(correct - old_correct)
print('New correct: {0}.'.format(len(new_correct)))
new_errors = sorted(errors - old_errors)
if len(new_errors) == 0:
	print('No new errors.')
else:
	print('New errors: {0}.'.format(len(new_errors)))
new_missing = sorted(missing - old_missing)
if len(new_missing) == 0:
	print('No new missing.')
else:
	print('New missing: {0}.'.format(len(new_missing)))
with open('new_correct.txt', 'w', encoding='utf-8') as fout:
	for string in new_correct:
		fout.write(string + '\n')
with open('new_errors.txt', 'w', encoding='utf-8') as fout:
	for string in new_errors:
		fout.write(string + '\n')
with open('new_missing.txt', 'w', encoding='utf-8') as fout:
	for string in new_missing:
		fout.write(string + '\n')
accuracy = 100 * n_correct / total
print('Accuracy: {0} % ({1} / {2}).'.format(round(accuracy, 2), n_correct, total))
strict_accuracy = 100 * n_equal / total
print('Equality: {0} % ({1} / {2}).'.format(round(strict_accuracy, 2), n_equal, total))
