import hou


class PresetManager(object):
    def __init__(self, _node):
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

