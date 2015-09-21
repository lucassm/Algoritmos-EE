from setuptools import setup, find_packages

setup(name = 'rede',
      version = '1.0',
      description = 'Funcionalidades para representacao da rede eletrica utilizando grafos com representacao no-profundidade',
      install_requires = ['numpy==1.8.2', 'terminaltables'],
      author = 'Lucas S Melo',
      packages = find_packages(),
      )
