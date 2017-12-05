#!/usr/bin/python3

import sys
from enum import Enum
import inspect

class KAARED_RISTI:
    sent_id = ''
    lause = []
    lubatud_ristid = {}
    tagasipandud_rida = False
    rida = ''
    eof = False

    def rida_faili_tagasi(self):
        self.tagasipandud_rida = True

    def rida_failist(self):
        """
        Rida sisendfailist
        :return:
            True -- self.rida sisalduba trimmitud sisendrida
            False -- EOF
        """
        if self.eof:
            return False
        if self.tagasipandud_rida == True:
            self.tagasipandud_rida = False
            return True
        while True:
            self.rida = self.input.readline()
            if self.rida == '':
                self.eof = True
                return False    # EOF
            self.rida = self.rida.strip()
            if len(self.rida) == 0:
                continue        # ainult white space'ist koosnevaid ridasid ingoreerime
            return True         # saime mingit infot sisaldava rea

    def loe_lause_id(self):
        #print(inspect.stack()[0][2], ":DB-loe_lause_id")
        self.sent_id = ''
        # kommentaarimärgiga ridadest võtame lause ID
        while self.rida_failist():
            if self.rida[0] != '#':             # kommentaariblokk läbi
                self.rida_faili_tagasi()
                return
            if self.rida.find('sent_id') > 0:
                pos = self.rida.find('=')       # lause id sellest reast
                if pos > 0:
                    self.sent_id = self.rida[pos+1:].strip()
                else:
                    print(inspect.stack()[0][2], ":DB jamane lause id", self.rida, file=sys.stderr)
                    exit()

    def sordi_lause(self, kirje):
        return "%5s" % str(kirje[0]) + "|%5s" % str(kirje[1])

    def loe_lause(self):
        #print(inspect.stack()[0][2], ":DB")
        self.lause = []
        while self.rida_failist() and self.rida[0] != '#':
            veerg = self.rida.split('\t')
            n = len(veerg)
            if n != 10:
                print(inspect.stack()[0][2], ":DB Veider veergude arv: ", self.sent_id, ' : ', self.rida, file=sys.stderr)
            try:
                kirje = [int(veerg[6].strip()), int(veerg[0].strip())]
                self.lause.append(kirje)
            except:
                print(inspect.stack()[0][2], ":DB Mingi jama selle reaga: ", self.sent_id, ' : ', self.rida, file=sys.stderr)
        self.rida_faili_tagasi()
        self.lause.sort()

        #print(inspect.stack()[0][2], ":DB lause id = ", self.sent_id)
        #for s in self.lause:
        #    print(inspect.stack()[0][2], ":DB", s)
        #print(inspect.stack()[0][2], ":DB")

    def on_vahel(self, p1, p2, x):
        if p1 < p2:
            return p1 < x and x < p2
        return p2 < x and x < p1

    def on_valjas(self, p1, p2, x):
        if p1 < p2:
            return x < p1 or p2 < x
        return x < p2 or p1 < x

    def ristuvad_2_kaart(self, kaar1, kaar2):
        # Teise kaare 1. otspunkt on vahel ja 2. ei ole
        if self.on_vahel(kaar1[0], kaar1[1], kaar2[0]) == True and  self.on_valjas(kaar1[0], kaar1[1], kaar2[1]) == True:
            return True
        # Teise kaare 2. otspunkt on vahel ja 1. ei ole
        if self.on_vahel(kaar1[0], kaar1[1], kaar2[1]) == True and  self.on_valjas(kaar1[0], kaar1[1], kaar2[0]) == True:
            return True
        return False

    def kontrolli_ristumist_lauses(self):
        #print(inspect.stack()[0][2], ":DB")
        if self.lause[0][0] != 0:
            print(inspect.stack()[0][2], ":DB Ei leidnud juurikat:", self.sent_id, file=sys.stderr)
            return
        for n in range(1,len(self.lause)):
            k = abs(self.lause[n][0] - self.lause[n][1])
            if k == 0:
                print(inspect.stack()[0][2], ":DB Ise-enda ülemus:", self.sent_id, " sõna nr:", self.lause[n][0], file=sys.stderr)
                continue;
            if k == 1:
                continue
            # mahub midagi vahele
            for m in range(n+1, len(self.lause)):
                if abs(self.lause[m][0] - self.lause[m][1]) == 1:
                    continue
                if self.ristuvad_2_kaart(self.lause[n], self.lause[m]) == True:
                    rist = self.sent_id + ' ' + str(self.lause[n][0]) + ',' + str(self.lause[n][1]) \
                                        + ' ' + str(self.lause[m][0]) + ',' + str(self.lause[m][1])
                    try:
                        self.lubatud_ristid[rist]
                        continue
                    except:
                        print(rist, file=self.output)

    def lubatud_ristid_failist(self, in_risti):
        try:
            risti = open(in_risti, "r")
            for rida in risti:
                rida = rida.strip()
                self.lubatud_ristid[rida] = 'ok'
        except IOError:
            # pole ühtegi lubatud ristumist
            return


    def __init__(self, in_risti, in_fn, out_fn):
        #self.test()

        self.input = sys.stdin          # vaikimisi std-sisendist...
        self.output = sys.stdout        # ... std-väljundisse
        #print(inspect.stack()[0][2], "DB:", in_fn)
        if in_fn != '-':                # sisendfaili nimi, "-" korral jääb stdin
            try:
                self.input = open(in_fn, "r")
            except IOError:
                print("Ei suuda avada sisendfaili:", in_fn, file=sys.stderr)
                sys.exit(1)
        if out_fn != '-':               # väljundfaili nimi, "-" korral jääb stdout
            try:
                self.output = open(out_fn, "w")
            except IOError:
                print("Ei suuda luua väljundfaili:", out_fn, file=sys.stderr)
                sys.exit(1)

        self.lubatud_ristid_failist(in_risti)
        while self.rida_failist():
            self.rida_faili_tagasi()
            self.loe_lause_id()
            self.loe_lause()
            self.kontrolli_ristumist_lauses()

    def test(self):
        kaared = [
            [[1, 2], [3, 4], False], [[1, 2], [4, 3], False],
            [[1, 3], [2, 4], True ], [[1, 3], [4, 2], True ],
            [[1, 4], [2, 3], False], [[1, 4], [3, 2], False],

            [[2, 1], [3, 4], False], [[2, 1], [4, 3], False],
            [[2, 3], [1, 4], False], [[2, 3], [4, 1], False],
            [[2, 4], [1, 3], True ], [[2, 4], [3, 1], True ],

            [[3, 1], [2, 4], True ], [[3, 1], [4, 2], True ],
            [[3, 2], [1, 4], False], [[3, 2], [4, 1], False],
            [[3, 4], [1, 2], False], [[3, 4], [2, 1], False],

            [[4, 1], [2, 3], False], [[4, 1], [3, 2], False],
            [[4, 2], [1, 3], True ], [[4, 2], [3, 1], True ],
            [[4, 3], [1, 2], False], [[4, 3], [2, 1], False],
        ]
        print('Test algas...')
        for paar in kaared:
            if self.ristuvad_2_kaart(paar[0], paar[1]) != paar[2]:
                print("Seda teeb valesti:", paar[0], paar[1], paar[2])
        print('... ja lõppes')
        exit()

def syntax():
    print("süntaks:", sys.argv[0], "[-e lubatud_ristumiste_fail] [{-|sisendfail} {-|väljundfail}]")
    print("Lubatud ristumiste fail on väljundfailiga täpselt samal kujul.")
    exit()

if __name__ == "__main__":
    n = 1
    in_risti = ''
    if n < len(sys.argv):
        if sys.argv[n] == '-e':
            n += 1
            if n >= len(sys.argv):
                syntax() # -e lipu tagant lubatud ristumisi sisaldava faili nimi puudu
            in_risti = sys.argv[n]
            n += 1
    if n >= len(sys.argv):
        in_fn = '-'
        out_fn = '-'
    elif n + 2 == len(sys.argv):
        in_fn =  sys.argv[n]
        out_fn = sys.argv[n+1]
    else:
        syntax()

    kr = KAARED_RISTI(in_risti, in_fn, out_fn)

