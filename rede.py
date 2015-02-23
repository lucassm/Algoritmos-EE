# coding=utf-8
import numpy as np
from random import randint
from rnp import Arvore, Aresta
from util import Fasor


class Setor(Arvore):
    Prioridade_Baixa, Prioridade_Media, Prioridade_Alta = range(3)

    def __init__(self, nome, vizinhos, nos_de_carga, prioridade=None):
        assert isinstance(nome, str), 'O parâmetro nome da classe' \
                                      'Setor deve ser do tipo string'
        assert isinstance(vizinhos, list), 'O parâmetro vizinhos da classe' \
                                           ' Setor deve ser do tipo list'
        assert isinstance(nos_de_carga, list), 'O parâmetro nos_de_carga da classe' \
                                               'Setor deve ser do tipo list'
        #assert isinstance(prioridade, int), 'O parâmetro Prioridade da classe' \
        #                                    'Setor deve ser do tipo int'
        self.nome = nome
        self.prioridade = prioridade
        self.vizinhos = vizinhos

        self.rnp_associadas = {i: None for i in self.vizinhos}

        self.nos_de_carga = dict()
        for no in nos_de_carga:
            no.setor = self.nome
            self.nos_de_carga[no.nome] = no

        self.no_de_ligacao = None

        arvore_de_setor = self._gera_arvore_do_setor()
        super(Setor, self).__init__(arvore_de_setor, str)

    def _gera_arvore_do_setor(self):
        arvore_do_setor = dict()
        # for percorre os nós de carga do setor
        for i, j in self.nos_de_carga.iteritems():
            print '%-12s vizinhos %s' % (str(j), j.vizinhos)
            vizinhos = list()
            # for percorre os vizinhos do nó de carga
            for k in j.vizinhos:
                # condição só considera vizinho o nó de carga que está
                # no mesmo setor que o nó de carga analisado
                if k in self.nos_de_carga.keys():
                    vizinhos.append(k)
            arvore_do_setor[i] = vizinhos

        return arvore_do_setor

    def calcular_potencia(self):

        potencia = Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia)
        for no in self.nos_de_carga.values():
            potencia = potencia + no.potencia

        return potencia

    def __str__(self):
        return 'Setor: ' + self.nome


class NoDeCarga(object):
    def __init__(self,
                 nome,
                 vizinhos,
                 potencia=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
                 tensao=Fasor(real=0.0, imag=0.0, tipo=Fasor.Tensao),
                 chaves=None):
        assert isinstance(nome, str), 'O parâmetro nome da classe NoDeCarga' \
                                      ' deve ser do tipo string'
        assert isinstance(vizinhos, list), 'O parâmetro vizinhos da classe' \
                                           ' Barra deve ser do tipo string'

        self.nome = nome
        self.vizinhos = vizinhos
        self.potencia = potencia
        self.potencia_eq = Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia)
        self.tensao = tensao
        if chaves is not None:
            assert isinstance(chaves, list), 'O parâmetro chaves da classe NoDeCarga' \
                                             ' deve ser do tipo list'
            self.chaves = chaves
        else:
            self.chaves = list()

        self.setor = None

    def __str__(self):
        return 'No de Carga: ' + self.nome


