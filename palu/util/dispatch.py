class Dispatcher:
    def __init__(self):
        self.mapping = {}

    def case(self, match):
        def wrapper(func):
            self.mapping[match] = func
            return func

        return wrapper

    def default(self):
        def wrapper(func):
            self.mapping['__default'] = func
            return func

        return wrapper

    def dispatch(self, match, *args, **kwargs):
        if match not in self.mapping:
            return self.mapping['__default'](match, *args, **kwargs)
        else:
            return self.mapping[match](match, *args, **kwargs)
