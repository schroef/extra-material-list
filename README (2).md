# Extra Material List

>Original addon from <b>MeshLogic</b>

Have you ever struggled with the tiny pop-up list in the material Node Editor? So have I!

Therefore, I made an addon that enables to pop-up an extra material list with specified number of rows and columns. Optionally, you can display all materials in a plain list.

Moreover, there is a button to remove material and node group duplicates (ending with .001, .002, etc), which might occur after appending assets from external files.

!['Preview'](https://raw.githubusercontent.com/wiki/schroef/extra-material-list/images/eml-v023.jpg?2021-0409)


## Extra Material List

This addon makes it possible to save rig setup to a preset folder. The function was already existing but would generate a text inside Blender. I simply added some new functions so these presets can directly be saved in the Blender preset folder of Metarigs. Presets can be added to a folder as well as new folders can be created.

The added presets can then be loaded directly using the add menu. To get the new preset to show, you need to either restart blender or reload the all the addons pressing F8. Its also now possible save Rigify main settings as presets. These can be loaded at any time, no need for a refresh.

>Addon documentation can be found at: <b>[MeshLogic / Extra Material List](https://meshlogic.github.io/posts/blender/addons/extra-material-list/)</b>

## Features

- Two display options (preview and plain list)
- Button to clear all users for the selected image datablock
- Double click on an image in the Node Editor opens the image in the UV/Image Editor
- Located in UV/Image Editor - Tools panel (T)


### System Requirements

| **OS** | **Blender** |
| ------------- | ------------- |
| OSX | Blender 2.80 |
| Windows | Blender 2.80 |
| Linux | Not Tested |

### Blender 2.80 | Pre-release
Try this pre-release branch for Blender 2.80: [bl280_dev](https://github.com/schroef/extra-material-list/tree/bl280_dev)

### Installation Process

1. Download the latest <b>[release](https://github.com/schroef/extra-material-list/releases/)</b>
2. If you downloaded the zip file.
3. Open Blender.
4. Go to File -> User Preferences -> Addons.
5. At the bottom of the window, choose *Install From File*.
6. Select the file `extra-material-list-master.zip` from your download location..
7. Activate the checkbox for the plugin that you will now find in the list.



### Changelog
[Full Changelog](CHANGELOG.md)





<!--
- Fill in data
 -
 -
-->

