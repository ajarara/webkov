from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='webkov',

    version='0.2.8',
    author='Ahmad Jarara',
    author_email='ajarara94@gmail.com',
    url='shakespeare.jarmac.org',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Me',
        'Topic :: IoT :: Private Interface',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],

    packages=find_packages(),

    include_package_data=True,
    package_data={'webkov': ['full.html']},

    # install_requires=["aiohttp"],

    entry_points={
        'console_scripts': [
            'shakespeare=webkov.server:main',
        ],
    },
)
