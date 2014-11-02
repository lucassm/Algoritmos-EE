# coding=utf-8
from numpy import size, array, mat

from rnp import Arvore, Aresta


class Setor(Arvore):
    def __init__(self, nome, vizinhos, nos_de_carga):
        assert isinstance(nome, str), 'O parâmetro nome da classe' \
                                      'Setor deve ser do tipo string'
        assert isinstance(vizinhos, list), 'O parâmetro vizinhos da classe' \
                                           ' Setor deve ser do tipo list'
        assert isinstance(nos_de_carga, list), 'O parâmetro nos_de_carga da classe' \
                                               'Setor deve ser do tipo list'
        self.nome = nome
        self.vizinhos = vizinhos
        self.nos_de_carga = dict()
        for no in nos_de_carga:
            no.setor = self.nome
            self.nos_de_carga[no.nome] = no

        self.arvore_do_setor = self._gera_arvore_do_setor()

        super(Setor, self).__init__(self.arvore_do_setor, str)

    def _gera_arvore_do_setor(self):
        arvore_do_setor = dict()
        for i, j in self.nos_de_carga.iteritems():
            print '%-12s vizinhos %s' % (str(j), j.vizinhos)
            vizinhos = list()
            for k in j.vizinhos:
                if k in self.nos_de_carga.keys():
                    vizinhos.append(k)
            arvore_do_setor[i] = vizinhos

        return arvore_do_setor

    def __str__(self):
        return 'Setor: ' + self.nome


class NoDeCarga(object):
    def __init__(self, nome, vizinhos, potencia):
        assert isinstance(nome, str), 'O parâmetro nome da classe NoDeCarga' \
                                      ' deve ser do tipo string'
        assert isinstance(vizinhos, list), 'O parâmetro vizinhos da classe' \
                                           ' Barra deve ser do tipo string'
        assert isinstance(potencia, complex), 'O parâmetro potência da classe' \
                                              'NoDeCarga deve ser do tipo complex'
        self.nome = nome
        self.potencia = potencia
        self.vizinhos = vizinhos
        self.setor = None

    def __str__(self):
        return 'No de Carga: ' + self.nome


class Alimentador(Arvore):
    def __init__(self):
        pass


class Trecho(Aresta):
    def __init__(self, nome, n1, n2, chave=None):
        assert isinstance(nome, str), 'O parâmetro nome da classe Trecho ' \
                                      'deve ser do tipo str'
        assert isinstance(n1, NoDeCarga), 'O parâmetro n1 da classe Trecho ' \
                                          'deve ser do tipo No de carga'
        assert isinstance(n2, NoDeCarga), 'O parâmetro n2 da classe Trecho' \
                                          'deve ser do tipo No de carga'
        assert isinstance(chave, Chave) or \
               chave is None, 'O parâmetro nome da classe Trecho deve' \
                              ' ser do tipo Chave'
        super(Trecho, self).__init__(nome)
        self.n1 = n1
        self.n2 = n2
        self.chave = chave

    def __str__(self):
        return 'Trecho: %s' % self.nome


