#!/usr/bin/env python

from __future__ import with_statement
from math import *
from xml.sax import saxutils
import csv, sys

# All commented methods were lifted from:
# http://code.google.com/p/kmlcircle/

#
# Convert (x,y,z) on unit sphere
# back to (long, lat)
#
# p is vector of three elements
# 
def toEarth(p):
    if (p[0] == 0.0):
        longitude = pi / 2.0
    else:
        longitude = atan(p[1]/p[0])
    colatitude = acos(p[2]);
    latitude = (pi / 2.0 - colatitude)

    # select correct branch of arctan
    if p[0] < 0.0:
        if p[1] <= 0.0:
            longitude = -(pi - longitude)
        else:
            longitude = pi + longitude

    DEG = 180.0 / pi
    return [longitude * DEG, latitude * DEG]

#c
# convert long, lat IN RADIANS to (x,y,z)
# 
def toCart(longitude, latitude):
    theta = longitude
    # spherical coordinate use "co-latitude", not "lattitude"
    # lattiude = [-90, 90] with 0 at equator
    # co-latitude = [0, 180] with 0 at north pole
    phi = pi / 2.0 - latitude
    return [ cos(theta) * sin(phi), sin(theta) * sin(phi), cos(phi)]

# spoints -- get raw list of points in long,lat format
#
# meters: radius of polygon
# n: number of sides
# offset: rotate polygon by number of degrees
#
# Returns a list of points comprising the object
#
def spoints(long, lat, meters, n, offset=0):
    # constant to convert to radians
    RAD = pi / 180.0;
    # Mean Radius of Earth, meters
    MR = 6378.1 * 1000.0;
    offsetRadians = offset * RAD
    # compute longitude degrees (in radians) at given latitude
    r = (meters / (MR * cos(lat * RAD)))

    vec = toCart(long * RAD, lat * RAD)
    pt = toCart(long * RAD + r, lat * RAD)
    pts = [ ]

    for i in range(0,n):
        pts.append(toEarth(rotPoint(vec, pt, offsetRadians + (2.0 * pi/n)*i)))

    # connect to starting point exactly
    # not sure if required, but seems to help when
    # the polygon is not filled
    pts.append(pts[0])
    return pts

#
# rotate point pt, around unit vector vec by phi radians
# http://blog.modp.com/2007/09/rotating-point-around-vector.html
# 
def rotPoint(vec, pt,  phi):
    # remap vector for sanity
    (u,v,w,x,y,z) = (vec[0],vec[1],vec[2], pt[0],pt[1],pt[2])

    a = u*x + v*y + w*z;
    d = cos(phi);
    e = sin(phi);

    return [ (a*u + (x - a*u)*d + (v*z - w*y) * e),
             (a*v + (y - a*v)*d + (w*x - u*z) * e),
             (a*w + (z - a*w)*d + (u*y - v*x) * e) ]

#
# Regular polygon
# (longitude, latitude) in decimal degrees
# meters is radius in meters
# segments is number of sides, > 20 looks like a circle
# offset, rotate polygon by a number of degrees
#
# returns a string suitable for adding to a KML file.
#
# You may want to
#  edit this function to change "extrude" and other XML nodes.
#
def kml_regular_polygon(long, lat, meters, segments=30, offset=0):
    s = "<Polygon>\n"
    s += "  <outerBoundaryIs><LinearRing><coordinates>\n"
    for p in spoints(long, lat, meters, segments, offset):
        s += "    " + str(p[0]) + "," + str(p[1]) + "\n"
    s += "  </coordinates></LinearRing></outerBoundaryIs>\n"
    s += "</Polygon>\n"
    return s
    
if len(sys.argv) is 3:
    input_file = sys.argv[1]
    output_file = sys.argv[2]
else:
    print('You must specify an input csv of name, lat, lng, radius (in meters) and an output file for the kml file')
    sys.exit(2)
    
with open(input_file, 'r') as file:
    reader = csv.reader(file)
    with open(output_file, 'w') as output:
        output.write('<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://earth.google.com/kml/2.0">\n')
        output.write('<Folder>\n')
        for row in reader:               
            if row[1] != '#N/A' and row[2] != '#N/A': 
                name = saxutils.escape(row[0])
                lat = float(row[1])
                lng = float(row[2])
                radius_in_miles = float(row[3])
                radius_in_meters = radius_in_miles * 1609.34
                output.write('<Placemark>\n')
                output.write('<name>')
                output.write(name)
                output.write('</name>\n')
                output.write('<visibility>1</visibility>\n')
                output.write(kml_regular_polygon(lng, lat, radius_in_meters))
                output.write('</Placemark>\n')  
        output.write('</Folder>\n')
        output.write('</kml>')      
              