class Subestacao(object):
    def __init__(self, nome, alimentadores, transformadores):
        assert isinstance(nome, str), 'O parâmetro nome da classe Subestacao ' \
                                      'deve ser do tipo str'
        assert isinstance(alimentadores, list), 'O parâmetro alimentadores da classe ' \
                                                'deve ser do tipo list'

        assert isinstance(transformadores, list), 'O parâmetro alimentadores da classe ' \
                                                  'deve ser do tipo list'
        self.nome = nome

        self.alimentadores = dict()
        for alimentador in alimentadores:
            self.alimentadores[alimentador.nome] = alimentador

        self.transformadores = dict()
        for transformador in transformadores:
            self.transformadores[transformador.nome] = transformador

    def _busca_trecho(self, alimentador, n1, n2):
        """Função que busca trechos em um alimendador entre os nós/chaves
          n1 e n2"""
        # for pecorre os nos de carga do alimentador
        for no in alimentador.nos_de_carga.keys():

            # cria conjuntos das chaves ligadas ao no
            chaves_n1 = set(alimentador.nos_de_carga[n1].chaves)
            chaves_n2 = set(alimentador.nos_de_carga[n2].chaves)

            # verifica se existem chaves comuns aos nos
            chaves_intersec = chaves_n1.intersection(chaves_n2)

            if chaves_intersec != set():
                # verifica quais trechos estão ligados a chave
                # comum as nós.
                chave = chaves_intersec.pop()
                trechos_ch = []
                # identificação dos trechos requeridos
                for trecho in alimentador.trechos.values():
                    if trecho.n1.nome == chave:
                        if trecho.n2.nome == n1 or trecho.n2.nome == n2:
                            trechos_ch.append(trecho)
                    elif trecho.n2.nome == chave:
                        if trecho.n1.nome == n1 or trecho.n1.nome == n2:
                            trechos_ch.append(trecho)
                # caso o comprimento da lista seja dois, ou seja, há chave
                # entre dois ós de carga, a função retorna os trechos.
                if len(trechos_ch) == 2:
                    return trechos_ch
            else:
                # se não existirem chaves comuns, verifica qual trecho
                # tem os nos n1 e n2 como extremidade
                for trecho in alimentador.trechos.values():
                    if trecho.n1.nome == n1:
                        if trecho.n2.nome == n2:
                            return trecho
                    elif trecho.n1.nome == n2:
                        if trecho.n2.nome == n1:
                            return trecho

    def _atribuir_tensao_a_subestacao(self, tensao):
        """ Função que atribui tensão à subestação
         e a define para todos os nós de carga"""
        self.tensao = tensao
        for alimentador in self.alimentadores.values():
            for no in alimentador.nos_de_carga.values():
                no.tensao = Fasor(real=tensao.real,
                                  imag=tensao.imag,
                                  tipo=Fasor.Tensao)

    def _varrer_alimentador(self, alimentador):
        """ Função que varre os alimentadores pelo
        método varredura direta/inversa"""

        # guarda os nós de carga na variável nos_alimentador
        nos_alimentador = alimentador.nos_de_carga.values()

        # guarda a rnp dos nós de carga na variável rnp_alimentador
        rnp_alimentador = alimentador.arvore_nos_de_carga.rnp

        # guarda a árvore de cada nós de carga
        arvore_nos_de_carga = alimentador.arvore_nos_de_carga.arvore

        # variáveis para o auxílio na determinação do nó mais profundo
        prof_max = 0

        # for percorre a rnp dos nós de carga tomando valores
        # em pares (profundidade, nó).
        for no_prof in rnp_alimentador.transpose():
            # pega os nomes dos nós de carga.
            nos_alimentador_nomes = [no.nome for no in nos_alimentador]

            # verifica se a profundidade do nó é maior do que a
            # profundidade máxima e se ele está na lista de nós do alimentador.
            if (int(no_prof[0]) > prof_max) \
               and (no_prof[1] in nos_alimentador_nomes):
                prof_max = int(no_prof[0])

        # prof recebe a profundidae máxima determinada
        prof = prof_max

        # seção do cálculo das potências partindo dos
        # nós com maiores profundidades até o nó raíz
        while prof >= 0:
            # guarda os nós com maiores profundidades.
            nos = [alimentador.nos_de_carga[no_prof[1]]
                   for no_prof in rnp_alimentador.transpose() if
                   int(no_prof[0]) == prof]

            # decrementodo da profundidade.
            prof -= 1

            # for que percorre os nós com a profundidade
            # armazenada na variável prof
            for no in nos:
                # zera as potências para que na próxima
                # iteração não ocorra acúmulo.
                no.potencia_eq.real = 0.0
                no.potencia_eq.imag = 0.0

                # armazena a árvore do nó de carga
                # armazenado na variável nó
                vizinhos = arvore_nos_de_carga[no.nome]

                # guarda os pares (profundidade, nó)
                no_prof = [no_prof for no_prof in rnp_alimentador.transpose()
                           if no_prof[1] == no.nome]
                vizinhos_jusante = list()

                # for que percorre a árvore de cada nó de carga
                for vizinho in vizinhos:
                    # verifica quem é vizinho do nó desejado.
                    vizinho_prof = [viz_prof for viz_prof in
                                    rnp_alimentador.transpose()
                                    if viz_prof[1] == vizinho]

                    # verifica se a profundidade do vizinho é maior
                    if int(vizinho_prof[0][0]) > int(no_prof[0][0]):
                        # armazena os vizinhos a jusante.
                        vizinhos_jusante.append(
                            alimentador.nos_de_carga[vizinho_prof[0][1]])

                # verifica se não há vizinho a jusante,
                # se não houverem o nó de carga analisado
                # é o último do ramo.
                if vizinhos_jusante == []:
                    no.potencia_eq.real += no.potencia.real
                    no.potencia_eq.imag += no.potencia.imag
                else:
                    # soma a potencia da carga associada ao nó atual
                    no.potencia_eq.real += no.potencia.real
                    no.potencia_eq.imag += no.potencia.imag

                    # acrescenta à potência do nó atual
                    # as potências dos nós a jusante
                    for no_jus in vizinhos_jusante:
                        no.potencia_eq.real += no_jus.potencia_eq.real
                        no.potencia_eq.imag += no_jus.potencia_eq.imag

                        # chama a função busca_trecho para definir
                        # quais trechos estão entre o nó atual e o nó a jusante
                        trecho = self._busca_trecho(alimentador,
                                                    no.nome,
                                                    no_jus.nome)
                        # se o trecho não for uma instancia da classe
                        # Trecho(quando há chave entre nós de cargas)
                        # a impedância é calculada
                        if not isinstance(trecho, Trecho):

                            r1, x1 = trecho[0].calcula_impedancia()
                            r2, x2 = trecho[1].calcula_impedancia()
                            r, x = r1 + r2, x1 + x2
                        # se o trecho atual for uma instancia da classe trecho
                        else:
                            r, x = trecho.calcula_impedancia()
                            # calculo das potências dos nós de carga a jusante.
                        no.potencia_eq.real += r * (no_jus.potencia_eq.mod ** 2) / \
                            no_jus.tensao.mod ** 2
                        no.potencia_eq.imag += x * (no_jus.potencia_eq.mod ** 2) / \
                            no_jus.tensao.mod ** 2

        prof = 0
        # seção do cálculo de atualização das tensões
        while prof <= prof_max:
            # salva os nós de carga a montante
            nos = [alimentador.nos_de_carga[col_no_prof[1]]
                   for col_no_prof in rnp_alimentador.transpose()
                   if int(col_no_prof[0]) == prof + 1]
            # percorre os nós para guardar a árvore do nó requerido
            for no in nos:
                vizinhos = arvore_nos_de_carga[no.nome]
                # guarda os pares (profundidade,nó)
                no_prof = [col_no_prof
                           for col_no_prof in rnp_alimentador.transpose()
                           if col_no_prof[1] == no.nome]
                vizinhos_montante = list()
                # verifica quem é vizinho do nó desejado.
                for vizinho in vizinhos:
                    vizinho_prof = [viz_prof
                                    for viz_prof in rnp_alimentador.transpose()
                                    if viz_prof[1] == vizinho]
                    if int(vizinho_prof[0][0]) < int(no_prof[0][0]):
                        # armazena os vizinhos a montante.
                        vizinhos_montante.append(
                            alimentador.nos_de_carga[vizinho_prof[0][1]])
                # armazena o primeiro vizinho a montante
                no_mon = vizinhos_montante[0]
                trecho = self._busca_trecho(alimentador, no.nome, no_mon.nome)
                # se existir chave, soma a resistência dos dois trechos
                if not isinstance(trecho, Trecho):

                    r1, x1 = trecho[0].calcula_impedancia()
                    r2, x2 = trecho[1].calcula_impedancia()
                    r, x = r1 + r2, x1 + x2
                # caso não exista, a resistência é a do próprio trecho
                else:
                    r, x = trecho.calcula_impedancia()

                v_mon = no_mon.tensao.mod

                p = no.potencia_eq.real
                q = no.potencia_eq.imag

                # parcela de perdas
                p += r * (no.potencia_eq.mod ** 2) / no.tensao.mod ** 2
                q += x * (no.potencia_eq.mod ** 2) / no.tensao.mod ** 2

                v_jus = v_mon ** 2 - 2 * (r * p + x * q) + \
                    (r ** 2 + x ** 2) * (p ** 2 + q ** 2) / v_mon ** 2
                v_jus = np.sqrt(v_jus)

                k1 = (p * x - q * r) / v_mon
                k2 = v_mon - (p * r - q * x) / v_mon

                ang = no_mon.tensao.ang * np.pi / 180.0 - np.arctan(k1 / k2)

                no.tensao.mod = v_jus
                no.tensao.ang = ang * 180.0 / np.pi

                print 'Tensao do no {nome}: {tens}'.format(nome=no.nome, tens=no.tensao.mod/1e3)

                # calcula o fluxo de corrente passante no trecho
                corrente = no.tensao.real - no_mon.tensao.real
                corrente += (no.tensao.imag - no_mon.tensao.imag) * 1.0j
                corrente /= (r + x * 1.0j)
                # se houver chaves, ou seja, há dois trechos a mesma corrente
                # é atribuida
                if not isinstance(trecho, Trecho):
                    trecho[0].fluxo = Fasor(real=corrente.real,
                                            imag=corrente.imag,
                                            tipo=Fasor.Corrente)
                    trecho[1].fluxo = Fasor(real=corrente.real,
                                            imag=corrente.imag,
                                            tipo=Fasor.Corrente)
                else:
                    trecho.fluxo = Fasor(real=corrente.real,
                                         imag=corrente.imag,
                                         tipo=Fasor.Corrente)
            prof += 1

    def calcular_fluxo_de_carga(self):

        f1 = Fasor(mod=13.8e3, ang=0.0, tipo=Fasor.Tensao)
        self._atribuir_tensao_a_subestacao(f1)

        for alimentador in self.alimentadores.values():
            max_iteracaoes = 50
            criterio_converg = 0.001
            converg = 1e6
            iter = 0

            print '============================'
            print 'Varredura no alimentador {al}'.format(al=alimentador.nome)
            converg_nos = dict()
            for no in alimentador.nos_de_carga.values():
                converg_nos[no.nome] = 1e6

            while iter <= max_iteracaoes and converg > criterio_converg:
                iter += 1
                print '-------------------------'
                print 'Iteração: {iter}'.format(iter=iter)

                tensao_nos = dict()
                for no in alimentador.nos_de_carga.values():
                    tensao_nos[no.nome] = Fasor(real=no.tensao.real,
                                                imag=no.tensao.imag,
                                                tipo=Fasor.Tensao)

                self._varrer_alimentador(alimentador)

                for no in alimentador.nos_de_carga.values():
                    converg_nos[no.nome] = abs(tensao_nos[no.nome].mod -
                                               no.tensao.mod)

                converg = max(converg_nos.values())
                print 'Max. diferença de tensões: {conv}'.format(conv=converg)


