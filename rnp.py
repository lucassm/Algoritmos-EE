# coding=utf-8
"""
módulo de representação nó profundidade
"""

from collections import OrderedDict
from numpy import array


class No(object):
    """
    Classe No
    ---------
    documentacao classe No
    """
    def __init__(self, nome, vizinhos=list()):
        assert isinstance(nome, int)
        self.nome = nome
        assert isinstance(vizinhos, list)
        self.visinhos = vizinhos


class Aresta(object):
    """
    Classe Aresta
    -------------
    documentacao classe Aresta
    """
    def __init__(self, n1, n2):
        self.n1 = n1
        self.n2 = n2


class Arvore(object):
    """
    Classe Arvore
    -------------
    documentacao classe Arvore
    """
    def __init__(self, arvore):
        assert isinstance(arvore, dict)
        self.arvore = arvore
        self.raiz = None
        self.rnp = OrderedDict()
        self._arvore = None

    def ordena(self, raiz):
        self.rnp[raiz] = 0
        visitados = []
        pilha = []
        self._proc(raiz, visitados, pilha)

    def _proc(self, no, visitados, pilha):
        print 'No visitado %2s' % no
        visitados.append(no)
        pilha.append(no)
        visinhos = self.arvore[no]
        prox = None
        for i in visinhos:
            if i not in visitados:
                prox = i
                self.rnp[i] = len(pilha)
                break
        else:
            pilha.pop()
            if pilha:
                anter = pilha.pop()
                return self._proc(anter, visitados, pilha)
            else:
                return
        return self._proc(prox, visitados, pilha)

    def podar(self, no):
        assert isinstance(no, int)
        if self.rnp:

        else:
            print 'A arvore ainda não possui uma estrutura RNP'


class Floresta(object):
    """
    Classe Floresta
    ---------------
    documentacao classe Floresta
    """
    def __init__(self, floresta):
        assert isinstance(floresta, list)
        pass

if __name__ == '__main__':
    # arvore 1
    nos = {3: [1],
           1: [3, 2, 7],
           7: [1, 8, 9, 4, 10],
           10: [7],
           4: [7, 5, 6],
           5: [4],
           6: [4],
           9: [7],
           8: [7],
           2: [1, 11, 12, 13],
           11: [2],
           12: [2, 13],
           13: [12]}

    arv_1 = Arvore(nos)
    arv_1.ordena(3)
    print arv_1.rnp
