# Houdini Preset Manager
A simple python tool that can be used to publish Houdini node presets to a central location (currently a shared folder on disk).
## Usage
First ensure that the preset manager is added to the Houdini script path, and that the PRESET_REPO is set to point at the central presets directory:
```bash
export HOUDINI_SCRIPT_PATH=@/scripts:/store/preset-manager
export PRESET_REPO=/store/presets
```
From a Houdini python shell the following code can be run to trigger the preset manager for a specified node:
```python
import presetmanager
# select a node in the scene
n = hou.node('/obj/geo1/sphere1')
# initialise the preset manager with the node
man = presetmanager.PresetManager(n)
# start the publish
man.publish_preset()
```
This could be added as a right-click menu option in the network editior. The ```can_publish``` method can be used to determine whether the publish option should be available or not.

## Notes
Currently the publish is a basic comparison / update of a shared directory of presets as a proof of concept. This probably needs further development to use a versioned publish directory, or perhaps source control to make it more robust, as using a single publish directory could result in overwrite issues when being used by several users concurrently.
