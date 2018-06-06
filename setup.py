from setuptools import (
    find_packages,
    setup,
)

setup(
    name='azban.utils',
    version='0.0.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    extras_require={
        'flask': [
            'flask==1.0.2',
            'schematics==2.0.1',
        ],
    },
)
