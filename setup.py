"""setup.py file for packaging amti."""

from setuptools import setup


with open('readme.md', 'r') as readme_file:
    readme = readme_file.read()


setup(
    name='amti',
    version='0.0.2',
    description="A Mechanical Turk Interface",
    long_description=readme,
    url='http://github.com/allenai/amti',
    author='Nicholas Lourie',
    author_email='nicholasl@collaborator.allenai.org',
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
    packages=['amti'],
    install_requires=[
        'Jinja2 >= 2.11.2',
        'boto3 >= 1.12.39',
        'click >= 7.1.1'
    ],
    python_requires='>=3.6',
    scripts=[
        'scripts/amti'
    ],
    zip_safe=False
)
