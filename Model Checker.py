# Libraries
import bpy
import math
import numpy as np

# Add-on information
bl_info = {
    "name": "Model Checker",
    "author": "XRAILab",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Properties > Scene Properties > Model Checker",
    "description": "Calculates the discrepancy between two 3D models. It expresses in meters the minimum, maximum, average and standard deviation distance between two models. It also generates a heat map of the model in the weight painting layer with the least amount of vertices indicating in red the vertices with the highest discrepancy and in blue the ones with the lowest discrepancy.",
    "warning": "It only works by selecting two polygonal models. For correct operation the normals of both models must be correctly oriented.",
    "doc_url": "",
    "category": "",
}

# THRESHOLDS CLASS
class MyProperties(bpy.types.PropertyGroup):
    min_threshold: bpy.props.FloatProperty(name="Min threshold", default=0.01)
    max_threshold: bpy.props.FloatProperty(name="Max threshold", default=0.05)

# MAIN CLASS
class ModelChecker(bpy.types.Operator):
    """Calculates the discrepancy between two 3D models. It expresses in meters the minimum, maximum, average and standard deviation distance between two models. It also generates a heat map of the model in the weight painting layer with the least amount of vertices indicating in red the vertices with the highest discrepancy and in blue the ones with the lowest discrepancy"""
    bl_idname = "object.calculate_model_checker"
    bl_label = "Calculate discrepancy"

    # Initialize class variables
    distance_differences = []
    min_distance = 0
    max_distance = 0
    mean_distance = 0
    standard_deviation = 0
    error = "none"

    # Function to start the operation
    def execute(self, context):
        # Obtaining the selected objects in the scene
        selected_objects = bpy.context.selected_objects

         # Check whether exactly two objects were selected
        if len(selected_objects) != 2:
            ModelChecker.error = "Exactly two objects must be selected and both must be meshes."
            return {'CANCELLED'}  # If the operation is cancelled, returns 'CANCELLED'.
        else:
            # Verify if both objects are of mesh type
            for obj in selected_objects:
                if obj.type != 'MESH':
                    ModelChecker.error = "Exactly two objects must be selected and both must be meshes."
                    return {'CANCELLED'}  # If the operation is cancelled, returns 'CANCELLED'.

            # Select the first and last object from the list of selected objects
            obj1 = selected_objects[0]
            obj2 = selected_objects[-1]

        ModelChecker.error = "none"

        # Function for calculating the distance between two points
        def point_distance(p1, p2):
            return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 + (p1[2] - p2[2])**2)

        # Function to calculate the angle between two vectors
        def angle_between_vectors(v1, v2):
            dot_product = np.dot(v1, v2)
            magnitude_v1 = np.linalg.norm(v1)
            magnitude_v2 = np.linalg.norm(v2)
            cos_theta = dot_product / (magnitude_v1 * magnitude_v2)
            angle_radians = np.arccos(cos_theta)
            angle_degrees = np.degrees(angle_radians)
            return angle_degrees

        # Count the number of vertices of each object
        num_vertices_obj1 = len(obj1.data.vertices)
        num_vertices_obj2 = len(obj2.data.vertices)

        # Determine which object has the least number of vertices and assign them accordingly
        if num_vertices_obj1 <= num_vertices_obj2:
            obj_less_polygons = obj1
            obj_more_polygons = obj2
        else:
            obj_less_polygons = obj2
            obj_more_polygons = obj1

        # List for storing distance differences
        distance_differences = []

        # Loop for enlarging the opening angle to calculate distances
        threshold = 1
        while threshold <= 15:
            # Iterate over model vertices with fewer polygons (obj_less_polygons)
            for v1 in obj_less_polygons.data.vertices:
                # Coordinates of the vertex in the model with the fewest polygons
                coord_v1 = obj_less_polygons.matrix_world @ v1.co

                # Obtains the normal vector of the vertex in the model with fewer polygons
                normal_v1 = v1.normal

                # Initializes the list of distances for this vertex
                vertex_distances = []

                # Initializes the minimum distance to the vertex
                min_distance = float('inf')

                # Iterate over model vertices with more polygons (obj_more_polygons)
                for v2 in obj_more_polygons.data.vertices:
                    # Coordinates of the vertex in the model with more polygons
                    coord_v2 = obj_more_polygons.matrix_world @ v2.co

                    # Vector that goes from the vertex in obj_less_polygons to the vertex in obj_more_polygons
                    difference_vector = coord_v2 - coord_v1

                    # Calculates the angle between the difference vector and the normal of obj_less_polygons
                    angle = angle_between_vectors(normal_v1, difference_vector)

                    # If the angle is greater than the current threshold, calculate the distance between the vertices
                    if angle > threshold:
                        distance = point_distance(coord_v1, coord_v2)
                        if distance < min_distance:
                            min_distance = distance

                # If a minimum distance for this vertex was found, store it
                if min_distance != float('inf'):
                    distance_differences.append(min_distance)

            # If distance differences were found, stop the loop
            if distance_differences:
                break

            # Increase the threshold for the next attempt
            threshold += 1

        # Calculate scores
        if distance_differences:
            min_distance = min(distance_differences)
            max_distance = max(distance_differences)
        else:
            min_distance = 0.0  # If there are no valid distances, set the minimum distance to 0
            max_distance = 0.0  # If there are no valid distances, set the minimum distance to 0

        # Calculate mean distance and standard deviation
        if distance_differences:
            mean_distance = np.mean(distance_differences)
            standard_deviation = np.std(distance_differences)
        else:
            mean_distance = 0.0  # If there are no valid distances, set the minimum distance to 0
            standard_deviation = 0.0  # If there are no valid distances, set the minimum distance to 0

        # Heat map creation in weight painting
        weight_group_name = "ModelChecker_Weight"
        weight_group = obj_less_polygons.vertex_groups.new(name=weight_group_name)
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')  # Switch to weight painting mode

        # Loop for assigning a weight to each vertex
        for v in obj_less_polygons.data.vertices:
            # Obtain vertex index
            vertex_index = v.index

            # Get the distance from the current vertex
            vertex_distance = distance_differences[vertex_index]

            # Normalize the distance according to the minimum and maximum thresholds.
            if vertex_distance > context.scene.my_properties.max_threshold:
                weight_value = 1.0
            elif vertex_distance <= context.scene.my_properties.min_threshold:
                weight_value = 0.01
            else:
                weight_value = 0.01 + (vertex_distance - context.scene.my_properties.min_threshold) / (context.scene.my_properties.max_threshold - context.scene.my_properties.min_threshold) * 0.9

            # Assign weight to the vertex in the vertex group
            obj_less_polygons.vertex_groups.active.add([vertex_index], weight_value, 'REPLACE')

        # Stream of variables to the UI
        ModelChecker.min_distance = min_distance
        ModelChecker.max_distance = max_distance
        ModelChecker.mean_distance = mean_distance
        ModelChecker.standard_deviation = standard_deviation

        return {'FINISHED'}

