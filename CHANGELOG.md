# Changelog

All notable changes to this project will be documented in this file.

## [0.2.6] - 2024-11-08

### Removed

- Simple Updater, think about Blenders Extension Platform, easier method perhaps

### Fixed

- Poll issue texture preview > update nested image texture nodegroup
- Update not working for nested image texture > nodegroup

## [0.2.5] - 2022-06-13

### Fixed

- Texture panel not showing inside node group

## [0.2.4] - 2021-07-28

### Fixed

-Panel issue difference 2.83 and 290

## [0.2.4] - 2021-04-08

### Added

- Check if we are in shading mode, should not show in Compositor
- Better filter for what to show > later add lights and perhaps grease pencil?
  Still needs work though

## [0.2.3] - 2021-04-09

### Added

- Support for Blender 2.80
- Popup operator for fullscreen workflow
- Material slot picker > adds better control to what material is being changed
- Extra Image List texture panel preview
- Option to show/hide texture info

### Changed

- Layout to match Blender 2.80 panels and sub-panels
- Layout for easier control
- Lower default rows & cols
- Make it only visible in Shading Node mode, Compositor Node has no use for it 
- Extra check if wo do rename materials & node groups > this needs thoughts > its very destructive operation!

### Removed

- Unneed object type interaction modes > did not work
- Grease Pencil shading mode > is this needed or supported?

## [0.2] - 2017-08-11

### Added

- Afeature to eliminate duplicates for node groups and materials

## [0.1] - 2017-05-30

- Initial release for Blender 2.78

## Notes

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

[0.2.6]:https://github.com/schroef/Extra-Material-List/releases/tag/v.0.2.6
[0.2.3]:https://github.com/schroef/Extra-Material-List/releases/tag/v.0.2.3
[0.2]:https://github.com/schroef/Extra-Material-List/releases/tag/v0.2
[0.1]:https://github.com/schroef/Extra-Material-List/releases/tag/v0.1
