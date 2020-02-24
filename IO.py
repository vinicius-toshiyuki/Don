from Log import *

class IO:
    default = 1
    go_back = "Go back"
    __tag = "Prompt"

    def prompt(header, options, default=None, valid=None, return_option=False):
        if type(options) != dict:
            options = dict(enumerate(options, 1))
        Log.put(" {}".format(header), IO.__tag)
        for o in options:
            Log.put("[{}] {}".format(o, options[o]), IO.__tag)
        o = IO._right_input("Option:", options.keys() if valid is None else valid, default)

        return o if return_option else options[o]

    def _right_input(text=None, options=None, default=None):
        if text is not None:
            if default is not None:
                text += "[{}]".format(default)
            text += ' '
        if options is None:
            while (i := input(text if text is not None else '')) != '':
                if default is not None and i == '':
                    i = default
                    break
            return i
        while (i := IO._input(text if text else '')) not in [str(o) for o in options]:
            if i == '' and default in options:
                i = default
                break
            Log.put("Invalid option!", IO.__tag)
        return type(list(options)[0])(i)

    def _input(text):
        Log.flush()
        return input(text)
