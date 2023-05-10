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
import copy
import math
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
mirror: tk.BooleanVar = None

is_windows = hasattr(sys, 'getwindowsversion')
is_click_to_position: tk.BooleanVar = None
is_show_shape_enclosing_rect: tk.BooleanVar = None
last_click_position = (0,0)
is_crop = False
crop_side = 0
TOP_SIDE = 0
LEFT_SIDE = 1
BOTTOM_SIDE = 2
RIGHT_SIDE = 3

TOP_RIGHT = 0
TOP_LEFT = 1
BOTTOM_LEFT = 2
BOTTOM_RIGHT = 3
X = 0
Y = 1
shape_center = (0,0)
original_enclosing_rect = []
enclosing_rect = [] # 4 points [top-right, top-left, bottom-left, bottom-right]
transformed_enclosing_rect = []
crop_rect = []
transformation_matrix = np.eye(3)

def update_enclosing_rect():
    global enclosing_rect
    global transformation_matrix
    global shape_center
    transformed_enclosing_rect.clear()
    for point in enclosing_rect:
        transformed_point = apply_matrix(transformation_matrix, point)
        # round up
        transformed_enclosing_rect.append(transformed_point)
    transformed_enclosing_rect[TOP_RIGHT][X] = math.ceil(transformed_enclosing_rect[TOP_RIGHT][X])
    transformed_enclosing_rect[TOP_RIGHT][Y] = math.floor(transformed_enclosing_rect[TOP_RIGHT][Y])
    transformed_enclosing_rect[TOP_LEFT][X] = math.floor(transformed_enclosing_rect[TOP_LEFT][X])
    transformed_enclosing_rect[TOP_LEFT][Y] = math.floor(transformed_enclosing_rect[TOP_LEFT][Y])
    transformed_enclosing_rect[BOTTOM_LEFT][X] = math.floor(transformed_enclosing_rect[BOTTOM_LEFT][X])
    transformed_enclosing_rect[BOTTOM_LEFT][Y] = math.ceil(transformed_enclosing_rect[BOTTOM_LEFT][Y])
    transformed_enclosing_rect[BOTTOM_RIGHT][X] = math.ceil(transformed_enclosing_rect[BOTTOM_RIGHT][X])
    transformed_enclosing_rect[BOTTOM_RIGHT][Y] = math.ceil(transformed_enclosing_rect[BOTTOM_RIGHT][Y])


def update_transformation_matrix():
    global transformation_matrix
    # Apply translation
    transformation_matrix = np.array([[1, 0, translate_X], [0, 1, translate_Y], [0, 0, 1]])
    # Apply rotation
    transformation_matrix = np.matmul(transformation_matrix, np.array([[np.cos(np.radians(angle)), -np.sin(np.radians(angle)), 0], [np.sin(np.radians(angle)), np.cos(np.radians(angle)), 0], [0, 0, 1]]))
    # Apply scaling
    transformation_matrix = np.matmul(transformation_matrix, np.array([[scale, 0, 0], [0, scale, 0], [0, 0, 1]]))
    # apply vertical mirrror
    # transformation_matrix = np.matmul(transformation_matrix, np.array([[1, 0, 0], [0, -1, 0], [0, 0, 1]]))
    # apply horizontal mirrror
    if mirror.get():
        transformation_matrix = np.matmul(transformation_matrix, np.array([[-1, 0, 0], [0, 1, 0], [0, 0, 1]]))
    # Apply translation offset to the shape's center (caused by rotation)
    transformation_matrix = np.matmul(transformation_matrix, np.array([[1, 0, -shape_center[0]], [0, 1, -shape_center[1]], [0, 0, 1]]))
    update_enclosing_rect()

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


def is_point_inside_polygon(point, polygon):
    x, y = point
    num_vertices = len(polygon)

    # Initialize counter for number of intersections
    num_intersections = 0

    # Iterate over each edge of the polygon
    for i in range(num_vertices):
        # Get the coordinates of the current vertex and the next vertex
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % num_vertices]

        # Check if the ray from the point intersects the edge
        if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
            num_intersections += 1

    # If the number of intersections is odd, the point is inside the polygon
    return num_intersections % 2 == 1

