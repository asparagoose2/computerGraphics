'''
    HW2 - 2D Transformations
    This is the work of:
    - Ofir Duchovne
    - Shoval Zohar
    - Koral Tsaba
    Subbmitted to:
    - Dr. Sheffer Eyal
    As part of the course:
    - Computer Graphics
    At:
    - Shenkar College of Engineering and Design
'''
import sys
import tkinter as tk
import xml.etree.ElementTree as ET
import numpy as np
from tkinter import Canvas
from xml.etree.ElementTree import Element, ElementTree
from tkinter import messagebox as mb
from tkinter import filedialog as fd

HELP_MESSAGE = '''Use the mouse to drag the image around or click the position you want the image to be at.
Use the mouse wheel to zoom in and out
Use the slider to rotate the image'''
HELP_TITLE = "Help"
DEFAULT_FILE = "tractor.svg"

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

canvas: Canvas = None
root: Element = None
window: tk.Tk = None
slider: tk.Scale = None

scale = 1
angle = 0
translate_X = 0
translate_Y = 0

is_windows = hasattr(sys, 'getwindowsversion')
is_click_to_position: tk.BooleanVar = None
last_click_position = (0,0)

shape_center = (0,0)
transformation_matrix = np.eye(3)

def update_transformation_matrix():
    global transformation_matrix
    # Apply translation
    transformation_matrix = np.array([[1, 0, translate_X], [0, 1, translate_Y], [0, 0, 1]])
    # Apply rotation
    transformation_matrix = np.matmul(transformation_matrix, np.array([[np.cos(np.radians(angle)), -np.sin(np.radians(angle)), 0], [np.sin(np.radians(angle)), np.cos(np.radians(angle)), 0], [0, 0, 1]]))
    # Apply scaling
    transformation_matrix = np.matmul(transformation_matrix, np.array([[scale, 0, 0], [0, scale, 0], [0, 0, 1]]))
    # Apply translation offset to the shape's center (caused by rotation)
    transformation_matrix = np.matmul(transformation_matrix, np.array([[1, 0, -shape_center[0]], [0, 1, -shape_center[1]], [0, 0, 1]]))

def set_scale(new_scale):
    global scale
    # Prevent scale from being too small
    if(scale + new_scale < 0.15):
        scale = 0.1
    else:
        scale = new_scale
    update_transformation_matrix()

def set_angle(new_angle):
    global angle
    angle = new_angle
    update_transformation_matrix()

def set_translate_X(new_translate_X):
    global translate_X
    translate_X =  new_translate_X
    update_transformation_matrix()

def set_translate_Y(new_translate_Y):  
    global translate_Y
    translate_Y =  new_translate_Y
    update_transformation_matrix()
    
def set_translate(new_translate_X, new_translate_Y):
    global translate_X
    global translate_Y
    translate_X =  new_translate_X
    translate_Y =  new_translate_Y
    update_transformation_matrix()

def error(msg):
    print("Error! " + msg)
    mb.showerror("Error", msg)
    window.destroy()
    exit(-1)

def apply_matrix(matrix, point):
    '''
    Apply a matrix to a point
    :param matrix: The matrix to apply
    :param point: The point to apply the matrix to
    :return: The transformed point
    '''
    homogeneous_point = np.array([point[0], point[1], 1])
    transformed_point = np.matmul(matrix, homogeneous_point)
    return transformed_point[:2]  # Extract the x and y coordinates

def parse_circle(shape_properties: dict):
    '''
    Parse the circle shape properties
    :param shape_properties: The properties of the shape
    :return: The center point and radius of the circle
    '''
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

def draw_circle(canvas: Canvas, c, r, shape_properties, start, extent):
    '''
    Draw a circle on the canvas
    :param canvas: The canvas to draw on
    :param c: The center point of the circle
    :param r: The radius of the circle
    :param shape_properties: The properties of the shape
    :param start: The start angle of the arc
    :param extent: The extent of the arc
    :return: None
    '''
    fill = shape_properties.get("fill")
    stroke = shape_properties.get("stroke")
    stroke_width = shape_properties.get("width")
    if stroke_width is None:
        stroke_width = 1
    else:
        stroke_width = float(stroke_width) * scale

    if start is not None and extent is not None:
        canvas.create_arc(c[0]-r, c[1]-r, c[0]+r, c[1]+r, start=start, extent=extent, style=tk.ARC, width=stroke_width, outline=stroke)
    else:
        canvas.create_oval(c[0]-r, c[1]-r, c[0]+r, c[1]+r,fill=fill, outline=stroke, width=stroke_width)

