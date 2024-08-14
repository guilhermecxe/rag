from setuptools import setup, find_packages

# Lendo a lista de pacotes
with open('requirements.txt', 'r', encoding='utf-16') as f:
    required = f.read().splitlines()

# Removendo os pacotes de desenvolvimento
dev_packages = ['pytest']
required = list(filter(lambda p: not (p.split('==')[0] in dev_packages), required))

setup(
    author="Guilherme Alves",
    description="",
    name="rag",
    version="0.0.15",
    packages=find_packages(include=["rag"]),
    python_requires='>=3.10',
    install_requires=required,
)