class Subestacao(Arvore):
    def __init__(self, nome, setores, chaves):
        assert isinstance(nome, str), 'O parâmetro nome da classe Subestação' \
                                      'deve ser do tipo string'
        assert isinstance(setores, list), 'O parâmetro setores da classe' \
                                          'Subestacao deve ser do tipo dict'
        assert isinstance(chaves, list), 'O parâmetro chaves da classe' \
                                         'Subestacao deve ser do tipo dict'
        self.nome = nome
        self.setores = dict()
        for setor in setores:
            self.setores[setor.nome] = setor

        self.chaves = dict()
        for chave in chaves:
            self.chaves[chave.nome] = chave

        self.nos_de_carga = dict()
        for setor in self.setores.values():
            for no in setor.nos_de_carga.values():
                self.nos_de_carga[no.nome] = no

        self.trechos = dict()

        self.arvore_da_rede = self._gera_arvore_da_rede()

        super(Subestacao, self).__init__(self.arvore_da_rede, str)

    def _gera_arvore_da_rede(self):
        arvore_da_rede = dict()
        for i, j in self.setores.iteritems():
            print '%-12s vizinhos %s' % (str(j), j.vizinhos)
            arvore_da_rede[i] = j.vizinhos

        return arvore_da_rede

    def gera_arvore_nos_de_carga(self):

        setor_raiz = self.setores[self.rnp[1][0]]
        self.arvore_nos_de_carga = Arvore(arvore=setor_raiz.arvore_do_setor, dtype=str)
        self.arvore_nos_de_carga.ordena(raiz=setor_raiz.rnp[1][0])
        visitados = []
        pilha = []
        self._gera_arvore_nos_de_carga(setor_raiz, visitados, pilha)
        self.rnp_nos_de_carga = self.arvore_nos_de_carga.rnp

    def _gera_arvore_nos_de_carga(self, setor, visitados, pilha):
        visitados.append(setor.nome)
        pilha.append(setor.nome)

        vizinhos = setor.vizinhos
        # for percorre os setores vizinhos ao setor atual
        # que ainda não tenham sido visitados
        for i in vizinhos:
            if i not in visitados:
                prox = i
                setor_vizinho = self.setores[i]
                # for percorre os nós de carga do setor atual
                for k in setor.nos_de_carga.keys():
                    # for verifica qual nó de carga em comum
                    # entre os nós de carga do setor atual e do vizinho
                    if k in setor_vizinho.nos_de_carga.keys():
                        no = setor_vizinho.rnp[1, 1]
                        poda = setor_vizinho.podar(no)
                        self.arvore_nos_de_carga.inserir_ramo(no=k, ramo=poda)
                        for h, j in setor_vizinho.arvore_do_setor.iteritems():
                            if h not in self.arvore_nos_de_carga.arvore.keys():
                                self.arvore_nos_de_carga.arvore[h] = j

                        break
            else:
                continue
            break
        else:
            pilha.pop()
            if pilha:
                anter = pilha.pop()
                return self._gera_arvore_nos_de_carga(self.setores[anter], visitados, pilha)
            else:
                return
        return self._gera_arvore_nos_de_carga(self.setores[prox], visitados, pilha)

    def gera_trechos_da_rede(self):
        print self.arvore_nos_de_carga.rnp
        j = 0
        for i in range(1, size(self.arvore_nos_de_carga.rnp, axis=1)):
            prof_1 = int(self.arvore_nos_de_carga.rnp[0, i])
            prof_2 = int(self.arvore_nos_de_carga.rnp[0, j])

            while abs(prof_1 - prof_2) is not 1:
                if abs(prof_1 - prof_2) == 0:
                    j -= 1
                elif abs(prof_1 - prof_2) == 2:
                    j = i - 1
                prof_2 = int(self.arvore_nos_de_carga.rnp[0, j])
            else:
                n_1 = str(self.arvore_nos_de_carga.rnp[1, j])
                n_2 = str(self.arvore_nos_de_carga.rnp[1, i])
                setor_1 = None
                setor_2 = None
                for setor in self.setores.values():
                    if n_1 in setor.nos_de_carga.keys() and n_1 != str(setor.rnp[1, 0]):
                        setor_1 = setor
                    if n_2 in setor.nos_de_carga.keys() and n_2 != str(setor.rnp[1, 0]):
                        setor_2 = setor

                    if setor_1 is not None and setor_2 is not None:
                        break
                else:
                    if setor_1 is None:
                        n = n_1
                    else:
                        n = n_2
                    for setor in self.setores.values():
                        if n in setor.nos_de_carga.keys() and size(setor.rnp, axis=1) == 1:
                            if setor_1 is None:
                                setor_1 = setor
                            else:
                                setor_2 = setor
                            break

                if setor_1 != setor_2:
                    for chave in self.chaves.values():
                        if chave.n1 in (setor_1, setor_2) and chave.n2 in (setor_1, setor_2):
                            self.trechos[n_1 + n_2] = Trecho(nome=n_1 + n_2,
                                                             n1=self.nos_de_carga[n_1],
                                                             n2=self.nos_de_carga[n_2],
                                                             chave=chave)
                else:
                    self.trechos[n_1 + n_2] = Trecho(nome=n_1 + n_2,
                                                     n1=self.nos_de_carga[n_1],
                                                     n2=self.nos_de_carga[n_2])

    def podar(self, no, alterar_rnp=False):
        poda = super(Subestacao, self).podar(no, alterar_rnp)
        if alterar_rnp:
            setores = dict()
            for i in poda[1, :]:
                setor = self.setores.pop(i)
                setores[setor.nome] = setor

            nos_de_carga = dict()
            for setor in setores.values():
                for j in setor.nos_de_carga.values():
                    if j.nome in self.nos_de_carga.keys():
                        no_de_carga = self.nos_de_carga.pop(j.nome)
                        nos_de_carga[no_de_carga.nome] = no_de_carga

            for setor in self.setores.values():
                for no in setor.nos_de_carga.values():
                    self.nos_de_carga[no.nome] = no
                    if no.nome in nos_de_carga.keys():
                        nos_de_carga.pop(no.nome)

            # TODO: atualizar os parâmetros arvore, arvore_da_rede e arvore_nos_de_carga

            return poda, setores, nos_de_carga
        else:
            return poda