class Trecho(Aresta):
    def __init__(self,
                 nome,
                 n1,
                 n2,
                 fluxo=None,
                 condutor=None,
                 comprimento=None):
        assert isinstance(nome, str), 'O parâmetro nome da classe Trecho ' \
                                      'deve ser do tipo str'
        assert isinstance(n1, NoDeCarga) or isinstance(n1, Chave), 'O parâmetro n1 da classe Trecho ' \
                                                                   'deve ser do tipo No de carga ' \
                                                                   'ou do tipo Chave'
        assert isinstance(n2, NoDeCarga) or isinstance(n2, Chave), 'O parâmetro n2 da classe Trecho ' \
                                                                   'deve ser do tipo No de carga ' \
                                                                   'ou do tipo Chave'

        super(Trecho, self).__init__(nome)
        self.n1 = n1
        self.n2 = n2
        self.no_montante = None
        self.no_jusante = None
        self.condutor = condutor
        self.comprimento = comprimento

        if fluxo is None:
            self.fluxo = Fasor(real=0.0, imag=0.0, tipo=Fasor.Corrente)
        else:
            self.fluxo = fluxo

    def calcula_impedancia(self):
        return (self.comprimento * self.condutor.rp / 1e3,
                self.comprimento * self.condutor.xp / 1e3)

    def __repr__(self):
        return 'Trecho: %s' % self.nome


