wprompt = None
winput = None
default = 1
go_back = 'Go back'

def prompt(header, options, default=None, valid=None, return_option=False):
	wprompt.wipe()
	if type(options) != dict:
		options = dict(enumerate(options, 1))
	wprompt.print(header)
	for o in options:
		wprompt.print(' [{}] {}'.format(o, options[o]))
	o = _right_input(options.keys() if valid is None else valid, default)

	return o if return_option else options[o]

def _right_input(options=None, default=None):
	winput.wipe()
	text = ('[{}] '.format(default) if default else '') + '-> '
	i = winput.input(text)
	while i not in [str(o) for o in options]:
		if i == '' and (options is None or default in options):
			i = default
			break
		winput.wipe()
		text = 'Invalid option! ' + ('[{}] '.format(default) if default else '') + '-> '
		i = winput.input(text)
	return type(list(options)[0])(i)
