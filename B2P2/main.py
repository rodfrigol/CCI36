import xml.etree.ElementTree as ET
import os
import sys
import numpy as np

class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def __str__(self):
        return "({}, {}, {})".format(self.x, self.y, self.z)

class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
    
    def __str__(self):
        return "({}, {}, {})".format(self.r, self.g, self.b)

class Triangle:
    def __init__(self, p1, p2, p3, c1, c2, c3):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.c1 = c1
        self.c2 = c2
        self.c3 = c3
        self.color = None
        self.normal = None
        self.area = None
        self.centroid = None
        self.e = None
    
    def __str__(self):
        return "1: {}, {} \n2: {}, {} \n3: {}, {}\ncolor: {}\nnormal: {}\narea: {}\ncentroid: {}\nE: {}\n" \
            .format(self.p1, self.c1, self.p2, self.c2, self.p3, self.c3, self.color, self.normal, self.area, self.centroid, self.e)

    def get_color(self):
        r = np.mean(np.array([self.c1.r, self.c2.r, self.c3.r]))
        g = np.mean(np.array([self.c1.g, self.c2.g, self.c3.g]))
        b = np.mean(np.array([self.c1.b, self.c2.b, self.c3.b]))
        self.color = Color(r, g, b)
    
    def get_normal_and_area(self):
        p1 = np.array([self.p1.x, self.p1.y, self.p1.z])
        p2 = np.array([self.p2.x, self.p2.y, self.p2.z])
        p3 = np.array([self.p3.x, self.p3.y, self.p3.z])
        cross = np.cross(p2 - p1, p3 - p1)
        norm = np.linalg.norm(cross)
        self.normal = cross / norm
        self.area = norm / 2
    
    def get_centroid(self):
        x = np.mean(np.array([self.p1.x, self.p2.x, self.p3.x]))
        y = np.mean(np.array([self.p1.y, self.p2.y, self.p3.y]))
        z = np.mean(np.array([self.p1.z, self.p2.z, self.p3.z]))
        self.centroid = np.array([x, y, z])
    
    def get_e(self, geo_name):
        if geo_name == "Cube.001" and self.normal[1] == -1:
            self.e = 1
        else:
            self.e = 0

def get_doc():
    # parse xml
    dir_file = os.path.dirname(os.path.realpath(__file__))
    return ET.parse(dir_file + "/source/cci36lab2.dae")

def get_triangles(doc, ns):
    triangles = []

    geometries = doc.findall(".//geometry", ns)
    for geometry in geometries:
        #
        #if geometry.attrib.get("name") != "Cube.001":
        #    continue

        sources = geometry.findall(".//source", ns)
        m = doc.find(".//instance_geometry[@url='{}']...//matrix".format("#" + geometry.attrib.get("id")), ns)
        vec = m.text.split(" ")

        scaleX = float(vec[0])
        scaleY = float(vec[5])
        scaleZ = float(vec[10])
        locX = float(vec[3])
        locY = float(vec[7])
        locZ = float(vec[11])

        # get points
        points_float_array = sources[0].find(".//float_array", ns)
        points_arr = points_float_array.text.split(" ")
        points = []
        for i in range(int(len(points_arr) / 3)):
            offset = i * 3
            x = float(points_arr[offset]) * scaleX + locX
            y = float(points_arr[offset + 1]) * scaleY + locY
            z = float(points_arr[offset + 2]) * scaleZ + locZ
            points.append(Point(x, y, z))

        # get colors
        colors_float_array = sources[3].find(".//float_array", ns)
        colors_arr = colors_float_array.text.split(" ")
        colors = []
        for i in range(int(len(colors_arr) / 4)):
            offset = i * 4
            r = float(colors_arr[offset])
            g = float(colors_arr[offset + 1])
            b = float(colors_arr[offset + 2])
            colors.append(Color(r, g, b))
        
        # build triangles
        triangle = geometry.find(".//triangles//p", ns)
        indexes = triangle.text.split(" ")
        for i in range(int(len(indexes) / 12)):
            offset = i * 12
            p1 = points[int(indexes[offset])]
            p2 = points[int(indexes[offset + 4])]
            p3 = points[int(indexes[offset + 8])]
            c1 = colors[int(indexes[offset + 3])]
            c2 = colors[int(indexes[offset + 7])]
            c3 = colors[int(indexes[offset + 11])]
            tr = Triangle(p1, p2, p3, c1, c2, c3)
            # calculate attributes of triangle
            tr.get_color()
            tr.get_normal_and_area()
            tr.get_centroid()
            tr.get_e(geometry.attrib.get("name"))
            triangles.append(tr)
    return triangles