# Function to draw a pixel on the screen
def put_pixel(x, y, color, screen: Canvas, width):
    if is_point_inside_polygon((x,y), transformed_enclosing_rect) == False:
        return
    screen.create_oval(x, y, x+1, y+1, fill=color, width=width, outline=color)

def draw_arc_helper(arc_center, arc_radius, start_angle, end_angle, color, screen,width):

    start_angle = math.radians(start_angle)
    end_angle = math.radians(end_angle)

    x = 0
    y = arc_radius
    decision = 1 - arc_radius
    center_x = arc_center[X]
    center_y = arc_center[Y]

    while x <= y:
        # Calculate the angle of the current point
        current_angle = math.atan2(y, x)

        # Check if the current angle is within the specified range
        if start_angle <= current_angle <= end_angle:
            # Plot the points by symmetry in the first and second octants
            put_pixel(center_x + x, center_y + y, "black",canvas,width)
            put_pixel(center_x - x, center_y + y, "black",canvas,width)

        if decision <= 0:
            decision += 2 * x + 3
        else:
            decision += 2 * (x - y) + 5
            y -= 1
        x += 1

def draw_circle_helper(circle_x, circle_y, circle_radius, color, screen,width):
    # Initialize the x and y coordinates of the first point on the circle
    # (which is at 0 degrees) and the value of a variable called d.
    x = 0
    y = circle_radius
    d = 3 - 2 * circle_radius

    # Loop while x is less than or equal to y.
    while x <= y:
        # Plot the points of the circle using symmetry
        # 0-45
        put_pixel(circle_x + y, circle_y - x, color,screen,width)
        #  45 - 90
        put_pixel(circle_x + x, circle_y - y, color,screen,width)
        # 90 - 135
        put_pixel(circle_x - x, circle_y - y, color,screen,width)
        # 135 - 180
        put_pixel(circle_x - y, circle_y - x, color,screen,width)
        # 180 - 225
        put_pixel(circle_x - y, circle_y + x, color,screen,width)
        # 225 - 270
        put_pixel(circle_x - x, circle_y + y, color,screen,width)
        # 270 - 315
        put_pixel(circle_x + x, circle_y + y, color,screen,width)
        # 315 - 360
        put_pixel(circle_x + y, circle_y + x, color,screen,width)
        
        # Increment x by 1.
        x += 1

        # If d is greater than 0, decrement y by 1 and update the value of d.
        if d > 0:
            y -= 1
            d = d + 4 * (x - y) + 10

        # Otherwise, update the value of d without changing y.
        else:
            d = d + 4 * x + 6
        

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

    if start is not None and extent is not None and start != 0 and extent != 360:
        canvas.create_arc(c[0]-r, c[1]-r, c[0]+r, c[1]+r, start=start, extent=extent, style=tk.ARC, width=stroke_width, outline=stroke)
    else:
        draw_circle_helper(c[X],c[Y],r,stroke,canvas,stroke_width)

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

def cohen_sutherland_clip(x_min, y_min, x_max, y_max, point1, point2):
    # Define the region codes for the line endpoints
    INSIDE = 0  # Both endpoints are inside the clipping window
    LEFT = 1    # Bit 1: x-coordinate is to the left of the clipping window
    RIGHT = 2   # Bit 2: x-coordinate is to the right of the clipping window
    BOTTOM = 4  # Bit 3: y-coordinate is below the clipping window
    TOP = 8     # Bit 4: y-coordinate is above the clipping window

    # Compute the region codes for a point
    def compute_region_code(x, y):
        code = INSIDE
        if x < x_min:
            code |= LEFT
        elif x > x_max:
            code |= RIGHT
        if y < y_min:
            code |= BOTTOM
        elif y > y_max:
            code |= TOP
        return code

    # Extract the coordinates from the points
    x1, y1 = point1
    x2, y2 = point2

    # Compute the region codes for the line endpoints
    code1 = compute_region_code(x1, y1)
    code2 = compute_region_code(x2, y2)

    # Clip the line against the clipping window
    while True:
        if code1 == 0 and code2 == 0:
            # Both endpoints are inside the clipping window
            return point1, point2
        elif code1 & code2 != 0:
            # Both endpoints are outside the same region; the line is completely outside
            return None, None
        else:
            # At least one endpoint is outside the clipping window; clip the line
            x = 0
            y = 0
            code = code1 if code1 != 0 else code2
            if code & TOP != 0:
                x = x1 + (x2 - x1) * (y_max - y1) / (y2 - y1)
                y = y_max
            elif code & BOTTOM != 0:
                x = x1 + (x2 - x1) * (y_min - y1) / (y2 - y1)
                y = y_min
            elif code & RIGHT != 0:
                y = y1 + (y2 - y1) * (x_max - x1) / (x2 - x1)
                x = x_max
            elif code & LEFT != 0:
                y = y1 + (y2 - y1) * (x_min - x1) / (x2 - x1)
                x = x_min

            if code == code1:
                point1 = (x, y)
                code1 = compute_region_code(x, y)
            else:
                point2 = (x, y)
                code2 = compute_region_code(x, y)
        
