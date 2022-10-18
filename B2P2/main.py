import xml.etree.ElementTree as ET
import os
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
        self.centroid = Point(x, y, z)
    
    def get_e(self, geo_name):
        if geo_name == "Cube.001" and self.normal[1] == -1:
            self.e = 1
        else:
            self.e = 0

def get_triangles():
    triangles = []
    # parse xml
    dir_file = os.path.dirname(os.path.realpath(__file__))
    doc = ET.parse(dir_file + "/source/cci36lab2.dae")
    ns = {'': 'http://www.collada.org/2005/11/COLLADASchema'}

    geometries = doc.findall(".//geometry", ns)
    for geometry in geometries:
        sources = geometry.findall(".//source", ns)
        if len(sources) < 4:
            continue
        # get points
        points_float_array = sources[0].find(".//float_array", ns)
        points_arr = points_float_array.text.split(" ")
        points = []
        for i in range(int(len(points_arr) / 3)):
            offset = i * 3
            x = float(points_arr[offset])
            y = float(points_arr[offset + 1])
            z = float(points_arr[offset + 2])
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

def get_ff(t1, t2):
    t1_centroid = np.array([t1.centroid.x, t1.centroid.y, t1.centroid.z])
    t2_centroid = np.array([t2.centroid.x, t2.centroid.y, t2.centroid.z])
    r = t2_centroid - t1_centroid

    if np.dot(r, t1.normal) <= 0:
        return 0

    r2 = np.dot(r, r)
    #TODO


def get_form_factors(triangles):
    ffs = []
    for i in range(len(triangles)):
        ffs.append([])
        for j in range(i):
            ffs[i].append(get_ff(triangles[i], triangles[j]))
        ##
        if i == 1:
            break
    return ffs

if __name__ == "__main__":
    # get data from xml file
    triangles = get_triangles()

    # calculate form_factors
    form_factors = get_form_factors(triangles)