class Alimentador(Arvore):
    def __init__(self, nome, setores, trechos, chaves):
        assert isinstance(nome, str), 'O parâmetro nome da classe Alimentador' \
                                      'deve ser do tipo string'
        assert isinstance(setores, list), 'O parâmetro setores da classe' \
                                          'Alimentador deve ser do tipo list'
        assert isinstance(chaves, list), 'O parâmetro chaves da classe' \
                                         'Alimentador deve ser do tipo list'
        self.nome = nome

        self.setores = dict()
        for setor in setores:
            self.setores[setor.nome] = setor

        self.chaves = dict()
        for chave in chaves:
            self.chaves[chave.nome] = chave

        self.nos_de_carga = dict()
        for setor in setores:
            for no in setor.nos_de_carga.values():
                self.nos_de_carga[no.nome] = no

        self.trechos = dict()
        for trecho in trechos:
            self.trechos[trecho.nome] = trecho

        for setor in self.setores.values():
            print 'Setor: ', setor.nome
            setores_vizinhos = list()
            for chave in self.chaves.values():
                if chave.n1 is setor:
                    setores_vizinhos.append(chave.n2)
                elif chave.n2 is setor:
                    setores_vizinhos.append(chave.n1)

            for setor_vizinho in setores_vizinhos:
                print 'Setor Vizinho: ', setor_vizinho.nome
                nos_de_ligacao = list()
                for i in setor.nos_de_carga.values():
                    for j in setor_vizinho.nos_de_carga.values():
                        if i.nome in j.vizinhos:
                            nos_de_ligacao.append((j, i))

                for no in nos_de_ligacao:
                    setor.ordenar(no[1].nome)
                    setor.rnp_associadas[setor_vizinho.nome] = (no[0],
                                                                setor.rnp)
                    print 'RNP: ', setor.rnp

        _arvore_da_rede = self._gera_arvore_da_rede()

        super(Alimentador, self).__init__(_arvore_da_rede, str)

    def ordenar(self, raiz):
        super(Alimentador, self).ordenar(raiz)

        for setor in self.setores.values():
            caminho = self.caminho_no_para_raiz(setor.nome)
            if setor.nome != raiz:
                setor_jusante = caminho[1, 1]
                setor.rnp = setor.rnp_associadas[setor_jusante][1]

    def _gera_arvore_da_rede(self):

        arvore_da_rede = {i: list() for i in self.setores.keys()}

        for chave in self.chaves.values():
            if chave.n1.nome in self.setores.keys() and chave.estado == 1:
                arvore_da_rede[chave.n1.nome].append(chave.n2.nome)
            if chave.n2.nome in self.setores.keys() and chave.estado == 1:
                arvore_da_rede[chave.n2.nome].append(chave.n1.nome)

        return arvore_da_rede

    def gerar_arvore_nos_de_carga(self):

        # define os nós de carga do setor raiz da subestação como os primeiros
        # nós de carga a povoarem a arvore nós de carga e a rnp nós de carga
        setor_raiz = self.setores[self.rnp[1][0]]
        self.arvore_nos_de_carga = Arvore(arvore=setor_raiz._gera_arvore_do_setor(),
                                          dtype=str)
        self.arvore_nos_de_carga.ordenar(raiz=setor_raiz.rnp[1][0])

        # define as listas visitados e pilha, necessárias ao
        # processo recursivo de visita
        # dos setores da subestação
        visitados = []
        pilha = []

        # inicia o processo iterativo de visita dos setores
        # em busca de seus respectivos nós de carga
        self._gerar_arvore_nos_de_carga(setor_raiz, visitados, pilha)

    def _gerar_arvore_nos_de_carga(self, setor, visitados, pilha):

        # atualiza as listas de recursão
        visitados.append(setor.nome)
        pilha.append(setor.nome)

        # for percorre os setores vizinhos ao setor atual
        # que ainda não tenham sido visitados
        vizinhos = setor.vizinhos
        for i in vizinhos:

            # esta condição testa se existe uma ligação
            # entre os setores de uma mesma subestação, mas
            # que possuem uma chave normalmente aberta entre eles.
            # caso isto seja constatado o laço for é interrompido.
            if i not in visitados and i in self.setores.keys():
                for c in self.chaves.values():
                    if c.n1.nome == setor.nome and c.n2.nome == i:
                        if c.estado == 1:
                            break
                        else:
                            pass
                    elif c.n2.nome == setor.nome and c.n1.nome == i:
                        if c.estado == 1:
                            break
                        else:
                            pass
                else:
                    continue
                prox = i
                setor_vizinho = self.setores[i]
                no_insersao, rnp_insersao = setor_vizinho.rnp_associadas[setor.nome]
                arvore_insersao = setor_vizinho._gera_arvore_do_setor()

                setor_vizinho.no_de_ligacao = no_insersao

                setor_vizinho.rnp = rnp_insersao

                self.arvore_nos_de_carga.inserir_ramo(no_insersao.nome,
                                                      (rnp_insersao,
                                                       arvore_insersao),
                                                      no_raiz=rnp_insersao[1, 0]
                                                      )
                break
            else:
                continue
        else:
            pilha.pop()
            if pilha:
                anter = pilha.pop()
                return self._gerar_arvore_nos_de_carga(self.setores[anter],
                                                       visitados, pilha)
            else:
                return
        return self._gerar_arvore_nos_de_carga(self.setores[prox],
                                               visitados,
                                               pilha)

    def atualizar_arvore_da_rede(self):
        _arvore_da_rede = self._gera_arvore_da_rede()
        self.arvore = _arvore_da_rede

    def gerar_trechos_da_rede(self):

        self.trechos = dict()

        j = 0
        for i in range(1, np.size(self.arvore_nos_de_carga.rnp, axis=1)):
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
                print 'Trecho: ' + n_1 + '-' + n_2

                # verifica quais os nós de carga existentes nas extremidades do trecho
                # e se existe uma chave no trecho

                for setor in self.setores.values():
                    if n_1 in setor.nos_de_carga.keys():
                        setor_1 = setor
                    if n_2 in setor.nos_de_carga.keys():
                        setor_2 = setor

                    if setor_1 is not None and setor_2 is not None:
                        break
                else:
                    if setor_1 is None:
                        n = n_1
                    else:
                        n = n_2
                    for setor in self.setores.values():
                        if n in setor.nos_de_carga.keys() and np.size(setor.rnp, axis=1) == 1:
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

    def calcular_potencia(self):
        potencia = Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia)
        for no in self.nos_de_carga.values():
            potencia = potencia + no.potencia

        return potencia

    def podar(self, no, alterar_rnp=False):
        poda = super(Alimentador, self).podar(no, alterar_rnp)
        rnp_setores = poda[0]
        arvore_setores = poda[1]

        if alterar_rnp:
            # for povoa dicionario com setores podados
            setores = dict()
            for i in rnp_setores[1, :]:
                setor = self.setores.pop(i)
                setores[setor.nome] = setor

            # for povoa dicionario com nos de carga podados
            nos_de_carga = dict()
            for setor in setores.values():
                for j in setor.nos_de_carga.values():
                    if j.nome in self.nos_de_carga.keys():
                        no_de_carga = self.nos_de_carga.pop(j.nome)
                        nos_de_carga[no_de_carga.nome] = no_de_carga

            # for atualiza a lista de nós de carga da subestação
            # excluindo os nós de carga podados
            for setor in self.setores.values():
                for no_de_carga in setor.nos_de_carga.values():
                    self.nos_de_carga[no_de_carga.nome] = no_de_carga
                    if no_de_carga.nome in nos_de_carga.keys():
                        nos_de_carga.pop(no_de_carga.nome)

            # poda o ramo na arvore da subetação
            poda = self.arvore_nos_de_carga.podar(setores[no].rnp[1, 0], alterar_rnp=alterar_rnp)
            rnp_nos_de_carga = poda[0]
            arvore_nos_de_carga = poda[1]

            # for povoa dicionario de chaves que estao nos trechos podados
            # e retira do dicionario de chaves da arvore que esta sofrendo a poda
            # as chaves que não fazem fronteira com os trechos remanescentes
            chaves = dict()
            for chave in self.chaves.values():
                if chave.n1.nome in setores.keys():
                    if not chave.n2.nome in self.setores.keys():
                        chaves[chave.nome] = self.chaves.pop(chave.nome)
                    else:
                        chave.estado = 0
                        chaves[chave.nome] = chave
                elif chave.n2.nome in setores.keys():
                    if not chave.n1.nome in self.setores.keys():
                        chaves[chave.nome] = self.chaves.pop(chave.nome)
                    else:
                        chave.estado = 0
                        chaves[chave.nome] = chave

            # for poda os trechos dos setores podados e povoa o dicionario trechos
            # para que possa ser repassado juntamente com os outros dados da poda
            trechos = dict()
            for no in rnp_nos_de_carga[1, :]:
                for trecho in self.trechos.values():
                    if trecho.n1.nome == no or trecho.n2.nome == no:
                        trechos[trecho.nome] = self.trechos.pop(trecho.nome)

            return (setores, arvore_setores, rnp_setores,
                    nos_de_carga, arvore_nos_de_carga, rnp_nos_de_carga,
                    chaves, trechos)
        else:
            return rnp_setores

    def inserir_ramo(self, no, poda, no_raiz=None):

        (setores, arvore_setores, rnp_setores,
         nos_de_carga, arvore_nos_de_carga, rnp_nos_de_carga,
         chaves, trechos) = poda

        if no_raiz is None:
            setor_inserir = setores[rnp_setores[1, 0]]
        else:
            setor_inserir = setores[no_raiz]

        setor_insersao = self.setores[no]

        # for identifica se existe alguma chave que permita a inserção do ramo na arvore
        # da subestação que ira receber a inserção.
        chaves_de_lig = dict()
        # for percorre os nos de carga do setor de insersão
        for i in self.setores[setor_insersao.nome].nos_de_carga.values():
            # for percorre as chaves associadas ao no de carga
            for j in i.chaves:
                # for percorre os nos de carga do setor raiz do ramo a ser inserido
                for w in setores[setor_inserir.nome].nos_de_carga.values():
                    # se a chave pertence aos nos de carga i e w então é uma chave de ligação
                    if j in w.chaves:
                        chaves_de_lig[j] = (i, w)

        if not chaves_de_lig:
            print 'A insersao não foi possível pois nenhuma chave de fronteira foi encontrada!'
            return

        i = randint(0, len(chaves_de_lig) - 1)
        n1, n2 = chaves_de_lig[chaves_de_lig.keys()[i]]

        self.chaves[chaves_de_lig.keys()[i]].estado = 1

        if setor_inserir.nome == setores[rnp_setores[1, 0]].nome:
            super(Alimentador, self).inserir_ramo(no, (rnp_setores, arvore_setores))
        else:
            super(Alimentador, self).inserir_ramo(no, (rnp_setores, arvore_setores), no_raiz)

        # atualiza setores do alimentador
        self.setores.update(setores)

        # atualiza os nos de carga do alimentador
        self.nos_de_carga.update(nos_de_carga)

        # atualiza as chaves do alimentador
        self.chaves.update(chaves)

        # atualiza os trechos do alimentador
        self.trechos.update(trechos)

        # atualiza a arvore de setores do alimentador
        self.atualizar_arvore_da_rede()

        # atualiza a arvore de nos de carga do alimentador
        self.gerar_arvore_nos_de_carga()


