"""setup.py file for packaging ``amti``"""

from setuptools import setup, find_packages


with open('readme.md', 'r') as readme_file:
    readme = readme_file.read()


setup(
    name='amti',
    version='0.0.2',
    description="A Mechanical Turk Interface",
    long_description=readme,
    url='http://github.com/allenai/amti',
    author='Allen Institute for Artificial Intelligence',
    author_email='alexandria@allenai.org',
    keywords='amti mechanical turk mturk crowdsourcing',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence'
    ],
    license='Apache',
    packages=find_packages(),
    install_requires=[
        'boto3 >= 1.5.29',
        'click >= 6.7',
        'Jinja2 >= 2.10'
    ],
    python_requires='>=3.6',
    scripts=[
        'scripts/amti'
    ],
    zip_safe=False
)
