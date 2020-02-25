from setuptools import setup, find_packages, Command

# Load text for description and license
with open('README.md') as f:
    readme = f.read()

# Go!
setup(
    # Module name (lowercase)
    name='PKPD',
    version='0.0.2dev0',

    # Description
    description='Pharmacokinetics and pharmacodynamics modelling interface.',
    long_description=readme,

    # License name
    license='BSD 3-clause license',

    # Maintainer information
    maintainer='David Augustin, Rebecca Rumney, Barnum Swannell, Simon Marchant',
    maintainer_email='david.augustin@dtc.ox.ac.uk',
    url='https://github.com/SABS-R3-projects/PKPD.git',

    # Packages to include
    packages=find_packages(include=('PKPD','PKPD.*')),

    # List of dependencies
    install_requires=[
        'cma>=2',
        'numpy>=1.8',
        'scipy>=0.14',
        'pyqt5==5.9',
        'sympy',
        'matplotlib>=1.5',
        'myokit>=1.29',
        'tabulate',
        'pandas',
        'pints @ git+git://github.com/pints-team/pints.git#egg=pints'
    ],
    dependency_links=[
     "git+git://github.com/pints-team/pints.git#egg=pints-0.2.2",
    ]
)