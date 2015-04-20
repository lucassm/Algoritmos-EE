from rnp import Arvore

nos_arvore_1 = {1: [4],
                4: [1, 5, 10],
                5: [4, 6],
                6: [5],
                10: [4, 16, 11],
                16: [10, 22, 23],
                23: [16],
                22: [16],
                11: [10, 12],
                12: [11]}

nos_arvore_2 = {2: [9],
                9: [2, 15, 8],
                15: [9, 14],
                14: [15],
                8: [9, 7, 13],
                13: [8],
                7: [8]}

nos_arvore_3 = {3: [27],
                27: [3, 21, 26],
                21: [27, 20],
                20: [21],
                26: [27, 25, 19],
                25: [26, 24],
                24: [25],
                19: [26, 18],
                18: [19, 17],
                17: [18]}

arvore_1 = Arvore(nos_arvore_1)
arvore_1.ordenar(raiz=1)

arvore_2 = Arvore(nos_arvore_2)
arvore_2.ordenar(raiz=2)

arvore_3 = Arvore(nos_arvore_3)
arvore_3.ordenar(raiz=3)

arvore_1.caminho_no_para_no(12, 23)