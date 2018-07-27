import hou


class PresetManager(object):
    def __init__(self, _node):
        self.preset_node = _node

    def isValid(self):
        """
        Check if the preset manager has a valid node as an input

        :return:        Is valid?
        :type:          bool
        """
        if self.preset_node and issubclass(type(self.preset_node), hou.Node):
            return True
        else:
            return False