def has_intersection(t1_centroid, r, r2, mod_r, triangles, i, j, intersections):
    if i > j:
        aux = j
        j = i
        i = aux
    if i not in intersections:
        intersections[i] = {}
    elif j in intersections[i]:
        return intersections[i][j]
    for tr in triangles:
        vec = tr.centroid - t1_centroid
        intersection_lambda = np.dot(vec, r) / r2
        if intersection_lambda > 0.1 and intersection_lambda < 0.9:
            d = np.linalg.norm(np.cross(vec, r)) / mod_r
            if d < 0.2:
                intersections[i][j] = True
                return True
    intersections[i][j] = False
    return False

def get_ff(i, j, triangles, intersections):
    t1 = triangles[i]
    t2 = triangles[j]

    r = t2.centroid - t1.centroid
    r2 = np.dot(r, r)
    if r2 == 0:
        return 0
    mod_r = np.sqrt(r2)

    cos01 = np.dot(r, t1.normal) / mod_r
    if cos01 < 0:
        return 0
    cos02 = -np.dot(r, t2.normal) / mod_r

    if has_intersection(t1.centroid, r, r2, mod_r, triangles, i, j, intersections):
        return 0
    
    return (cos01 * cos02 * t2.area) / (np.pi * r2 + t2.area)

def solve_equations(triangles, form_factors, colors):
    n = len(triangles)
    resp = {}
    for color in colors:
        matrix = []
        E = []
        for i in range(n):
            E.append(triangles[i].e)
            p = getattr(triangles[i].color, color)
            row = []
            for j in range(n):
                if i == j:
                    row.append(1)
                else:
                    row.append(-p * form_factors[i][j])
            matrix.append(row)
        matrix = np.linalg.inv(matrix)
        resp[color] = np.matmul(matrix, E)
        resp[color] *= 200
    return resp

def get_form_factors(triangles):
    ffs = []
    intersections = {}
    n = len(triangles)
    for i in range(n):
        print("{}/{}".format(i, n))
        ffs.append([])
        for j in range(n):
            ffs[i].append(get_ff(i, j, triangles, intersections))
    return ffs

def create_new_file(resp, doc, ns):
    i = 0

    geometries = doc.findall(".//geometry", ns)
    for geometry in geometries:
        colors = []

        sources = geometry.findall(".//source", ns)
        
        triangle = geometry.find(".//triangles//p", ns)
        indexes = triangle.text.split(" ")
        for j in range(int(len(indexes) / 12)):
            colors.append(resp['r'][i])
            colors.append(resp['g'][i])
            colors.append(resp['b'][i])
            colors.append(1)
            colors.append(resp['r'][i])
            colors.append(resp['g'][i])
            colors.append(resp['b'][i])
            colors.append(1)
            colors.append(resp['r'][i])
            colors.append(resp['g'][i])
            colors.append(resp['b'][i])
            colors.append(1)
            i += 1
        
        colors_float_array = sources[3].find(".//float_array", ns)
        colors_float_array.text = " ".join([str(x) for x in colors])
    
    dir_file = os.path.dirname(os.path.realpath(__file__))
    doc.write(dir_file + "/output.dae")

if __name__ == "__main__":
    ns = {'': 'http://www.collada.org/2005/11/COLLADASchema'}
    colors = ['r', 'g', 'b']

    # parse xml
    doc = get_doc()

    # get data from xml file
    triangles = get_triangles(doc, ns)

    # calculate form_factors
    form_factors = get_form_factors(triangles)
    
    # solve equations
    resp = solve_equations(triangles, form_factors, colors)

    # change colors on doc
    create_new_file(resp, doc, ns)

