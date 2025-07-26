SEP = ', '
def join(elements: set[str]) -> str:
	return SEP.join(sorted(elements))
def split(elements: set[str]) -> str:
	return set(elements.split(SEP))