def line_is_not_in_enclosing_rect(p1, p2):
    '''
    Check if a line is not in the enclosing rectangle
    :param p1: The first point of the line
    :param p2: The second point of the line
    :return: True if the line is not in the enclosing rectangle, False otherwise
    '''
    if p1[0] > transformed_enclosing_rect[TOP_RIGHT][0] and p2[0] > transformed_enclosing_rect[TOP_RIGHT][0]:
        print("1")
        return True
    if p1[0] < transformed_enclosing_rect[BOTTOM_LEFT][0] and p2[0] < transformed_enclosing_rect[BOTTOM_LEFT][0]:
        print("2")
        return True
    if p1[1] < transformed_enclosing_rect[TOP_RIGHT][1] and p2[1] < transformed_enclosing_rect[TOP_RIGHT][1]:
        print("3")
        return True
    if p1[1] > transformed_enclosing_rect[BOTTOM_LEFT][1] and p2[1] > transformed_enclosing_rect[BOTTOM_LEFT][1]:
        print("4")
        return True
    
    return False
    
def line_is_partially_outside_enclosing_rect(p1, p2):
    '''
    Check if a line is partially outside the enclosing rectangle
    :param p1: The first point of the line
    :param p2: The second point of the line
    :return: True if the line is partially outside the enclosing rectangle, False otherwise
    '''
    if p1[X] > transformed_enclosing_rect[TOP_RIGHT][X] or p2[X] > transformed_enclosing_rect[TOP_RIGHT][X]:
        return True
    if p1[X] < transformed_enclosing_rect[BOTTOM_LEFT][X] or p2[X] < transformed_enclosing_rect[BOTTOM_LEFT][X]:
        return True
    if p1[Y] < transformed_enclosing_rect[TOP_RIGHT][Y] or p2[Y] < transformed_enclosing_rect[TOP_RIGHT][Y]:
        return True
    if p1[Y] > transformed_enclosing_rect[BOTTOM_LEFT][Y] or p2[Y] > transformed_enclosing_rect[BOTTOM_LEFT][Y]:
        return True
    return False



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
    dotted = shape_properties.get("dotted")
    if dotted is not None:
        dotted = (2, 2)

    if width is None:
        width = 1
    else:
        width = float(width) * scale
    
    canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill=fill, width=width, dash=dotted)

