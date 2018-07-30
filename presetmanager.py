import hou
import os
import shutil
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

        # First extract the presets so we can analyse them
        self._extract_all_presets()
        self._analyse_presets()

    def _is_valid(self):
        """
        Check if the preset manager has a valid node as an input

        :return:        Is valid?
        :type:          bool
        """
        if self.preset_node and issubclass(type(self.preset_node), hou.Node):
            return True
        else:
            return False

    def _get_node_type(self, string=True):
        """
        Find the node type for the given node

        :param string:  Should the result be returned as a string, otherwise return the Houdini object
        :type string:   bool
        :return:        The node type
        :type:          hou.NodeType
        """
        if self._is_valid():
            if string:
                return self.preset_node.type().name()
            else:
                return self.preset_node.type()

    def _get_node_type_category(self, string=True):
        """
        Find the node type category for the given node

        :param string:  Should the result be returned as a string, otherwise return the Houdini object
        :type string:   bool
        :return:        The node type category
        :type:          hou.NodeTypeCategory
        """
        if self._is_valid():
            if string:
                return self._get_node_type(string=False).category().name()
            else:
                return self._get_node_type(string=False).category()

    def _local_preset_path(self):
        """
        The path on disk of the local preset for the given node if it exists

        :return:        The path on disk to the preset
        :type:          str
        """
        if self._is_valid():
            prefs = os.getenv('HOUDINI_USER_PREF_DIR')
            preset_path = '{prefs}/presets/{category}/{type}.idx'.format(prefs=prefs,
                                                                         category=self._get_node_type_category(),
                                                                         type=self._get_node_type())

            if os.path.isfile(preset_path):
                return preset_path

    def _remote_preset_path(self):
        """
        The path on disk of the remote preset for the given node if it exists

        :return:        The path on disk to the preset
        :type:          str
        """
        if self._is_valid():
            prefs = os.getenv('PRESET_REPO')
            preset_path = '{prefs}/{category}/{type}.idx'.format(prefs=prefs,
                                                                 category=self._get_node_type_category(),
                                                                 type=self._get_node_type())

            if os.path.isfile(preset_path):
                return preset_path

    def _setup_tmp_dir(self):
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

    def _extract_all_presets(self):
        """
        Extract all the presets into our temporary working area
        :return:
        """
        # Make sure we have a valid temp directory
        if not self.temp:
            self._setup_tmp_dir()

        # First lets extract the local presets
        local_dir = '{temp}/local'.format(temp=self.temp)
        os.makedirs(local_dir)

        # Now extract the presets into this directory (if any presets exist)
        if self._local_preset_path():
            cmd_list = ['hidx', '-x', local_dir, self._local_preset_path()]
            subprocess.call(cmd_list)
            print 'Local presets for {category}/{type} ' \
                  'extracted to {path}'.format(category=self._get_node_type_category(),
                                               type=self._get_node_type(),
                                               path=local_dir)
        else:
            print 'No local presets for {category}/{type} found'.format(category=self._get_node_type_category(),
                                                                        type=self._get_node_type())

        # Now lets extract the remote presets
        remote_dir = '{temp}/remote'.format(temp=self.temp)
        os.makedirs(remote_dir)

        # Now extract the presets into this directory (if any presets exist)
        if self._remote_preset_path():
            cmd_list = ['hidx', '-x', remote_dir, self._remote_preset_path()]
            subprocess.call(cmd_list)
            print 'Remote preset for {category}/{type} ' \
                  'extracted to {path}'.format(category=self._get_node_type_category(),
                                               type=self._get_node_type(),
                                               path=remote_dir)
        else:
            print 'No remote presets for {category}/{type} found'.format(category=self._get_node_type_category(),
                                                                         type=self._get_node_type())

    def _analyse_presets(self):
        """
        Analyse all the presets available for the given node and use them to populate the local and remote presets list
        """
        local_dir = '{temp}/local'.format(temp=self.temp)
        if os.path.exists(local_dir):
            self.local_presets = os.listdir(local_dir)
        # Make sure we have just the presets, not the index
        if 'Sections.list' in self.local_presets:
            self.local_presets.remove('Sections.list')

        remote_dir = '{temp}/remote'.format(temp=self.temp)
        if os.path.exists(remote_dir):
            self.remote_presets = os.listdir(remote_dir)
        # Make sure we have just the presets, not the index
        if 'Sections.list' in self.remote_presets:
            self.remote_presets.remove('Sections.list')

    def _regenerate_section_list(self):
        """
        Re-generate the Section.list for the given node
        """
        # First remove the old Section.list if one exists
        section_list = '{temp}/remote/Sections.list'.format(temp=self.temp)
        if os.path.exists(section_list):
            os.remove(section_list)

        # Now write the new one
        section_file = open(section_list, 'w')
        # First the header
        section_file.write('""\n')
        # Make sure our presets are up to date
        self._analyse_presets()
        # Loop through and write each remote preset
        for preset in self.remote_presets:
            section_file.write('{preset}\t{preset}\n'.format(preset=preset))
        # Finish writing and close the file
        section_file.close()

    def _remote_exists(self, preset):
        """
        Check if a preset with the same name as the one provided is already published

        :param preset:      The preset name to check
        :type preset:       str
        :return:            Does it exist?
        :type:              bool
        """
        if preset in self.remote_presets:
            return True
        else:
            return False

    def can_publish(self):
        """
        Check if there are any local presets for this operator available to be published

        :return:        Is there anything to publish?
        :type:          bool
        """
        if len(self.local_presets) > 0:
            return True
        else:
            return False

    def publish_preset(self):
        """
        Publish the preset for the given node
        """
        msg = 'Please pick from the following local presets for {category}/{type} ' \
              'that are available to publish.'.format(category=self._get_node_type_category(),
                                                      type=self._get_node_type())
        result = hou.ui.selectFromList(self.local_presets,
                                       message=msg,
                                       title='Preset Publisher',
                                       clear_on_cancel=True,
                                       default_choices=[0])

        if result:
            preset = self.local_presets[result[0]]

            if self._remote_exists(preset):
                # Already exists
                msg = 'A preset with this name has already been published for this node type. Either select a new ' \
                      'name or leave it unchanged to overwrite.'
                result = hou.ui.readInput(msg, initial_contents=preset)
                if result[1]:
                    new_preset_name = result[1]
                else:
                    new_preset_name = preset
            else:
                # Preset not renamed
                new_preset_name = preset

            # Copy preset to remote folder
            local_path = '{temp}/local/{preset}'.format(temp=self.temp,
                                                        preset=preset)
            remote_path = '{temp}/remote/{preset}'.format(temp=self.temp,
                                                          preset=new_preset_name)
            shutil.copy(local_path, remote_path)

            # Regenerate Section.list
            self._regenerate_section_list()

            # Write into idx
            remote_dir = '{temp}/remote'.format(temp=self.temp)

            prefs = os.getenv('PRESET_REPO')
            preset_dir = '{prefs}/{category}'.format(prefs=prefs,
                                                     category=self._get_node_type_category())
            preset_path = '{directory}/{type}.idx'.format(directory=preset_dir,
                                                          type=self._get_node_type())
            # Create any missing directories
            if not os.path.isdir(preset_dir):
                os.makedirs(preset_dir)

            # And write the file
            cmd_list = ['hidx', '-c', remote_dir, preset_path]
            subprocess.call(cmd_list)
