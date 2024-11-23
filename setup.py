from setuptools import setup, find_packages

setup(
    name='kgraphmemory',
    version='0.0.6',
    author='Marc Hadfield',
    author_email='marc@vital.ai',
    description='KGraph Memory',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/vital-ai/kgraphmemory',
    packages=find_packages(exclude=["test"]),
    license='Apache License 2.0',
    install_requires=[
            'vital-ai-vitalsigns>=0.1.26',
            'vital-ai-domain>=0.1.6',
            'six',
            'pyyaml',
            'vital-ai-haley-kg>=0.1.4',
            'rdflib==7.0.0',
            'SPARQLWrapper>=2.0.0',
            'networkx',
            'matplotlib',
            # 'transformers==4.41.2',
            'kgraphservice>=0.0.7'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)

