from fabric.state import env

from ..project import *

from ... import debian
from ...app import blueprint

from . import get_manager


class BaseProvider(object):
    def __init__(self):
        self.updates = []
        self.project = blueprint.get('project')

    def install(self):
        """
        Install provider.
        """
        raise NotImplementedError

    def get_config_path(self):
        """
        Get or create remote provider config home dir.

        :return: Remote config path
        """
        raise NotImplementedError

    def get_context(self):
        """
        Build Jinja2 context for provider config templates.

        :return: context dict
        """
        context = {
            'chdir': python_path(),
            'virtualenv': virtualenv_path(),
            'current_host': env.host_string
        }

        owner = debian.get_user(self.project)
        context.update(owner)  # name, uid, gid, ...

        return context

    def configure_web(self):
        """
        Render and upload provider web config files.

        :return: Updated config files
        """
        raise NotImplementedError

    def configure_worker(self):
        """
        Render and upload provider worker config files.

        :return: Updated config files
        """
        raise NotImplementedError

    def reload(self):
        """
        Reload provider configuration
        """
        pass


class ManagedProvider(BaseProvider):
    def __init__(self, manager=None, *args, **kw):
        super(ManagedProvider, self).__init__(*args, **kw)

        if not hasattr(self, 'default_manager'):
            raise AttributeError('%s has no default_manager attribute.' %
                                 self.__class__)

        if manager is None:
            manager = self.default_manager

        self.manager = get_manager(manager)


class BaseManager(BaseProvider):
    def configure_provider(self, provider, context, program_name=None):
        """
        This method is called from providers in order to upload their
        run configuration to the manager.
        :param provider: The provider's instance
        :param context: Template context
        :param program_name: Optional program name, to avoid collisions if
        you have multiple instances of the same provider running under the
        same manager.
        :return:
        """
        raise NotImplementedError('managers usually need to implement a '
                                  'configure_provider method.')