def draw_image(canvas: Canvas, root: Element):
    '''
    Draw the image on the canvas
    :param canvas: The canvas to draw on
    :param root: The root element of the XML tree
    :return: None
    '''
    global enclosing_rect
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
            if start is not None and extent is not None and start != 0 and extent != 360:
                start = float(start)
                extent = float(extent)
                # adjust the start angle according to the roation angle
                if mirror.get():
                    # adjust the extent angle according to the roation angle
                    extent = -extent
                    start = 180 - start - angle

                else:
                    start = start - angle 
                
            draw_circle(canvas, c, r, shape_properties, start, extent)
        
        elif shape_type == 'line':
            p1,p2 = parse_line(shape_properties)
            p1, p2 = cohen_sutherland_clip(enclosing_rect[TOP_LEFT][X],enclosing_rect[TOP_LEFT][Y],enclosing_rect[BOTTOM_RIGHT][X],enclosing_rect[BOTTOM_RIGHT][Y],p1,p2)
            if p1 is None or p2 is None:
                continue
            # apply the transformation matrix to the two points
            p1 = apply_matrix(transformation_matrix, p1)
            p2 = apply_matrix(transformation_matrix, p2)
            draw_line(canvas, p1, p2, shape_properties)

        else:
            error("Shape type " + shape_type + " is not supported")

    if is_show_shape_enclosing_rect.get():
        # p1 = apply_matrix(transformation_matrix, enclosing_rect[0])
        # p2 = apply_matrix(transformation_matrix, enclosing_rect[1])
        # p3 = apply_matrix(transformation_matrix, enclosing_rect[2])
        # p4 = apply_matrix(transformation_matrix, enclosing_rect[3])
        draw_line(canvas, transformed_enclosing_rect[0], transformed_enclosing_rect[1], {"fill": "red", "width": 1, "dotted": (2, 2)})
        draw_line(canvas, transformed_enclosing_rect[1], transformed_enclosing_rect[2], {"fill": "red", "width": 1, "dotted": (2, 2)})
        draw_line(canvas, transformed_enclosing_rect[2], transformed_enclosing_rect[3], {"fill": "red", "width": 1, "dotted": (2, 2)})
        draw_line(canvas, transformed_enclosing_rect[3], transformed_enclosing_rect[0], {"fill": "red", "width": 1, "dotted": (2, 2)})
       
        draw_line(canvas, crop_rect[0], crop_rect[1], {"fill": "green", "width": 1, "dotted": (2, 2)})
        draw_line(canvas, crop_rect[1], crop_rect[2], {"fill": "green", "width": 1, "dotted": (2, 2)})
        draw_line(canvas, crop_rect[2], crop_rect[3], {"fill": "green", "width": 1, "dotted": (2, 2)})
        draw_line(canvas, crop_rect[3], crop_rect[0], {"fill": "green", "width": 1, "dotted": (2, 2)})


def update_screen():
    '''
    Clears the screen and redraw the image
    :return: None
    '''
    canvas.delete("all")
    draw_image(canvas, root)

def point_is_on_line(point, p1, p2):
    '''
    Check if a point is on a line
    :param point: The point to check
    :param p1: The first point of the line
    :param p2: The second point of the line
    :return: True if the point is on the line, False otherwise
    '''
    # calculate the distance between the point and a line

    d = np.linalg.norm(np.cross(p2-p1, p1-point))/np.linalg.norm(p2-p1)
    print(d)
    return abs(d) < 5


def point_is_on_polygon_border(point, polygon):
    '''
    Check if a point is on the border of a polygon
    :param point: The point to check
    :param polygon: The polygon to check
    :return: True if the point is on the border of the polygon, False otherwise
    '''
    if point_is_on_line(point, polygon[0], polygon[1]):
        return True, TOP_SIDE
    if point_is_on_line(point, polygon[1], polygon[2]):
        return True, LEFT_SIDE
    if point_is_on_line(point, polygon[2], polygon[3]):
        return True, BOTTOM_SIDE
    if point_is_on_line(point, polygon[3], polygon[0]):
        return True, RIGHT_SIDE
    
    return False, -1

def clicked_on_enclosing_rect(x, y):
    '''
    Check if the user clicked on the enclosing rect
    :param x: The x coordinate of the click
    :param y: The y coordinate of the click
    :return: True if the user clicked on the enclosing rect, False otherwise
    '''
    global transformed_enclosing_rect
    if is_show_shape_enclosing_rect.get():
        return point_is_on_polygon_border((x, y), transformed_enclosing_rect)
    return False, -1

