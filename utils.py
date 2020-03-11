class TypeError(Exception):
    pass

def typecheck(*types, **kwtypes):
    def wrapper(f):
        def new_func(*args, **kwargs):
            for i in range(len(types)):
                if types[i] and not issubclass(type(args[i]), types[i]):
                    raise TypeError('{} should be of type {}'.format(args[i], types[i]))
            for k in kwtypes:
                if k in kwargs and kwtypes[k] and not issubclass(type(kwargs[k]), kwtypes[k]):
                    raise TypeError('{} ({}) should be of type {}'.format(k, kwargs[k], kwtypes[k]))
            return f(*args, **kwargs)
        return new_func
    return wrapper

class posint(int):
    def __new__(cls, value):
        return int.__new__(cls, abs(value))
