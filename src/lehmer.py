
import bisect
from factorial import factorial

def lehmer_from_deal2(perm):

    lehm = perm.copy()
    for i in range(1,len(perm)):
        j = i
        while (j):
            j -= 1
            if perm[j] < perm[i]:
                lehm[i] -= 1

    #print (lehm)
    return lehm

    """
    array<unsigned, 3> perm = {2, 0, 1};

    // Calculate the Lehmer code of the permutation.
    array<unsigned, 3> lehmer = perm;

    for (unsigned i = 1; i < perm.size(); ++i)
    {
        unsigned j = i;

        // Note the post-decrement (from i-1 to 0, inclusive).
        while (j--)
        {
            if (perm[j] < perm[i])
            --lehmer[i];
        }
    }
    """

def lehmer_from_deal(perm):

    # Dies ist die Umkehrung des Algorithmus unten. Die Elemente
    # der Permutation werden (von rechts nach links) in eine zuvor leere
    # Liste einsortiert. Die Einfügeposition wird in einer neuen Liste
    # gesammelt: Dies ist der Lehmer code.
    # (oben: effizientere Methode aus C portiert. Gibt das gleiche Resultat.)

    vals = []
    lehm = []
    for i in range(len(perm)-1,-1,-1):
        j = perm[i]
        bisect.insort(vals,j)
        lehm.insert(0,vals.index(j))

    #print (lehm)
    return lehm

def deal_from_lehmer(lehm):

    # Der Lehmercode bezeichnet das wievielte Element aus
    # der sortierten Liste ausgebucht wird (von links nach rechts),
    # bis die Liste leer ist. Die ausgebuchten Elemnte bilden eine
    # neue Liste in der Reihenfolge der Ausbuchung: Das ist die
    # zugehörige Permutation.

    vals = [v for v in range(0,len(lehm))]
    perm = []
    for i in range(0, len(lehm)):
        v = vals[lehm[i]]
        perm.append(v)
        vals.remove(v)

    #print (perm)
    return perm

#=============================================================================
# Anzahl aufsteigende Sequenzen

def quality_from_lehmer(lehm):
    seq = 0
    llen = len(lehm)
    for i in range(1, llen):
        if lehm[i] < lehm[i-1]:
            seq += 1
    return seq

#=============================================================================
# Der Lehmer Code stellt den Permutations Index im Factoriellen Zahlensystem
# dar. Daraus kann der Index berechnet werden.

def index_from_lehmer(lehm):

    cnt = len(lehm)
    sum = 0
    for i in range(0,cnt):
        sum = sum + factorial(cnt-i-1) * lehm[i]

    #print (sum)
    return sum

def lehmer_from_index(index,size = 52):

    lehm = []
    i = index
    print ("index: ",i)

    for n in range(size-1,-1,-1):
        f = factorial(n)
        d = i // f
        i = i - d * f
        lehm.append(d)

    #print (lehm)
    return lehm

#=============================================================================
# Exportierte Klasse.

class Lehmer(object):
	def __init__(self,index=None,perm=None,size=52):
		if index is not None:
			self.lehmer = lehmer_from_index(index,size)
		if perm is not None:
			self.lehmer = lehmer_from_deal(perm)

	def getCode(self):
		return self.lehmer

	def getIndex(self):
		return index_from_lehmer(self.lehmer)

	def getSequence(self):
		return deal_from_lehmer(self.lehmer)

	def getQuality(self):
		return quality_from_lehmer(self.lehmer)

#=============================================================================