def update_crop_rect(x, y, side):
    '''
    Update the crop rect according to the mouse position
    :param x: The x coordinate of the mouse
    :param y: The y coordinate of the mouse
    :return: None
    '''
    global crop_rect, last_click_position, crop_side, enclosing_rect
    y_diff = y - last_click_position[Y]
    x_diff = x - last_click_position[X]

    if mirror.get() and (side == RIGHT_SIDE or side == LEFT_SIDE):
        x_diff = -x_diff

    # adjust distance according to the angle of the enclosing rect
    if side == TOP_SIDE or side == BOTTOM_SIDE:
        y_diff = y_diff * math.cos(angle)
    elif side == LEFT_SIDE or side == RIGHT_SIDE:
        x_diff = x_diff * math.cos(angle)

    crop_rect = copy.deepcopy(enclosing_rect)
    if crop_side == TOP_SIDE:
        crop_rect[TOP_LEFT] = (crop_rect[TOP_LEFT][X], crop_rect[TOP_LEFT][Y] + y_diff)
        crop_rect[TOP_RIGHT] = (crop_rect[TOP_RIGHT][X], crop_rect[TOP_RIGHT][Y] + y_diff)
    elif crop_side == LEFT_SIDE:
        crop_rect[TOP_LEFT] = (crop_rect[TOP_LEFT][X] + x_diff, crop_rect[TOP_LEFT][Y])
        crop_rect[BOTTOM_LEFT] = (crop_rect[BOTTOM_LEFT][X] + x_diff, crop_rect[BOTTOM_LEFT][Y])
    elif crop_side == BOTTOM_SIDE:
        crop_rect[BOTTOM_LEFT] = (crop_rect[BOTTOM_LEFT][X], crop_rect[BOTTOM_LEFT][Y] + y_diff)
        crop_rect[BOTTOM_RIGHT] = (crop_rect[BOTTOM_RIGHT][X], crop_rect[BOTTOM_RIGHT][Y] + y_diff)
    elif crop_side == RIGHT_SIDE:
        crop_rect[TOP_RIGHT] = (crop_rect[TOP_RIGHT][X] + x_diff, crop_rect[TOP_RIGHT][Y])
        crop_rect[BOTTOM_RIGHT] = (crop_rect[BOTTOM_RIGHT][X] + x_diff, crop_rect[BOTTOM_RIGHT][Y])
    last_click_position = (x, y)
    enclosing_rect = crop_rect
    update_enclosing_rect()
    update_screen()

def mouse_release(event):
    global is_crop
    if is_crop:
        print("Released")
        is_crop = False
        # update_crop_rect(event.x, event.y)

def mouse_click(event):
    global last_click_position, is_crop, crop_side
    last_click_position = (event.x, event.y)
    is_clicked_on_enclosing_rect, side = clicked_on_enclosing_rect(event.x, event.y)
    if is_clicked_on_enclosing_rect:
        is_crop = True
        crop_side = side
    elif is_click_to_position.get():
        set_translate(event.x, event.y)
        update_screen()
        
def mouse_drag(event):
    global last_click_position
    if is_crop:
        update_crop_rect(event.x,event.y, crop_side)
        last_click_position = (event.x, event.y)

    elif is_click_to_position.get():
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

def calculate_enclosing_rectangle(center_x, center_y, radius, start_angle, extent):
    # Convert angles from degrees to radians
    start_angle_rad = math.radians(start_angle)
    end_angle_rad = math.radians(start_angle + extent)

    # Calculate the coordinates of the four points of the enclosing rectangle
    x1 = center_x + radius * math.cos(start_angle_rad)
    y1 = center_y + radius * math.sin(start_angle_rad)

    x2 = center_x + radius * math.cos(end_angle_rad)
    y2 = center_y + radius * math.sin(end_angle_rad)

    x_min = min(x1, x2)
    y_min = min(y1, y2)
    x_max = max(x1, x2)
    y_max = max(y1, y2)



    return (x1,y1), (x2,y2)


