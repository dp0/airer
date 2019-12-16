from setuptools import setup

setup(
    name='Airer',
    version='0.1dev',
    packages=['airer'],
    license='BSD 3-Clause',
    long_description=open('README.md').read(),

    tests_require=['pytest'],
    setup_requires=['wheel', 'pytest-runner'],
    install_requires=['pyserial'],
)
