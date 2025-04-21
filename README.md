# Model Checker

## Overview
Model Checker is a Blender add-on designed to analyze distance discrepancies between 3D models and visualize the results using heatmaps. Blender version 2.8 or higher is required to install Model Checker. You can download the latest version of Blender from the following link: https://www.blender.org/download/


## Installation

1. **Download** the `Model Checker.py` file from this repository.
2. **Open Blender** and navigate to the Preferences menu.
3. Go to the **Add-ons** section.
4. Click on **Install from local disk** and select the downloaded `.py` file.
5. The add-on is now installed and a new section called **Model Checker** will appear in the Scene Properties panel.

## Add-on usage

### General usage
1. **Select two 3D Models**: Choose the models you want to analyze in the Blender viewport.
2. **Adjust the thresholds**: it is necessary to adjust the discrepancy thresholds for the heatmap generation. Values equal to or less than the minimum will be displayed in blue and values equal to or greater than the maximum in red. These default values are 0.01 for the minimum and 0.05 for the maximum. The values are expressed in meters. A Vertex Group will be created through which the heat map can be displayed in “Weight Painting” mode. For each analysis a new vertex group will be created.
3. **Analyze the Model**: Click the **Calculate Discrepancy** button in in the Model Checker panel.
4. **Review Results**: The results will display in the add-on panel. In addition, in the model with fewer polygons a Vertex Group will be created through which the heat map can be displayed in the “Weight Painting” mode. For each analysis a new vertex group will be created.

### Heatmaps usage
- Each heatmap can be displayed using the “Weight painting” mode.
- Previous heatmaps can be displayed by selecting the previous vertex groups.
- These vertex weight values can be used as attributes for texturing, creating compatible heatmap textures and materials for display with other software.


## Uninstallation
To uninstall Model Checker:
1. Go back to Blender's Preferences.
2. Navigate to the Add-ons section.
3. Click on **Uninstall** for Model Checker.

## Contributing
If you would like to contribute to Model Checker, feel free to fork the repository and submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
