import tkinter as tk
import xml.etree.ElementTree as ET
import numpy as np

# Load and parse the SVG-like file
tree = ET.parse('file.svg')
root = tree.getroot()

# Create a Tkinter window
window = tk.Tk()
canvas = tk.Canvas(window, width=700, height=500)
canvas.pack()

def error(msg):
    print("Error! " + msg)
    exit(-1)

# Iterate over shape elements
for shape_elem in root.findall('Shape'):
    shape_type = shape_elem.attrib['type']
    shape_properties = shape_elem.attrib
    print(shape_elem)
    print("------------------")
    print(shape_type)
    print(shape_properties)
    print("------------------")

    # Apply the transformation matrix to the shape properties
    if shape_type == 'rect':
        x = shape_properties.get('x')
        y = shape_properties.get('y')
        if x is None or y is None:
            error("In shape rect, x or y are not defined")
        x = float(x)
        y = float(y)

        width = shape_properties.get('width')
        height = shape_properties.get('height')

        if width is None or height is None:
            error("In shape rect, width or height are not defined")

        width = float(width)
        height = float(height)

        fill = shape_properties.get("fill")
        stroke = shape_properties.get("stroke")
        stroke_width = shape_properties.get("stroke_width")

        # Apply transformation to the rectangle's vertices
        vertices = [(x, y), (x + width, y), (x + width, y + height), (x, y + height)]

        # Draw the transformed rectangle on the canvas
        canvas.create_rectangle(x,y,x+width,y+height, fill=fill, outline=stroke, width=stroke_width)

    elif shape_type == 'circle':
        cx = float(shape_properties['cx'])
        cy = float(shape_properties['cy'])
        r = float(shape_properties['r'])

        # safely get start_angle
        start = shape_properties.get('start_angle')
        extent = shape_properties.get('extent')

        fill = shape_properties.get("fill")
        stroke = shape_properties.get("stroke")
        width = shape_properties.get("width")
        
        if start is not None and extent is not None:
            canvas.create_arc(cx-r, cy-r, cx+r, cy+r, start=start, extent=extent, style=tk.ARC, width=width, outline=stroke)
        else:
            canvas.create_oval(cx-r, cy-r, cx+r, cy+r,fill=fill, outline=stroke, width=width)

        # Draw the transformed circle on the canvas
    
    elif shape_type == 'line':
        x1 = float(shape_properties['x1'])
        y1 = float(shape_properties['y1'])
        x2 = float(shape_properties['x2'])
        y2 = float(shape_properties['y2'])

        # Apply transformation to the line's vertices
        vertices = [(x1, y1), (x2, y2)]

        # Draw the transformed line on the canvas
        canvas.create_line(x1, y1, x2, y2, fill=shape_properties['fill'])


# Run the Tkinter event loop
window.mainloop()