class Chave(Aresta):
    def __init__(self, nome, estado=1):
        assert estado == 1 or estado == 0, 'O parâmetro estado deve ser um inteiro de valor 1 ou 0'
        super(Chave, self).__init__(nome)
        self.estado = estado

    def __str__(self):
        return 'Chave: %s - n1: %s, n2: %s' % (self.nome, self.n1.nome, self.n2.nome)


if __name__ == '__main__':
    # Este trecho do módulo faz parte de sua documentacao e serve como exemplo de como
    # utiliza-lo. Uma pequena rede com duas subestações é representada.

    # Na Subestação S1 existem três setores de carga: A, B, C.
    # O setor A possui três nós de carga: A1, A2, e A3
    # O setor B possui três nós de carga: B1, B2, e B3
    # O setor C possui três nós de carga: C1, C2, e C3
    # O nó de carga S1 alimenta o setor A por A2 através da chave 1
    # O nó de carga A3 alimenta o setor B por B1 através da chave 2
    # O nó de carga A2 alimenta o setor C por C1 através da chave 3

    # Na Subestação S2 existem dois setores de carga: D e E.
    # O setor D possui três nós de carga: D1, D2, e D3
    # O setor E possui três nós de carga: E1, E2, e E3
    # O nó de carga S2 alimenta o setor D por D1 através da chave 6
    # O nó de carga D1 alimenta o setor E por E1 através da chave 7

    # A chave 4 interliga os setores B e E respectivamente por B2 e E2
    # A chave 5 interliga os setores B e C respectivamente por B3 e C3
    # A chave 8 interliga os setores C e E respectivamente por C3 e E3

    # Para representar a rede são criados então os seguintes objetos:
    # _chaves : dicionario contendo objetos do tipo chave que representam
    # as chaves do sistema;
    # _seotores_1 : dicionario contendo objetos setor que representam
    # os setores da Subestação S1;
    # _seotores_2 : dicionario contendo objetos setor que representam
    # os setores da Subestação S2;
    # _nos : dicionarios contendo objetos nos_de_carga que representam
    # os nós de carga dos setores em cada um dos trechos das
    # subestações;
    # _subestacoes : dicionario contendo objetos Subestacao que herdam
    # a classe Arvore e contém todos os elementos que
    # representam um ramo da rede elétrica, como chaves, setores,
    # nós de carga e trechos;

    # chaves do alimentador de S1
    ch1 = Chave(nome='1', estado=1)
    ch2 = Chave(nome='2', estado=1)
    ch3 = Chave(nome='3', estado=1)

    # chaves de Fronteira
    ch4 = Chave(nome='4', estado=0)
    ch5 = Chave(nome='5', estado=0)
    ch8 = Chave(nome='8', estado=0)

    # chaves do alimentador de S2
    ch6 = Chave(nome='6', estado=1)
    ch7 = Chave(nome='7', estado=1)

    # Nos de carga do alimentador S1
    s1 = NoDeCarga(nome='S1', vizinhos=['A2'], potencia=0.0 + 0.0j)
    a1 = NoDeCarga(nome='A1', vizinhos=['A2'], potencia=160 + 120j)
    a2 = NoDeCarga(nome='A2', vizinhos=['S1', 'A1', 'A3', 'C1'], potencia=150 + 110j)
    a3 = NoDeCarga(nome='A3', vizinhos=['A2', 'B1'], potencia=100 + 80j)
    b1 = NoDeCarga(nome='B1', vizinhos=['B2', 'A3'], potencia=200 + 140j)
    b2 = NoDeCarga(nome='B2', vizinhos=['B1', 'B3', 'E2'], potencia=150 + 110j)
    b3 = NoDeCarga(nome='B3', vizinhos=['B2', 'C3'], potencia=100 + 80j)
    c1 = NoDeCarga(nome='C1', vizinhos=['C2', 'C3', 'A2'], potencia=200 + 140j)
    c2 = NoDeCarga(nome='C2', vizinhos=['C1'], potencia=150 + 110j)
    c3 = NoDeCarga(nome='C3', vizinhos=['C1', 'B3', 'E3'], potencia=100 + 80j)

    # Nos de carga do alimentador S2
    s2 = NoDeCarga(nome='S2', vizinhos=['D1'], potencia=0.0 + 0.0j)
    d1 = NoDeCarga(nome='D1', vizinhos=['S2', 'D2', 'D3', 'E1'], potencia=200 + 160j)
    d2 = NoDeCarga(nome='D2', vizinhos=['D1'], potencia=90 + 40j)
    d3 = NoDeCarga(nome='D3', vizinhos=['D1'], potencia=100 + 80j)
    e1 = NoDeCarga(nome='E1', vizinhos=['E3', 'E2', 'D1'], potencia=100 + 40j)
    e2 = NoDeCarga(nome='E2', vizinhos=['E1', 'B2'], potencia=110 + 70j)
    e3 = NoDeCarga(nome='E3', vizinhos=['E1', 'C3'], potencia=150 + 80j)

    # Setor S1
    st1 = Setor(nome='S1',
                vizinhos=['A'],
                nos_de_carga=[s1])

    # setor A
    stA = Setor(nome='A',
                vizinhos=['S1', 'B', 'C'],
                nos_de_carga=[s1, a1, a2, a3])

    # Setor B
    stB = Setor(nome='B',
                vizinhos=['A'],
                nos_de_carga=[a3, b1, b2, b3])

    # Setor C
    stC = Setor(nome='C',
                vizinhos=['A'],
                nos_de_carga=[a2, c1, c2, c3])

    # Setor S2
    st2 = Setor(nome='S2',
                vizinhos=['D'],
                nos_de_carga=[s2])

    # Setor D
    stD = Setor(nome='D',
                vizinhos=['S2', 'E'],
                nos_de_carga=[s2, d1, d2, d3])

    # Setor E
    stE = Setor(nome='E',
                vizinhos=['D'],
                nos_de_carga=[d1, e1, e2, e3])

    # ligação das chaves com os respectivos setores
    ch1.n1 = st1
    ch1.n2 = stA

    ch2.n1 = stA
    ch2.n2 = stB

    ch3.n1 = stA
    ch3.n2 = stC

    ch4.n1 = stB
    ch4.n2 = stE

    ch5.n1 = stB
    ch5.n2 = stC

    ch6.n1 = st2
    ch6.n2 = stD

    ch7.n1 = stD
    ch7.n2 = stE

    ch8.n1 = stC
    ch8.n2 = stE

    # Subestacao S1
    _sub_1 = Subestacao(nome='S1',
                        setores=[st1, stA, stB, stC],
                        chaves=[ch1, ch2, ch3, ch4, ch5, ch8])

    # Subestacao S2
    _sub_2 = Subestacao(nome='S2',
                        setores=[st2, stD, stE],
                        chaves=[ch6, ch7, ch4, ch8])

    _subestacoes = {_sub_1.nome: _sub_1, _sub_2.nome: _sub_2}

    # Definicao da estrutura dos ramos da Subestacao S1
    for i, j in _sub_1.setores.iteritems():
        if i == 'S1':
            j.ordena(raiz='S1')
            print j.rnp
        elif i == 'A':
            j.ordena(raiz='S1')
            print j.rnp
        elif i == 'C':
            j.ordena(raiz='A2')
            print j.rnp
        elif i == 'B':
            j.ordena(raiz='A3')
            print j.rnp

    # Definicao da estrutura dos ramos da Subestacao S2
    for i, j in _sub_2.setores.iteritems():
        if i == 'S2':
            j.ordena(raiz='S2')
            print j.rnp
        elif i == 'D':
            j.ordena(raiz='S2')
            print j.rnp
        elif i == 'E':
            j.ordena(raiz='D1')
            print j.rnp

    _sub_1.ordena(raiz='S1')
    _sub_2.ordena(raiz='S2')

    _sub_1.gera_arvore_nos_de_carga()
    _sub_2.gera_arvore_nos_de_carga()

    # Imprime a representação de todos os setores da subestção na representação
    # nó profundidade
    # print sub1.rnp

    # print sub1.arvore_nos_de_carga.arvore
    # print sub1.rnp_nos_de_carga

    # imprime as rnp dos setores de S1
    for setor in _sub_1.setores.values():
        print 'setor: ', setor.nome
        print setor.rnp

    # imprime as rnp dos setores de S2
    for setor in _sub_2.setores.values():
        print 'setor: ', setor.nome
        print setor.rnp

    _subestacoes['S1'].gera_trechos_da_rede()

    # imprime os trechos da rede S1
    for trecho in _sub_1.trechos.values():
        print trecho
