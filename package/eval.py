def is_correct(pred: set[str], corr: set[str]) -> bool:
	return len(pred & corr) > 0