class Chave(Aresta):
    def __init__(self, nome, estado=1):
        assert estado == 1 or estado == 0, 'O parâmetro estado deve ser um inteiro de valor 1 ou 0'
        super(Chave, self).__init__(nome)
        self.estado = estado

    def __str__(self):
        if self.n1 is not None and self.n2 is not None:
            return 'Chave: %s - n1: %s, n2: %s' % (self.nome, self.n1.nome, self.n2.nome)
        else:
            return 'Chave: %s' % self.nome


class Transformador(object):
    def __init__(self, nome, tensao_primario, tensao_secundario, potencia, impedancia):
        assert isinstance(nome, str), 'O parâmetro nome deve ser do tipo str'
        assert isinstance(tensao_secundario, Fasor), 'O parâmetro tensao_secundario deve ser do tipo Fasor'
        assert isinstance(tensao_primario, Fasor), 'O parâmetro tensao_primario deve ser do tipo Fasor'
        assert isinstance(potencia, Fasor), 'O parâmetro potencia deve ser do tipo Fasor'
        assert isinstance(impedancia, Fasor), 'O parâmetro impedancia deve ser do tipo Fasor'

        self.nome = nome
        self.tensao_primario = tensao_primario
        self.tensao_secundario = tensao_secundario
        self.potencia = potencia
        self.impedancia = impedancia


