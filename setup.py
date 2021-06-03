from setuptools import setup, find_packages

setup(
    name='cli-pat',
    version='0.1.0',
    packages=find_packages(include=['cli-pat', 'modules.*']),
    install_requires= [
	'pick',
	'configparser==4.0.2',
	'prettytable==1.0.1'], 
    #scripts=['run/proxy-install'],
    entry_points = {
        'console_scripts': ['cli-proxy=modules.cli:main'],
    }
)
