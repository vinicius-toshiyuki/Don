class Log:
    _common = list()
    _tagged = dict()
    
    def put(message, tag=None):
        if tag is None:
            Log._common.append(message)
        elif tag in Log._tagged:
            Log._tagged[tag].append(message)
        else:
            Log._tagged[tag] = [message]
    
    def flush():
        while len(Log._common) > 0:
            print(Log._common.pop(0))

        for t in Log._tagged:
            print("\n", t)
            while len(Log._tagged[t]) > 0:
                print(Log._tagged[t].pop(0))
        Log._tagged = dict()

    def _move(x, y):
        pass

    def _place(x, y):
        print("\033[{};{}H".format(x,y), end='')

    def _clear():
        print("\033[2J", end='')
        Log._place(0, 0)