def parse_line(shape_properties: dict):
    '''
    Parse the line shape properties
    :param shape_properties: The properties of the shape
    :return: The two points of the line
    '''
    x1 = shape_properties.get('x1')
    y1 = shape_properties.get('y1')
    x2 = shape_properties.get('x2')
    y2 = shape_properties.get('y2')
    if x1 is None or y1 is None or x2 is None or y2 is None:
        error("In shape line, x1, y1, x2, or y2 are not defined")
    x1 = float(x1)
    y1 = float(y1)
    x2 = float(x2)
    y2 = float(y2)

    return (x1,y1),(x2,y2)

def draw_line(canvas: Canvas, p1, p2, shape_properties):
    '''
    Draw a line on the canvas
    :param canvas: The canvas to draw on
    :param p1: The first point of the line  
    :param p2: The second point of the line
    :param shape_properties: The properties of the shape
    :return: None
    '''
    fill = shape_properties.get("fill")
    width = shape_properties.get("width")
    if width is None:
        width = 1
    else:
        width = float(width) * scale

    canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill=fill, width=width)

def draw_image(canvas: Canvas, root: Element):
    '''
    Draw the image on the canvas
    :param canvas: The canvas to draw on
    :param root: The root element of the XML tree
    :return: None
    '''
    # Iterate over shape elements
    for shape_elem in root.findall('Shape'):
        shape_type = shape_elem.attrib['type']
        shape_properties = shape_elem.attrib

        if shape_type == 'circle':
            c, r = parse_circle(shape_properties)
            # apply the transformation matrix to the center point and radius
            c = apply_matrix(transformation_matrix, c)
            # scale the radius
            r = r * scale
            
            start = shape_properties.get('start_angle')
            extent = shape_properties.get('extent')

            # apply the transformation matrix to the start and extent angles
            if start is not None and extent is not None:
                start = float(start)
                extent = float(extent)
                # adjust the start angle according to the roation angle
                start = start - angle 

            draw_circle(canvas, c, r, shape_properties, start, extent)
        
        elif shape_type == 'line':
            p1,p2 = parse_line(shape_properties)
            # apply the transformation matrix to the two points
            p1 = apply_matrix(transformation_matrix, p1)
            p2 = apply_matrix(transformation_matrix, p2)
            draw_line(canvas, p1, p2, shape_properties)

        else:
            error("Shape type " + shape_type + " is not supported")


def update_screen():
    '''
    Clears the screen and redraw the image
    :return: None
    '''
    canvas.delete("all")
    draw_image(canvas, root)

def mouse_click(event):
    global last_click_position
    last_click_position = (event.x, event.y)
    if is_click_to_position.get():
        set_translate(event.x, event.y)
        update_screen()
        
def mouse_drag(event):
    global last_click_position
    if is_click_to_position.get():
        set_translate(event.x, event.y)
    else:
        offset_point = (event.x - last_click_position[0], event.y - last_click_position[1])
        set_translate(translate_X + offset_point[0], translate_Y + offset_point[1])
        last_click_position = (event.x, event.y)
    update_screen()

def scroll_up(event):
    set_scale(scale + 0.1)
    update_screen()


def scroll_down(event):
    set_scale(scale - 0.1)
    update_screen()

def handle_slider(event):
    set_angle(int(event))
    update_screen()

def show_help():
    mb.showinfo(HELP_TITLE, HELP_MESSAGE)

def mouse_wheel(event: tk.Event):
    if event.delta > 0 or event.num == 4:
        scroll_up(event)
    elif event.delta < 0 or event.num == 5:
        scroll_down(event)
    else:
        print("Unknown mouse wheel event")

