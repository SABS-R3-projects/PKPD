import os
import distutils
from setuptools import setup, find_packages, Command
from setuptools.command.build_py import build_py

# Load text for description and license
with open('README.md') as f:
    readme = f.read()

class BuildPyCommand(build_py):
  """Custom build command."""

  def run(self):
    self.run_command('pints')
    build_py.run(self)


class PINTS_installer(Command):
    """A costum command to install PINTS in the process of setting up the PKPD module.
    """
    description = ('Clones and pip installs PINTS.')

    def initialize_options(self) -> None:
        self.commands = []

    def finalize_options(self) -> None:
        self.commands = [
            'git clone https://github.com/pints-team/pints.git',
            'pip install pints/']

    def run(self):
        """Run commands.
        """
        git_clone_cmd = self.commands[0]
        pip_install_cmd = self.commands[1]

        # clone PINTS repository.
        if os.path.isdir('pints'):
            self.announce(
                'PINTS repository exists in directory',
                level=distutils.log.INFO)
        elif not os.path.isfile('./pints'):
            self.announce(
                'Running command: %s' % str(git_clone_cmd),
                level=distutils.log.INFO)
            os.system(git_clone_cmd)

        # pip install PINTS
        os.system(pip_install_cmd)

# Go!
setup(
    # Module name (lowercase)
    name='PKPD',
    version='0.1dev',

    # Description
    description='Pharmacokinetics and pharmacodynamics modelling interface.',
    long_description=readme,

    # License name
    license='BSD 3-clause license',

    # Maintainer information
    maintainer='David Augustin, Rebecca Rumney, Barnum Swannell, Simon Marchant',
    maintainer_email='david.augustin@dtc.ox.ac.uk',
    url='https://github.com/SABS-R3-projects/PKPD.git',

    # customised commands
    cmdclass={
        'pints': PINTS_installer,
        'build_py': BuildPyCommand
    },

    # Packages to include
    packages=find_packages(include=('PKPD',)),

    # install PINTS
    #scripts=['setup_scripts/install_pints.py'],

    # List of dependencies
    install_requires=[
        'cma>=2',
        'numpy>=1.8',
        'scipy>=0.14',
        'pyqt5>=5.9',
        'sympy',
        'matplotlib>=1.5',
        'libsundials-dev',
        'myokit>=1.29',
        'tabulate',

    ]
)