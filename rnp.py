# coding=utf-8
"""
módulo de representação nó profundidade
"""

from collections import OrderedDict
from numpy import array, size, reshape, where, concatenate, mat, shape


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
        self.rnp = array(mat('0; 0'))
        self._arvore = None

    def ordena(self, raiz):
        self.rnp[1][0] = raiz
        visitados = []
        pilha = []
        self._proc(raiz, visitados, pilha)

    def _proc(self, no, visitados, pilha):
        visitados.append(no)
        pilha.append(no)
        visinhos = self.arvore[no]
        for i in visinhos:
            if i not in visitados:
                prox = i
                self.rnp = concatenate((self.rnp, [[len(pilha)], [i]]), axis=1)
                break
        else:
            pilha.pop()
            if pilha:
                anter = pilha.pop()
                return self._proc(anter, visitados, pilha)
            else:
                return
        return self._proc(prox, visitados, pilha)

    def rnp_dic(self):
        rnp = OrderedDict()
        for i in self.rnp.transpose():
            rnp[i[1]] = i[0]
        return rnp

    def podar(self, no):
        assert isinstance(no, int)
        if self.rnp.sum():
            poda, indice = self._busca_prof(no, retorna_array=True)
            prof = poda[0][0]
            for i in range(indice+1, size(self.rnp, axis=1)):
                prox = self.rnp[:, i]
                prox = reshape(prox, (2, 1))
                if prox[0][0] > prof:
                    poda = concatenate((poda, prox), axis=1)
                else:
                    break
            return poda
        else:
            raise ValueError('A árvore ainda não possui uma estrutura RNP!')

    def _busca_prof(self, no, retorna_array=False):
        try:
            indice = where(self.rnp[1, :] == no)[0][0]
            prof = int(self.rnp[0][indice])
        except IndexError:
            raise IndexError('O nó especificado não existe na árvore!')

        if retorna_array:
            return array([[prof], [no]]), indice
        else:
            return prof, indice

    def caminho_no_para_raiz(self, no, sentido=1):
        assert isinstance(no, int), 'O parâmetro nó deve ser do tipo inteiro'
        assert sentido == 1 or sentido == 0, 'O parâmetro sentido deve ser um inteiro de valor 1 ou 0'

        if self.rnp.sum():
            caminho, indice = self._busca_prof(no, retorna_array=True)
            prof = caminho[0][0]
            for i in range(indice, -1, -1):
                print self.rnp[1, i]
                prox = self.rnp[:, i]
                prox = reshape(prox, (2, 1))
                if prox[0, 0] < prof:
                    prof -= 1
                    caminho = concatenate((caminho, prox), axis=1)
            if sentido == 1:
                return caminho
            else:
                return caminho[:, range(size(caminho, axis=1)-1, -1, -1)]
        else:
            raise ValueError('A árvore ainda não possui uma estrutura RNP!')

    def caminho_no_para_no(self, n1, n2):
        pass

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
    arv_1.ordena(raiz=3)
    print arv_1.rnp
    #print arv_1.rnp_dic()
    print arv_1.podar(4)
    print arv_1.caminho_no_para_raiz(12, sentido=1)
