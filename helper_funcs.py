import atexit

class WindowsInhibitor:
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001

    def __init__(self):
        pass

    def inhibit(self):
        import ctypes
        print("Preventing Windows from going to sleep")
        ctypes.windll.kernel32.SetThreadExecutionState(
            WindowsInhibitor.ES_CONTINUOUS | \
            WindowsInhibitor.ES_SYSTEM_REQUIRED)

    def uninhibit(self):
        import ctypes
        print("Allowing Windows to go to sleep")
        ctypes.windll.kernel32.SetThreadExecutionState(
            WindowsInhibitor.ES_CONTINUOUS)
        
# sleep inhibitor 
osSleep = WindowsInhibitor()
osSleep.inhibit()

def exit_handler():
    osSleep.uninhibit()

atexit.register(exit_handler)

class singleton:
    def __init__(self) -> None:
        print()
        des = input("Default Behavior? ~5min (y/n): ").lower() 
        if (des == 'y'):
            self.isVerbose = True
            self.isRand = False
            self.kAnnealing = 2000
            self.nWalk = 3
            self.T = 1
            self.kGreedy = 6000
            self.sigma = 0.3
            self.dBeta = True
            print()
        elif (des == 'test'):
            self.isVerbose = True
            self.isRand = True
            self.kAnnealing = 1000
            self.nWalk = 1
            self.T = 1
            self.kGreedy = 250
            self.sigma = 0.3
            self.dBeta = False
            print()
        else:
            print()
            self.isVerbose = ("y" == input("Verbose? (y/n): ").lower())
            print()
            self.isRand = ("y" == input("Random Starting Point? (y/n): ").lower())
            if self.isRand:
                print()
                print("!!!! Recommend higher SD, assume nominal transistors, and num steps !!!!")
            print()
            self.dBeta = ("y" == input("(y) Check transistor tolerances or (n) assume nominal (y/n): ").lower())
            print()
            self.sigma = float(input("Neighbor Standard Deviation (recommend <1): "))
            print()
            print("Simulated Annealing")
            self.kAnnealing = int(input("Num steps per walk: "))
            self.nWalk = int(input("Num walks: "))
            self.T = float(input("Starting Temperature (recommend <1.25): "))
            print()
            print("Greedy Random Walk")
            self.kGreedy = int(input("Num steps: "))

single = singleton()