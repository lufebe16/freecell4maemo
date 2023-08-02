
#=============================================================================
# factorial funktion mit cache.

class fact(object):
    cache = {}

    def calc(self,n):
        if n in self.cache.keys():
            #print ("cache hit:",n)
            return self.cache[n]

        if (n==1 or n==0):
            self.cache[n] = 1
        else:
            self.cache[n] = n * self.calc(n - 1)
        return self.cache[n]

        # return 1 if (n==1 or n==0) else n * self.calc(n - 1);
        # 52! =
        # 80658175170943878571660636856403766975289505440883277824000000000000
        # d.h. ein eindeutiger Identifikator wäre (als Zahl dargestellt) so lang.

    def __call__(self,n):
        return self.calc(n)

factorial = fact()

#=============================================================================
