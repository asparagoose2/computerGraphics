import tkinter as tk
import xml.etree.ElementTree as ET
import numpy as np

# Load and parse the SVG-like file
tree = ET.parse('file.svg')
root = tree.getroot()

# Create a Tkinter window
window = tk.Tk()
canvas = tk.Canvas(window, width=800, height=600)
canvas.pack()

# Define helper function for matrix multiplication
def apply_matrix(matrix, point):
    homogeneous_point = np.array([point[0], point[1], 1])
    transformed_point = np.matmul(matrix, homogeneous_point)
    return transformed_point[:2]  # Extract the x and y coordinates

# Iterate over shape elements
for shape_elem in root.findall('Shape'):
    shape_type = shape_elem.attrib['type']
    shape_properties = shape_elem.attrib

    # Apply transformations
    transformation_matrix = np.eye(3)  # Identity matrix
    for transform_elem in root.findall('Transformations/*'):
        if transform_elem.tag == 'Translate':
            tx = float(transform_elem.attrib['x'])
            ty = float(transform_elem.attrib['y'])
            translation_matrix = np.array([[1, 0, tx], [0, 1, ty], [0, 0, 1]])
            transformation_matrix = np.matmul(transformation_matrix, translation_matrix)
        elif transform_elem.tag == 'Scale':
            sx = float(transform_elem.attrib['x'])
            sy = float(transform_elem.attrib['y'])
            scaling_matrix = np.array([[sx, 0, 0], [0, sy, 0], [0, 0, 1]])
            transformation_matrix = np.matmul(transformation_matrix, scaling_matrix)
        elif transform_elem.tag == 'Rotate':
            angle = float(transform_elem.attrib['angle'])
            rad = np.radians(angle)
            cos_theta = np.cos(rad)
            sin_theta = np.sin(rad)
            rotation_matrix = np.array([[cos_theta, -sin_theta, 0], [sin_theta, cos_theta, 0], [0, 0, 1]])
            transformation_matrix = np.matmul(transformation_matrix, rotation_matrix)

    # Apply the transformation matrix to the shape properties
    if shape_type == 'rect':
        x = float(shape_properties['x'])
        y = float(shape_properties['y'])
        width = float(shape_properties['width'])
        height = float(shape_properties['height'])

        # Apply transformation to the rectangle's vertices
        vertices = [(x, y), (x + width, y), (x + width, y + height), (x, y + height)]
        transformed_vertices = [apply_matrix(transformation_matrix, vertex) for vertex in vertices]

        # Draw the transformed rectangle on the canvas
        canvas.create_rectangle(*transformed_vertices, fill=shape_properties['fill'])

    elif shape_type == 'circle':
        cx = float(shape_properties['cx'])
        cy = float(shape_properties['cy'])
        r = float(shape_properties['r'])

        # Apply transformation to the circle's center
        transformed_center = apply_matrix(transformation_matrix, (cx, cy))

        # Draw the transformed circle on the canvas
        canvas.create_oval(transformed_center[0] - r, transformed_center[1] - r,
                           transformed_center[0] + r, transformed_center[1] + r,
                           fill=shape_properties['fill'])

# Run the Tkinter event loop
window.mainloop()
