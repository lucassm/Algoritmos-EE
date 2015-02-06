# coding=utf-8
from rede import *
import numpy as np


def busca_trecho(alimentador, n1, n2):
    # for pecorre os nos de carga do alimentador
    for no in alimentador.nos_de_carga.keys():

        # cria conjuntos das chaves ligadas ao no
        chaves_n1 = set(alimentador.nos_de_carga[n1].chaves)
        chaves_n2 = set(alimentador.nos_de_carga[n2].chaves)

        # verifica se existem chaves comuns aos nos
        chaves_intersec = chaves_n1.intersection(chaves_n2)

        if chaves_intersec != set():
            # verifica quais trechos estão ligados a chave
            # comum aos nos i e j
            chave = chaves_intersec.pop()
            trechos_ch = []
            for trecho in alimentador.trechos.values():
                if trecho.n1.nome == chave:
                    if trecho.n2.nome == n1 or trecho.n2.nome == n2:
                        trechos_ch.append(trecho)
                elif trecho.n2.nome == chave:
                    if trecho.n1.nome == n1 or trecho.n1.nome == n2:
                        trechos_ch.append(trecho)

            if len(trechos_ch) == 2:
                return trechos_ch
        else:
            # se não existirem chaves comuns, verifica qual trecho
            # tem os nos i e j como extremidade
            for trecho in alimentador.trechos.values():
                if trecho.n1.nome == n1:
                    if trecho.n2.nome == n2:
                        return trecho
                elif trecho.n1.nome == n2:
                    if trecho.n2.nome == n1:
                        return trecho


def atribuir_tensao_a_subestacao(subestacao, tensao):
    for alimentador in subestacao.alimentadores.values():
        for no in alimentador.nos_de_carga.values():
            no.tensao = Fasor(real=tensao.real,
                              imag=tensao.imag,
                              tipo=Fasor.Tensao)


def varrer_alimentador(alimentador):
    nos_alimentador = alimentador.nos_de_carga.values()
    rnp_alimentador = alimentador.arvore_nos_de_carga.rnp
    arvore_nos_de_carga = alimentador.arvore_nos_de_carga.arvore
    no_max, prof_max = None, 0

    for no_prof in rnp_alimentador.transpose():
        nos_alimentador_nomes = [no.nome for no in nos_alimentador]

        if int(no_prof[0]) > prof_max and no_prof[1] in nos_alimentador_nomes:
            no_max = no_prof[1]
            prof_max = int(no_prof[0])

    prof = prof_max

    while prof >= 0:
        nos = [alimentador.nos_de_carga[no_prof[1]] for no_prof in rnp_alimentador.transpose() if
               int(no_prof[0]) == prof]
        prof -= 1

        for no in nos:
            no.potencia_eq.real = 0.0
            no.potencia_eq.imag = 0.0

            vizinhos = arvore_nos_de_carga[no.nome]

            no_prof = [no_prof for no_prof in rnp_alimentador.transpose() if no_prof[1] == no.nome]
            vizinhos_jusante = list()

            for vizinho in vizinhos:
                vizinho_prof = [viz_prof for viz_prof in rnp_alimentador.transpose() if viz_prof[1] == vizinho]
                if int(vizinho_prof[0][0]) > int(no_prof[0][0]):
                    vizinhos_jusante.append(alimentador.nos_de_carga[vizinho_prof[0][1]])

            if vizinhos_jusante == []:
                no.potencia_eq.real += no.potencia.real
                no.potencia_eq.imag += no.potencia.imag
            else:
                no.potencia_eq.real += no.potencia.real
                no.potencia_eq.imag += no.potencia.imag

                for no_jus in vizinhos_jusante:
                    no.potencia_eq.real += no_jus.potencia_eq.real
                    no.potencia_eq.imag += no_jus.potencia_eq.imag

                    trecho = busca_trecho(alimentador, no.nome, no_jus.nome)
                    if not isinstance(trecho, Trecho):

                        r1, x1 = trecho[0].calcula_impedancia()
                        r2, x2 = trecho[1].calcula_impedancia()
                        r, x = r1 + r2, x1 + x2

                    else:
                        r, x = trecho.calcula_impedancia()

                    no.potencia_eq.real += r * (no_jus.potencia_eq.mod ** 2) / no_jus.tensao.mod ** 2
                    no.potencia_eq.imag += x * (no_jus.potencia_eq.mod ** 2) / no_jus.tensao.mod ** 2

    prof = 0

    while prof <= prof_max:
        nos = [alimentador.nos_de_carga[no_prof[1]] for no_prof in rnp_alimentador.transpose() if
               int(no_prof[0]) == prof + 1]

        for no in nos:
            vizinhos = arvore_nos_de_carga[no.nome]

            no_prof = [no_prof for no_prof in rnp_alimentador.transpose() if no_prof[1] == no.nome]
            vizinhos_montante = list()

            for vizinho in vizinhos:
                vizinho_prof = [viz_prof for viz_prof in rnp_alimentador.transpose() if viz_prof[1] == vizinho]
                if int(vizinho_prof[0][0]) < int(no_prof[0][0]):
                    vizinhos_montante.append(alimentador.nos_de_carga[vizinho_prof[0][1]])

            no_mon = vizinhos_montante[0]
            trecho = busca_trecho(alimentador, no.nome, no_mon.nome)

            if not isinstance(trecho, Trecho):

                r1, x1 = trecho[0].calcula_impedancia()
                r2, x2 = trecho[1].calcula_impedancia()
                r, x = r1 + r2, x1 + x2

            else:
                r, x = trecho.calcula_impedancia()

            v_mon = no_mon.tensao.mod
            p = no_mon.potencia_eq.real
            q = no_mon.potencia_eq.imag

            v_jus = v_mon**2 - 2*(r*p + x*q) + (r**2 + x**2)*(p**2 + q**2)/v_mon**2
            v_jus = np.sqrt(v_jus)

            k1 = (p*x - q*r)/v_mon
            k2 = v_mon - (p*r - q*x)/v_mon

            ang = no_mon.tensao.ang * np.pi/180.0 - np.arctan(k1/k2)

            no.tensao.mod = v_jus
            no.tensao.ang = ang * 180.0/np.pi

        prof += 1


def calcula_fluxo(alimentador):

    max_iteracaoes = 50
    criterio_converg = 0.001
    converg = 1e6
    iter = 0

    f1 = Fasor(mod=13.8e3, ang=0.0, tipo=Fasor.Tensao)
    atribuir_tensao_a_subestacao(sub_1, f1)

    converg_nos = dict()
    for no in alimentador.nos_de_carga.values():
        converg_nos[no.nome] = 1e6

    while iter <= max_iteracaoes and converg > criterio_converg:
        iter += 1
        print '========================'
        print 'Iteração: {iter}'.format(iter=iter)

        tensao_nos = dict()
        for no in alimentador.nos_de_carga.values():
            tensao_nos[no.nome] = Fasor(real=no.tensao.real,
                                        imag=no.tensao.imag,
                                        tipo=Fasor.Tensao)

        varrer_alimentador(alimentador)

        for no in alimentador.nos_de_carga.values():
            converg_nos[no.nome] = abs(tensao_nos[no.nome].mod - no.tensao.mod)

        converg = max(converg_nos.values())
        print 'Máxima diferença de tensões: {converg}'.format(converg=converg)


if __name__ == '__main__':
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
