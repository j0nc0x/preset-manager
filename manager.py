import hou
import os
import time
import datetime
import getpass
import subprocess


class PresetManager(object):
    def __init__(self, _node):
        self.temp = None
        self.preset_node = _node
        self.local_presets = list()
        self.remote_presets = list()

    def is_valid(self):
        """
        Check if the preset manager has a valid node as an input

        :return:        Is valid?
        :type:          bool
        """
        if self.preset_node and issubclass(type(self.preset_node), hou.Node):
            return True
        else:
            return False

    def get_node_type(self, string=True):
        """
        Find the node type for the given node

        :param string:  Should the result be returned as a string, otherwise return the Houdini object
        :type string:   bool
        :return:        The node type
        :type:          hou.NodeType
        """
        if self.is_valid():
            if string:
                return self.preset_node.type().name()
            else:
                return self.preset_node.type()

    def get_node_type_category(self, string=True):
        """
        Find the node type category for the given node

        :param string:  Should the result be returned as a string, otherwise return the Houdini object
        :type string:   bool
        :return:        The node type category
        :type:          hou.NodeTypeCategory
        """
        if self.is_valid():
            if string:
                return self.get_node_type(string=False).category().name()
            else:
                return self.get_node_type(string=False).category()

    def local_preset_path(self):
        """
        The path on disk of the local preset for the given node if it exists

        :return:        The path on disk to the preset
        :type:          str
        """
        if self.is_valid():
            prefs = os.getenv('HOUDINI_USER_PREF_DIR')
            preset_path = '{prefs}/presets/{category}/{type}.idx'.format(prefs=prefs,
                                                                         category=self.get_node_type_category(),
                                                                         type=self.get_node_type())

            if os.path.isfile(preset_path):
                return preset_path

    def remote_preset_path(self):
        """
        The path on disk of the remote preset for the given node if it exists

        :return:        The path on disk to the preset
        :type:          str
        """
        if self.is_valid():
            prefs = os.getenv('PRESET_REPO')
            preset_path = '{prefs}/presets/{category}/{type}.idx'.format(prefs=prefs,
                                                                         category=self.get_node_type_category(),
                                                                         type=self.get_node_type())

            if os.path.isfile(preset_path):
                return preset_path

    def setup_tmp_dir(self):
        """
        Generate a temp directory on disk that we can use to work in
        """
        # Generate the timestamp
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d_%H_%M_%S')
        self.temp = '/tmp/{user}_{stamp}'.format(user=getpass.getuser(),
                                               stamp=st)

        # create the directory
        if not os.path.exists(self.temp):
            os.makedirs(self.temp)

    def extactAllPresets(self):
        """
        Extract all the presets into our temporary working area
        :return:
        """
        # Make sure we have a valid temp directory
        if not self.temp:
            self.setup_tmp_dir()

        # First lets extract the local presets
        local_dir = '{temp}/local'.format(temp=self.temp)
        os.makedirs(local_dir)

        # Now extract the presets into this directory (if any presets exist)
        if self.local_preset_path():
            cmd_list = ['hidx', '-x', local_dir, self.local_preset_path()]
            subprocess.call(cmd_list)
            print 'Local presets for {category}/{type} ' \
                  'extracted to {path}'.format(category=self.get_node_type_category(),
                                               type=self.get_node_type(),
                                               path=local_dir)
        else:
            print 'No local presets for {category}/{type} found'.format(category=self.get_node_type_category(),
                                                                        type=self.get_node_type())

        # Now lets extract the remote presets
        remote_dir = '{temp}/remote'.format(temp=self.temp)
        os.makedirs(remote_dir)

        # Now extract the presets into this directory (if any presets exist)
        if self.remote_preset_path():
            cmd_list = ['hidx', '-x', remote_dir, self.remote_preset_path()]
            subprocess.call(cmd_list)
            print 'Remote preset for {category}/{type} ' \
                  'extracted to {path}'.format(category=self.get_node_type_category(),
                                               type=self.get_node_type(),
                                               path=remote_dir)
        else:
            print 'No remote presets for {category}/{type} found'.format(category=self.get_node_type_category(),
                                                                         type=self.get_node_type())
