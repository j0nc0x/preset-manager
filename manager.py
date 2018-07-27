class PresetManager(object):
    def __init__(self):
        pass

    def publish(self, node_type):
        """
        Given a specified Houdini node type list all the available presets which can be published

        :param node_type:   The Houdini node type we are publishing presets for
        :type node_type:    hou.NodeType
        """
        print 'Publishing'
        print node_type
