import os

from fabric.context_managers import settings
from fabric.state import env

from blues import debian
from blues import supervisor

from .base import BaseProvider
from .. import blueprint
from ..project import *


class SupervisorProvider(BaseProvider):

    def get_config_path(self):
        """
        Get or create Supervisor project programs home dir.

        :return: Remote config path
        """
        destination = os.path.join(project_home(), 'supervisor.d', '')
        debian.mkdir(destination)
        return destination

    def upload_web_config(self):
        """
        TODO: Render and upload web program to projects Supervisor home dir.

        :return: Updated programs
        """
        raise NotImplementedError('Supervisor provider not yet implements web workers.')

    def upload_worker_config(self):
        """
        Render and upload worker program(s) to projects Supervisor home dir.

        :return: Updated programs
        """
        destination = self.get_config_path()
        context = super(SupervisorProvider, self).get_context()
        context.update({
            'workers': blueprint.get('worker.workers', debian.nproc()),
        })

        # Override context defaults with blueprint settings
        context.update(blueprint.get('worker'))

        # Filter program extensions by host
        programs = ['celery.conf']
        extensions = blueprint.get('worker.celery.extensions')
        if isinstance(extensions, list):
            for extension in extensions:
                programs.append('{}.conf'.format(extension))
        else:
            for extension, extension_host in extensions.items():
                if extension_host in ('*', env.host_string):
                    programs.append('{}.conf'.format(extension))

        # Upload programs
        for program in programs:
            template = os.path.join('supervisor', 'default', program)
            default_templates = supervisor.blueprint.get_default_template_root()
            with settings(template_dirs=[default_templates]):
                uploads = blueprint.upload(template, destination, context=context)
            self.updates.extend(uploads)

        return self.updates

    def reload(self):
        supervisor.reload()