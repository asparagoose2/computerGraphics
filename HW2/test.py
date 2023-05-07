import tkinter as tk
import xml.etree.ElementTree as ET
import numpy as np
from tkinter import Canvas
from xml.etree.ElementTree import Element, ElementTree
import time


WINDOW_WIDTH = 1800
WINDOW_HEIGHT = 1200

scale = 1

transformation_matrix = np.eye(3)

def error(msg):
    print("Error! " + msg)
    exit(-1)

# Define helper function for matrix multiplication
def apply_matrix(matrix, point):
    homogeneous_point = np.array([point[0], point[1], 1])
    transformed_point = np.matmul(matrix, homogeneous_point)
    return transformed_point[:2]  # Extract the x and y coordinates

def parse_rect(shape_properties):
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

    return (x,y),(x+width,y+height)

def draw_rect(canvas: Canvas, p1, p2, shape_properties):
    fill = shape_properties.get("fill")
    stroke = shape_properties.get("stroke")
    if stroke is None:
        stroke = ""
    stroke_width = shape_properties.get("stroke_width")
    if stroke_width is None:
        stroke_width = 1
    else:
        stroke_width = float(stroke_width) * scale

    # Draw the transformed rectangle on the canvas
    canvas.create_rectangle(p1[0], p1[1], p2[0], p2[1], fill=fill, outline=stroke, width=stroke_width)

def parse_circle(shape_properties: dict):
    cx = shape_properties.get('cx')
    cy = shape_properties.get('cy')
    if cx is None or cy is None:
        error("In shape circle, cx or cy are not defined")
    cx = float(cx)
    cy = float(cy)

    r = shape_properties.get('r')
    if r is None:
        error("In shape circle, r is not defined")
    r = float(r)

    return (cx,cy), r

def draw_circle(canvas: Canvas, c, r, shape_properties):
    fill = shape_properties.get("fill")
    stroke = shape_properties.get("stroke")
    stroke_width = shape_properties.get("width")
    if stroke_width is None:
        stroke_width = 1
    else:
        stroke_width = float(stroke_width) * scale



    start = shape_properties.get('start_angle')
    extent = shape_properties.get('extent')

    if start is not None and extent is not None:
        canvas.create_arc(c[0]-r, c[1]-r, c[0]+r, c[1]+r, start=start, extent=extent, style=tk.ARC, width=stroke_width, outline=stroke)
    else:
        canvas.create_oval(c[0]-r, c[1]-r, c[0]+r, c[1]+r,fill=fill, outline=stroke, width=stroke_width)



def draw_image(canvas: Canvas, root: Element):
    # create the transformation matrix to scale down the rectangle by 0.5
    transformation_matrix = np.array([[scale, 0, 0], [0, scale, 0], [0, 0, 1]])
    # Iterate over shape elements
    for shape_elem in root.findall('Shape'):
        shape_type = shape_elem.attrib['type']
        shape_properties = shape_elem.attrib

        # Apply the transformation matrix to the shape properties
        if shape_type == 'rect':
            p1,p2 = parse_rect(shape_properties)
            p1 = apply_matrix(transformation_matrix, p1)
            p2 = apply_matrix(transformation_matrix, p2)

            # Draw the transformed rectangle on the canvas
            draw_rect(canvas, p1, p2, shape_properties)


        elif shape_type == 'circle':
            c, r = parse_circle(shape_properties)
            c = apply_matrix(transformation_matrix, c)
            r = r * scale
            draw_circle(canvas, c, r, shape_properties)


            # cx = float(shape_properties['cx'])
            # cy = float(shape_properties['cy'])
            # r = float(shape_properties['r'])

            # # safely get start_angle
            # start = shape_properties.get('start_angle')
            # extent = shape_properties.get('extent')

            # fill = shape_properties.get("fill")
            # stroke = shape_properties.get("stroke")
            # width = shape_properties.get("width")
            
            # if start is not None and extent is not None:
            #     canvas.create_arc(cx-r, cy-r, cx+r, cy+r, start=start, extent=extent, style=tk.ARC, width=width, outline=stroke)
            # else:
            #     canvas.create_oval(cx-r, cy-r, cx+r, cy+r,fill=fill, outline=stroke, width=width)

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


def main():
    print("HW2: 2D Transformations is starting...")
    print("By: Ofir Duchvonov & Shoval Zohar & Koral Tsaba")

    global scale

    # Load and parse the SVG-like file
    tree: ElementTree = ET.parse('file.svg')
    root: Element = tree.getroot()

    # Create a Tkinter window
    window = tk.Tk()
    canvas: Canvas = tk.Canvas(window, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    canvas.pack()

    # draw the image from scale 0.1 to 1.0
    for scale in np.arange(0.1, 2, 0.1):
        # Clear the canvas
        canvas.delete("all")

        # Draw the image
        draw_image(canvas, root)

        # Wait for 1 second
        window.update()
        time.sleep(1)



    window.mainloop()


if __name__ == "__main__":
    main()