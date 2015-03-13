"""
Python Blueprint
================

Does not install python itself, only develop and setup tools.
Contains pip helper for other blueprints to use.

**Fabric environment:**

.. code-block:: yaml

    blueprints:
      - blues.python

"""
from fabric.decorators import task

from refabric.api import run, info
from refabric.context_managers import sudo
from refabric.contrib import blueprints

from . import debian

__all__ = ['setup', 'requested_version']


pip_log_file = '/tmp/pip.log'
blueprint = blueprints.get(__name__)


def requested_version():
    ver = blueprint.get('version', '2.7')  # Default to python 2.7
    return tuple(map(int, ver.split('.')))[:2]


@task
def setup():
    """
    Install python develop tools
    """
    install()


@task
def version():
    if not hasattr(version, 'version'):
        version_string = run('python --version').stdout
        _, ver = version_string.split(' ')
        version.version = tuple(map(int, ver.split('.')))

    return version.version


def install():
    with sudo():
        info('Install python dependencies')

        req_ver = requested_version()

        if req_ver < (3, 0):
            debian.apt_get('install', 'python-dev', 'python-setuptools')
        else:
            v_milestone = '.'.join(map(str, req_ver[:2]))
            v_major = str(req_ver[0])

            def py_pkg(ver, suffix=''):
                return 'python' + ver + suffix

            debian.apt_get('install',
                           py_pkg(v_milestone),
                           py_pkg(v_milestone, '-dev'),
                           py_pkg(v_major, '-pip'))

        run('easy_install pip')

        run('touch {}'.format(pip_log_file))
        debian.chmod(pip_log_file, mode=777)
        pip('install', 'setuptools', '--upgrade')


def pip(command, *options):
    info('Running pip {}', command)
    run('pip {0} {1} -v --log={2} --log-file={2}'\
        .format(
            command,
            ' '.join(options),
            pip_log_file))