class Condutor(object):
    def __init__(self, nome, rp, xp, rz, xz, ampacidade):
        self.nome = nome
        self.rp = float(rp)
        self.xp = float(xp)
        self.rz = float(rz)
        self.xz = float(xz)
        self.ampacidade = float(ampacidade)


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

    # Nos de carga do alimentador S1_AL1
    s1 = NoDeCarga(nome='S1',
                   vizinhos=['A2'],
                   potencia=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
                   chaves=['1'])
    a1 = NoDeCarga(nome='A1',
                   vizinhos=['A2'],
                   potencia=Fasor(real=160.0e3, imag=120.0e3, tipo=Fasor.Potencia))
    a2 = NoDeCarga(nome='A2',
                   vizinhos=['S1', 'A1', 'A3', 'C1'],
                   potencia=Fasor(real=150.0e3, imag=110.0e3, tipo=Fasor.Potencia),
                   chaves=['1', '3'])
    a3 = NoDeCarga(nome='A3',
                   vizinhos=['A2', 'B1'],
                   potencia=Fasor(real=100.0e3, imag=80.0e3, tipo=Fasor.Potencia),
                   chaves=['2'])
    b1 = NoDeCarga(nome='B1',
                   vizinhos=['B2', 'A3'],
                   potencia=Fasor(real=200.0e3, imag=140.0e3, tipo=Fasor.Potencia),
                   chaves=['2'])
    b2 = NoDeCarga(nome='B2',
                   vizinhos=['B1', 'B3', 'E2'],
                   potencia=Fasor(real=150.0e3, imag=110.0e3, tipo=Fasor.Potencia),
                   chaves=['4'])
    b3 = NoDeCarga(nome='B3',
                   vizinhos=['B2', 'C3'],
                   potencia=Fasor(real=100.0e3, imag=80.0e3, tipo=Fasor.Potencia),
                   chaves=['5'])
    c1 = NoDeCarga(nome='C1',
                   vizinhos=['C2', 'C3', 'A2'],
                   potencia=Fasor(real=200.0e3, imag=140.0e3, tipo=Fasor.Potencia),
                   chaves=['3'])
    c2 = NoDeCarga(nome='C2',
                   vizinhos=['C1'],
                   potencia=Fasor(real=150.0e3, imag=110.0e3, tipo=Fasor.Potencia))
    c3 = NoDeCarga(nome='C3',
                   vizinhos=['C1', 'E3', 'B3'],
                   potencia=Fasor(real=100.0e3, imag=80.0e3, tipo=Fasor.Potencia),
                   chaves=['5', '8'])

    # Nos de carga do alimentador S2_AL1
    s2 = NoDeCarga(nome='S2',
                   vizinhos=['D1'],
                   potencia=Fasor(real=0.0, imag=0.0, tipo=Fasor.Potencia),
                   chaves=['6'])
    d1 = NoDeCarga(nome='D1',
                   vizinhos=['S2', 'D2', 'D3', 'E1'],
                   potencia=Fasor(real=200.0e3, imag=160.0e3, tipo=Fasor.Potencia),
                   chaves=['6', '7'])
    d2 = NoDeCarga(nome='D2',
                   vizinhos=['D1'],
                   potencia=Fasor(real=90.0e3, imag=40.0e3, tipo=Fasor.Potencia))
    d3 = NoDeCarga(nome='D3',
                   vizinhos=['D1'],
                   potencia=Fasor(real=100.0e3, imag=80.0e3, tipo=Fasor.Potencia))
    e1 = NoDeCarga(nome='E1',
                   vizinhos=['E3', 'E2', 'D1'],
                   potencia=Fasor(real=100.0e3, imag=40.0e3, tipo=Fasor.Potencia),
                   chaves=['7'])
    e2 = NoDeCarga(nome='E2',
                   vizinhos=['E1', 'B2'],
                   potencia=Fasor(real=110.0e3, imag=70.0e3, tipo=Fasor.Potencia),
                   chaves=['4'])
    e3 = NoDeCarga(nome='E3',
                   vizinhos=['E1', 'C3'],
                   potencia=Fasor(real=150.0e3, imag=80.0e3, tipo=Fasor.Potencia),
                   chaves=['8'])

    cond_1 = Condutor(nome='CAA 266R', rp=0.2391, xp=0.37895, rz=0.41693, xz=1.55591, ampacidade=301)

    # Trechos do alimentador S1_AL1
    s1_ch1 = Trecho(nome='S1CH1', n1=s1, n2=ch1, condutor=cond_1, comprimento=0.01)

    ch1_a2 = Trecho(nome='CH1A2', n1=ch1, n2=a2, condutor=cond_1, comprimento=1.0)
    a2_a1 = Trecho(nome='A2A1', n1=a2, n2=a1, condutor=cond_1, comprimento=1.0)
    a2_a3 = Trecho(nome='A2A3', n1=a2, n2=a3, condutor=cond_1, comprimento=1.0)
    a2_ch3 = Trecho(nome='A2CH3', n1=a2, n2=ch3, condutor=cond_1, comprimento=0.5)
    a3_ch2 = Trecho(nome='A3CH2', n1=a3, n2=ch2, condutor=cond_1, comprimento=0.5)

    ch3_c1 = Trecho(nome='CH3C1', n1=ch3, n2=c1, condutor=cond_1, comprimento=0.5)
    c1_c2 = Trecho(nome='C1C2', n1=c1, n2=c2, condutor=cond_1, comprimento=1.0)
    c1_c3 = Trecho(nome='C1C3', n1=c1, n2=c3, condutor=cond_1, comprimento=1.0)
    c3_ch8 = Trecho(nome='C3CH8', n1=c3, n2=ch8, condutor=cond_1, comprimento=0.5)
    c3_ch5 = Trecho(nome='C3CH5', n1=c3, n2=ch5, condutor=cond_1, comprimento=0.5)

    ch2_b1 = Trecho(nome='CH2B1', n1=ch2, n2=b1, condutor=cond_1, comprimento=0.5)
    b1_b2 = Trecho(nome='B1B2', n1=b1, n2=b2, condutor=cond_1, comprimento=1.0)
    b2_ch4 = Trecho(nome='B2CH4', n1=b2, n2=ch4, condutor=cond_1, comprimento=0.5)
    b2_b3 = Trecho(nome='B2B3', n1=b2, n2=b3, condutor=cond_1, comprimento=1.0)
    b3_ch5 = Trecho(nome='B3CH5', n1=b3, n2=ch5, condutor=cond_1, comprimento=0.5)

    # Trechos do alimentador S2_AL1
    s2_ch6 = Trecho(nome='S2CH6', n1=s2, n2=ch6, condutor=cond_1, comprimento=0.01)

    ch6_d1 = Trecho(nome='CH6D1', n1=ch6, n2=d1, condutor=cond_1, comprimento=1.0)
    d1_d2 = Trecho(nome='D1D2', n1=d1, n2=d2, condutor=cond_1, comprimento=1.0)
    d1_d3 = Trecho(nome='D1D3', n1=d1, n2=d3, condutor=cond_1, comprimento=1.0)
    d1_ch7 = Trecho(nome='D1CH7', n1=d1, n2=ch7, condutor=cond_1, comprimento=0.5)

    ch7_e1 = Trecho(nome='CH7E1', n1=ch7, n2=e1, condutor=cond_1, comprimento=0.5)
    e1_e2 = Trecho(nome='E1E2', n1=e1, n2=e2, condutor=cond_1, comprimento=1.0)
    e2_ch4 = Trecho(nome='E2CH4', n1=e2, n2=ch4, condutor=cond_1, comprimento=0.5)
    e1_e3 = Trecho(nome='E1E3', n1=e1, n2=e3, condutor=cond_1, comprimento=1.0)
    e3_ch8 = Trecho(nome='E3CH8', n1=e3, n2=ch8, condutor=cond_1, comprimento=0.5)

    # Setor S1
    st1 = Setor(nome='S1',
                vizinhos=['A'],
                nos_de_carga=[s1])

    # setor A
    stA = Setor(nome='A',
                vizinhos=['S1', 'B', 'C'],
                nos_de_carga=[a1, a2, a3])

    # Setor B
    stB = Setor(nome='B',
                vizinhos=['A', 'C', 'E'],
                nos_de_carga=[b1, b2, b3])

    # Setor C
    stC = Setor(nome='C',
                vizinhos=['A', 'B', 'E'],
                nos_de_carga=[c1, c2, c3])

    # Setor S2
    st2 = Setor(nome='S2',
                vizinhos=['D'],
                nos_de_carga=[s2])

    # Setor D
    stD = Setor(nome='D',
                vizinhos=['S2', 'E'],
                nos_de_carga=[d1, d2, d3])

    # Setor E
    stE = Setor(nome='E',
                vizinhos=['D', 'B', 'C'],
                nos_de_carga=[e1, e2, e3])

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

    # Alimentador 1 de S1
    sub_1_al_1 = Alimentador(nome='S1_AL1',
                             setores=[st1, stA, stB, stC],
                             trechos=[s1_ch1, ch1_a2, a2_a1,
                                      a2_a3, a2_ch3, ch3_c1,
                                      c1_c2, c1_c3, c3_ch5,
                                      c3_ch8, a3_ch2, ch2_b1,
                                      b1_b2, b2_ch4, b2_b3,
                                      b3_ch5],
                             chaves=[ch1, ch2, ch3, ch4, ch5, ch8])

    # Alimentador 1 de S2
    sub_2_al_1 = Alimentador(nome='S2_AL1',
                             setores=[st2, stD, stE],
                             trechos=[s2_ch6, ch6_d1, d1_d2,
                                      d1_d3, d1_ch7, ch7_e1,
                                      e1_e2, e2_ch4, e1_e3,
                                      e3_ch8],
                             chaves=[ch6, ch7, ch4, ch8])

    t1 = Transformador(nome='S1_T1',
                       tensao_primario=Fasor(mod=69e3, ang=0.0, tipo=Fasor.Tensao),
                       tensao_secundario=Fasor(mod=13.8e3, ang=0.0, tipo=Fasor.Tensao),
                       potencia=Fasor(mod=10e6, ang=0.0, tipo=Fasor.Potencia),
                       impedancia=Fasor(real=0.5, imag=0.2, tipo=Fasor.Impedancia))

    t2 = Transformador(nome='S2_T1',
                       tensao_primario=Fasor(mod=69e3, ang=0.0, tipo=Fasor.Tensao),
                       tensao_secundario=Fasor(mod=13.8e3, ang=0.0, tipo=Fasor.Tensao),
                       potencia=Fasor(mod=10e6, ang=0.0, tipo=Fasor.Potencia),
                       impedancia=Fasor(real=0.5, imag=0.2, tipo=Fasor.Impedancia))

    sub_1 = Subestacao(nome='S1', alimentadores=[sub_1_al_1], transformadores=[t1])

    sub_2 = Subestacao(nome='S2', alimentadores=[sub_2_al_1], transformadores=[t2])

    _subestacoes = {sub_1_al_1.nome: sub_1_al_1, sub_2_al_1.nome: sub_2_al_1}

    sub_1_al_1.ordenar(raiz='S1')
    sub_2_al_1.ordenar(raiz='S2')

    sub_1_al_1.gerar_arvore_nos_de_carga()
    sub_2_al_1.gerar_arvore_nos_de_carga()

    # Imprime a representação de todos os setores da subestção
    # na representação
    # nó profundidade
    # print sub1.rnp

    # print sub1.arvore_nos_de_carga.arvore

    # imprime as rnp dos setores de S1
    # for setor in _sub_1.setores.values():
    # print 'setor: ', setor.nome
    # print setor.rnp

    # imprime as rnp dos setores de S2
    # for setor in _sub_2.setores.values():
    # print 'setor: ', setor.nome
    # print setor.rnp

    # _subestacoes['S1'].gera_trechos_da_rede()

    # imprime os trechos da rede S1
    # for trecho in _sub_1.trechos.values():
    #    print trecho
