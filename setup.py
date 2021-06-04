from setuptools import setup, find_packages
with open ("README.md", "r") as f:
	long_description = f.read()

setup(
    name='CLI Proxy Service',
    version='0.1.1',
    author='Nguyen Duc Lam',
    author_email='lamchipabc@gmail.com',
    description='CLI for Proxy Service integrated with OpenStack',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = 'https://github.com/LamNguy/cli_pat',
    python_requires='>=2.7',
    packages=find_packages(include=['cli-pat', 'modules.*']),
    install_requires= [
	'pick',
	'pbr>=2.0.0',
	'configparser',
	'prettytable',
	'openstacksdk==0.36.5'], 
    #scripts=['run/proxy-install'],
    entry_points = {
        'console_scripts': ['cli-proxy=modules.cli:main'],
    }
)