def calc_shape_center(shapes):
    vertices = []
    for shape_elem in shapes:
        shape_type = shape_elem.attrib['type']
        shape_properties = shape_elem.attrib

        if shape_type == 'circle':
            c, r = parse_circle(shape_properties)
            vertices.append(c)

        elif shape_type == 'line':
            p1,p2 = parse_line(shape_properties)
            vertices.append(p1)
            vertices.append(p2)

        else:
            error("Shape type " + shape_type + " is not supported")

    return np.mean(vertices, axis=0)


def load_file():
    global root
    global canvas
    global window
    global scale, angle, translate_X, translate_Y, shape_center, transformation_matrix

    filename = fd.askopenfilename(title="Select SVG file", filetypes=(("svg files", "*.svg"), ("all files", "*.*")))
    if filename is None or filename == () or filename == "":
        return

    # Load and parse the SVG-like file
    tree: ElementTree = ET.parse(filename)
    root = tree.getroot()

    # Clear the canvas
    canvas.delete("all")

    # Reset the transformation matrix
    transformation_matrix = np.identity(3)

    # Reset the scale
    scale = 1

    # Reset the angle
    angle = 0
    slider.set(0)

    # Reset the translation
    set_translate_X(WINDOW_WIDTH/2)
    set_translate_Y(WINDOW_HEIGHT/2)

    # Reset the shape center
    shape_center = calc_shape_center(root.findall('Shape'))

    # Draw the image
    draw_image(canvas, root)

def reset():
    global canvas
    global window
    global scale, angle, translate_X, translate_Y, shape_center, transformation_matrix

    # Clear the canvas
    canvas.delete("all")

    # Reset the transformation matrix
    transformation_matrix = np.identity(3)

    # Reset the scale
    scale = 1

    # Reset the angle
    angle = 0
    slider.set(0)

    # Reset the translation
    set_translate_X(WINDOW_WIDTH/2)
    set_translate_Y(WINDOW_HEIGHT/2)

    # Draw the image
    draw_image(canvas, root)

def main():
    global root, canvas, window, slider
    global scale, angle, translate_X, translate_Y, shape_center
    global is_click_to_position

    print("HW2: 2D Transformations is starting...")
    print("By: Ofir Duchvonov & Shoval Zohar & Koral Tsaba")


    # Load and parse the SVG-like file
    tree: ElementTree = ET.parse(DEFAULT_FILE)
    root = tree.getroot()

    # Create a Tkinter window
    window = tk.Tk()
    # disable resizing the GUI
    window.resizable(False, False)

    # Set the window title
    window.title("HW2: 2D Transformations   ·   Ofir & Shoval & Koral")

    canvas = tk.Canvas(window, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    canvas.pack()
    slider = tk.Scale(window, from_=0, to=360, orient=tk.HORIZONTAL, command=handle_slider, length=300)
    slider.pack()
    slider_label = tk.Label(window, text="Angle")
    slider_label.pack()

    # Show welcome message
    mb.showinfo("Welcome", "Welcome to our vector image viewer!\n" + HELP_MESSAGE)

    is_click_to_position = tk.BooleanVar()
    is_click_to_position.set(True)

    menu = tk.Menu(window)
    window.config(menu=menu)
    filemenu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="File", menu=filemenu)
    filemenu.add_command(label="Open", command=load_file)
    filemenu.add_command(label="Help", command=show_help)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=window.quit)
    optionsmenu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Options", menu=optionsmenu)
    optionsmenu.add_command(label="Reset", command=reset)
    optionsmenu.add_checkbutton(label="Click to position", variable=is_click_to_position, onvalue=True, offvalue=False)
    

    canvas.bind("<Button-1>", mouse_click)
    canvas.bind("<Button1-Motion>", mouse_drag)

    if is_windows:
        canvas.bind("<MouseWheel>", mouse_wheel)
    else:
        canvas.bind("<Button-4>", scroll_up)
        canvas.bind("<Button-5>", scroll_down)

    # calculate the shape's center
    shape_center = calc_shape_center(root.findall('Shape'))

    # center the shape to the center of the window
    set_translate_X(WINDOW_WIDTH/2)
    set_translate_Y(WINDOW_HEIGHT/2)

    draw_image(canvas, root)
    window.mainloop()


if __name__ == "__main__":
    main()