def calc_shape_center_and_enclosing_rect(shapes):
    vertices = []
    for shape_elem in shapes:
        shape_type = shape_elem.attrib['type']
        shape_properties = shape_elem.attrib

        if shape_type == 'circle':
            c, r = parse_circle(shape_properties)
            start = shape_properties.get('start_angle')
            extent = shape_properties.get('extent')
            width = shape_properties.get('width')
            width = 0 if width is None else int(width)
            r = r + width
            if start is not None and extent is not None:
                p1,p2 = calculate_enclosing_rectangle(int(c[0]), int(c[1]), int(r), int(start), int(extent))
                vertices.append(p1)
                vertices.append(p2)
            else:
                vertices.append((c[0] - r, c[1] - r))
                vertices.append((c[0] + r, c[1] - r))
                vertices.append((c[0] + r, c[1] + r))
                vertices.append((c[0] - r, c[1] + r))

        elif shape_type == 'line':
            p1,p2 = parse_line(shape_properties)
            vertices.append(p1)
            vertices.append(p2)

        else:
            error("Shape type " + shape_type + " is not supported")
    
    # find the shape's enclosing rectangle
    min_x = min(vertices, key=lambda x: x[0])[0]
    max_x = max(vertices, key=lambda x: x[0])[0]
    min_y = min(vertices, key=lambda x: x[1])[1]
    max_y = max(vertices, key=lambda x: x[1])[1]
    # round the values
    min_x = round(min_x)
    max_x = round(max_x)
    min_y = round(min_y)
    max_y = round(max_y)

    border = [(),(),(),()]
    border[TOP_RIGHT] = (max_x, min_y)
    border[TOP_LEFT] = (min_x, min_y)
    border[BOTTOM_LEFT] = (min_x, max_y)
    border[BOTTOM_RIGHT] = (max_x, max_y)

    return np.mean(vertices, axis=0), border


def load_file():
    global root
    global canvas
    global window
    global scale, angle, translate_X, translate_Y, shape_center, enclosing_rect, transformation_matrix

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

    # Reset the shape center
    shape_center, enclosing_rect = calc_shape_center_and_enclosing_rect(root.findall('Shape'))
    
    # Reset the translation
    set_translate_X(WINDOW_WIDTH/2)
    set_translate_Y(WINDOW_HEIGHT/2)


    # Draw the image
    draw_image(canvas, root)

def reset():
    global canvas
    global window
    global scale, angle, translate_X, translate_Y, shape_center, transformation_matrix, enclosing_rect

    # Clear the canvas
    canvas.delete("all")

    # Reset the transformation matrix
    transformation_matrix = np.identity(3)

    # Reset the scale
    scale = 1

    # Reset the angle
    angle = 0
    slider.set(0)

    enclosing_rect = original_enclosing_rect
    update_enclosing_rect()

    # Reset the translation
    set_translate_X(WINDOW_WIDTH/2)
    set_translate_Y(WINDOW_HEIGHT/2)

    # Draw the image
    draw_image(canvas, root)

def on_mirror_change():
    update_transformation_matrix()
    update_screen()

def main():
    global root, canvas, window, slider, crop_rect
    global scale, angle, translate_X, translate_Y, shape_center, enclosing_rect
    global is_click_to_position, is_show_shape_enclosing_rect, mirror, original_enclosing_rect

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
    is_show_shape_enclosing_rect = tk.BooleanVar()
    is_show_shape_enclosing_rect.set(False)
    is_show_shape_enclosing_rect.trace("w", lambda name, index, mode, sv=is_show_shape_enclosing_rect: update_screen())
    mirror = tk.BooleanVar()
    mirror.set(False)
    mirror.trace("w", lambda name, index, mode, sv=mirror: on_mirror_change())

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
    optionsmenu.add_checkbutton(label="Show shape enclosing rectangle", variable=is_show_shape_enclosing_rect, onvalue=True, offvalue=False)
    optionsmenu.add_checkbutton(label="Mirror", variable=mirror, onvalue=True, offvalue=False)
    

    canvas.bind("<Button-1>", mouse_click)
    canvas.bind("<Button1-Motion>", mouse_drag)
    canvas.bind("<ButtonRelease-1>", mouse_release)

    if is_windows:
        canvas.bind("<MouseWheel>", mouse_wheel)
    else:
        canvas.bind("<Button-4>", scroll_up)
        canvas.bind("<Button-5>", scroll_down)

    # calculate the shape's center
    shape_center, enclosing_rect = calc_shape_center_and_enclosing_rect(root.findall('Shape'))
    original_enclosing_rect = enclosing_rect
    crop_rect = copy.deepcopy(enclosing_rect)

    # center the shape to the center of the window
    set_translate_X(WINDOW_WIDTH/2)
    set_translate_Y(WINDOW_HEIGHT/2)

    draw_image(canvas, root)
    window.mainloop()


if __name__ == "__main__":
    main()