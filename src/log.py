class Log(object):
    show_verbose = False

    @staticmethod
    def verbose(*nargs):
        if Log.show_verbose:
            Log.println(nargs)

    @staticmethod
    def info(*nargs):
        Log.println(nargs)

    @staticmethod
    def error(*nargs):
        Log.println(nargs)

    @staticmethod
    def println(nargs):
        try:
            print(nargs[0] % tuple(nargs[1:]))
        except TypeError as e:
            import pdb;pdb.set_trace()
            print(e)

