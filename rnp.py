# coding=utf-8
"""
módulo de representação nó profundidade
"""

from collections import OrderedDict
from numpy import array, size, reshape, where, concatenate, mat, delete, ndarray, insert


class No(object):
    """
    Classe No
    ---------
        Classe que representa qualquer instancia que represente um nó em um
        grafo

    Parâmetros
    ----------
        nome : str identifica o nó
        vizinhos : list identifica os nós que estão na vizinhança
    """

    def __init__(self, nome, vizinhos=list()):
        assert isinstance(nome, str)
        self.nome = nome
        assert isinstance(vizinhos, list)
        self.vizinhos = vizinhos


class Aresta(object):
    """
    Classe Aresta
    -------------
        Classe que representa qualquer instancia que represente uma aresta em um grafo,
        uma aresta liga dois nós vizinhos e pode ser ou não direcionada.

    Parâmetros
    ----------
        nome : str identifica a aresta
    """

    n1 = None
    n2 = None

    def __init__(self, nome):
        assert isinstance(nome, str), 'O parâmetro nome da classe Aresta deve ser do tipo string'
        self.nome = nome


class Arvore(object):
    """
    Classe Arvore
    -------------
        A classe *Arvore* representa um grafo do tipo arvore. Uma arvore é um grafo
        conexo e que não possui ciclos em sua estrutura.

        Oferece métodos para manipular, alterar e buscar informações dos ramos e nós
        da *Arvore*.

    Parâmetros
    ----------
        arvore : dict Dicionário que representa a árvore, onde as chaves são os nós
        e os valores são listas com os vizinhos do nó que está como chave.
        dtype : tipo dos nós que podem ser strings ou inteiros
    """

    def __init__(self, arvore, dtype=int):
        assert isinstance(arvore, dict)
        self.arvore = arvore
        self.raiz = None
        self.dtype = dtype
        if issubclass(dtype, int):
            self.rnp = array(mat('0; 0'), dtype=int)
        else:
            self.rnp = array(mat('0; 0'), dtype=str)
        self._arvore = None

    def ordena(self, raiz):
        """
        metodo ordena
        -------------
            Este método cria a representação no profundidade da arvore

        Parâmetros
        ----------
            raiz : dtype Nó, presente na arvore, que sera a raiz da representação
            nó profundidade

        """
        assert isinstance(raiz, self.dtype), 'Erro no tipo do parâmetro raiz!'
        self.raiz = raiz
        self.rnp[1][0] = raiz
        visitados = []
        pilha = []
        self._proc(raiz, visitados, pilha)

    def _proc(self, no, visitados, pilha):
        """
        método _proc
        ------------
            Este método faz uma busca em profundidade na arvore para que a
            representação nó profundidade possa ser criada

        Parâmetros
        ----------
            no : dtype Nó a ser visitado
            visitados : list Lista de nós já visitados
            pilha : list Lista para identificar em que nível do grafo a busca está
        """
        visitados.append(no)
        pilha.append(no)

        try:
            visinhos = self.arvore[no]
        except KeyError:
            pilha.pop()
            if pilha:
                anter = pilha.pop()
                return self._proc(anter, visitados, pilha)
            else:
                return

        for i in visinhos:
            if i not in visitados:
                prox = i
                if issubclass(self.dtype, str):
                    self.rnp = concatenate((self.rnp, [[str(len(pilha))], [i]]), axis=1)
                else:
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

    def podar(self, no, alterar_rnp=False):
        #assert isinstance(no, int)
        #if self.rnp.sum():
        poda, indice = self._busca_prof(no, retorna_array=True)
        prof = poda[0][0]
        indices_poda = list([indice])
        for i in range(indice + 1, size(self.rnp, axis=1)):
            prox = self.rnp[:, i]
            prox = reshape(prox, (2, 1))
            if prox[0][0] > prof:
                poda = concatenate((poda, prox), axis=1)
                indices_poda.append(i)
            else:
                break
        if alterar_rnp:
            self.rnp = delete(self.rnp, indices_poda, axis=1)
        return poda
        #else:
        #    raise ValueError('A árvore ainda não possui uma estrutura RNP!')

    def inserir_ramo(self, no, ramo):
        if issubclass(self.dtype, int):
            assert isinstance(no, int), 'O parâmetro no deve ser do tipo int'
        else:
            assert isinstance(no, str), 'O parâmetro no deve ser do tipo str'
        assert isinstance(ramo, ndarray), 'O parâmetro ramo deve ser do tipo ndarray'

        prof_raiz, indice = self._busca_prof(no)
        prof_raiz_ramo = ramo[0, 0]

        for i in range(size(ramo, axis=1)):
            prof_no = ramo[0, i]
            nova_prof = int(prof_no) - int(prof_raiz_ramo) + int(prof_raiz) + 1

            if issubclass(self.dtype, str):
                ramo[0][i] = str(nova_prof)

        self.rnp = insert(self.rnp, [indice+1], ramo, axis=1)

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
        assert isinstance(no, int), 'O parâmetro no deve ser do tipo inteiro'
        assert sentido == 1 or sentido == 0, 'O parâmetro sentido deve ser um inteiro de valor 1 ou 0'

        if self.rnp.sum():
            caminho, indice = self._busca_prof(no, retorna_array=True)
            prof = caminho[0][0]
            for i in range(indice, -1, -1):
                prox = self.rnp[:, i]
                prox = reshape(prox, (2, 1))
                if prox[0, 0] < prof:
                    prof -= 1
                    caminho = concatenate((caminho, prox), axis=1)
            if sentido == 1:
                return caminho
            else:
                return caminho[:, range(size(caminho, axis=1) - 1, -1, -1)]
        else:
            raise ValueError('A árvore ainda não possui uma estrutura RNP!')

    def caminho_no_para_no(self, n1, n2, sentido=1):
        assert isinstance(n1, int), 'O parâmetro n1 deve ser do tipo inteiro'
        assert isinstance(n2, int), 'O parâmetro n2 deve ser do tipo inteiro'
        assert sentido == 1 or sentido == 0, 'O parâmetro sentido deve ser um inteiro de valor 1 ou 0'

        if self.rnp.sum():
            caminho, indice = self._busca_prof(n1, retorna_array=True)
            prof = caminho[0][0]
            for i in range(indice, -1, -1):
                prox = self.rnp[:, i]
                prox = reshape(prox, (2, 1))
                if prox[0, 0] < prof:
                    prof -= 1
                    caminho = concatenate((caminho, prox), axis=1)
                    if prox[1][0] == n2:
                        break
            else:
                raise AttributeError('Os nós n1 e n2 não pertencem ao mesmo ramo!')

            if sentido == 1:
                return caminho
            else:
                return caminho[:, range(size(caminho, axis=1) - 1, -1, -1)]
        else:
            raise ValueError('A árvore ainda não possui uma estrutura RNP!')


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
    nos1 = {3: [1],
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

    # arvore 2
    nos2 = {14: [15],
            15: [14, 16, 19],
            16: [15, 17, 18],
            17: [16],
            18: [16],
            19: [15]}

    arv_1 = Arvore(nos1)
    arv_1.ordena(raiz=3)
    print arv_1.rnp
    # print arv_1.rnp_dic()
    ram = arv_1.podar(5)
    print ram
    arv_1.inserir_ramo(8, ram)
    print arv_1.rnp
    # print arv_1.caminho_no_para_raiz(no=12, sentido=1)
    # print arv_1.caminho_no_para_no(n1=13, n2=2, sentido=1)

    arv_2 = Arvore(nos2)
    arv_2.ordena(raiz=14)
    print arv_2.rnp