# INTERFACE CLASS
class CustomPanelScene(bpy.types.Panel):
    bl_label = "Model Checker"
    bl_idname = "SCENE_PT_ModelChecker"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Button for executing the main function
        row = layout.row()
        row.scale_y = 3.0
        row.operator("object.calculate_model_checker")

        # Sliders to define thresholds
        layout.label(text="Definition of thresholds for heat mapping, in meters:")
        layout.prop(context.scene.my_properties, "min_threshold")
        layout.prop(context.scene.my_properties, "max_threshold")

        # Min distance row
        layout.label(text="Min distance:")
        row = layout.row()
        row.label(text="{:.4f} in meters".format(round(ModelChecker.min_distance, 4)))

        # Max distance row
        layout.label(text="Max distance:")
        row = layout.row()
        row.label(text="{:.4f} in meters".format(round(ModelChecker.max_distance, 4)))

        # Average distance row
        layout.label(text="Average distance:")
        row = layout.row()
        row.label(text="{:.4f} in meters".format(round(ModelChecker.mean_distance, 4)))

        # Standard deviation row
        layout.label(text="Standard deviation:")
        row = layout.row()
        row.label(text="{:.4f} in meters".format(round(ModelChecker.standard_deviation, 4)))

        # Error notice row
        layout.label(text="Error notification:")
        row = layout.row()
        row.label(text=str(ModelChecker.error))

# Register all classes
def register():
    bpy.utils.register_class(CustomPanelScene)
    bpy.utils.register_class(ModelChecker)
    bpy.utils.register_class(MyProperties)
    bpy.types.Scene.my_properties = bpy.props.PointerProperty(type=MyProperties)

# Unregister all classes
def unregister():
    bpy.utils.unregister_class(CustomPanelScene)
    bpy.utils.unregister_class(ModelChecker)
    bpy.utils.unregister_class(MyProperties)
    del bpy.types.Scene.my_properties

if __name__ == "__main__":
    register()