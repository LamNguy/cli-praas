from setuptools import setup, find_packages
with open ("README.md", "r") as f:
	readme = f.read()

setup(
    name='cli-proxy-openstack',
    version='0.1.4',
    author='Nguyen Duc Lam',
    author_email='lamchipabc@gmail.com',
    description='CLI for Proxy Service integrated with OpenStack',
    long_description_content_type="text/markdown",
    url = 'https://github.com/LamNguy/cli-praas',
    python_requires='>=2.7',
    packages=find_packages(),
    include_package_data=True,
    install_requires= [
	'pick',
	'pbr',
	'configparser',
	'prettytable',
	'openstacksdk==0.36.5'], 
    entry_points = {
        'console_scripts': ['cli-proxy=cli.__main__:main'],
    }
)
