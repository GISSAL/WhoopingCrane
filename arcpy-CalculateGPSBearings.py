#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    File name: arcpy-CalculateGPSBearings.py
    Author: Shawn Hutchinson
    Description:  Calculates the bearing between points in a GPS dataset and two seasonal destinations
    Date created: 03/06/2024
    Python Version: 3.9.16
"""
# Create custom error class
class ProjectionError(Exception):
    pass

# Import required modules
import arcpy, time
from math import radians, cos, sin, asin, sqrt, atan2, degrees

# Define key environment settings:
arcpy.env.overwriteOutput = True

# Create local variable(s):
gpsPoints = arcpy.GetParameterAsText(0) #GPS telemetry points
destNorth = arcpy.GetParameterAsText(1) #Northern migratory destination (Wood Buffalo NP)
destSouth = arcpy.GetParameterAsText(2) #Southern migratory destination (Aransas NWR)
updatedRecords = 0

# Custom function to calculate bearings from
# https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
def compass_bearing(pointA, pointB):
    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")
    lat1 = radians(pointA[0])
    lat2 = radians(pointB[0])
    diffLong = radians(pointB[1] - pointA[1])
    x = sin(diffLong) * cos(lat2)
    y = cos(lat1) * sin(lat2) - (sin(lat1) * cos(lat2) * cos(diffLong))
    initial_bearing = atan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    return compass_bearing

try:
    # Start timer
    start = time.time()

    # Check to make sure all destination files are in WGS 1984 (WKID 4326)
    if arcpy.Describe(destNorth).spatialReference.name == "GCS_WGS_1984" and arcpy.Describe(destSouth).spatialReference.name == "GCS_WGS_1984":
        pass
    else:
        raise ProjectionError

    # Extract x, y coordinates for destNorth and destSouth point features (centroid returned for polys)
    with arcpy.da.SearchCursor(destNorth, ["SHAPE@XY"]) as cursor:
        for row in cursor:
            northYX = tuple(reversed(row[0]))
    with arcpy.da.SearchCursor(destSouth, ["SHAPE@XY"]) as cursor:
        for row in cursor:
            southYX = tuple(reversed(row[0]))

    # Add bearing fields to input GPS points
    listFields = arcpy.ListFields(gpsPoints)
    listFieldNames = [field.name for field in listFields]
    if "bearingN" in listFieldNames:
        print("Field 'bearingN' already exists...existing values will be overwritten!")
        arcpy.AddMessage("Field 'bearingN' already exists...existing values will be overwritten!")
    else:
        arcpy.management.AddField(gpsPoints, "bearingN", "FLOAT")
    if "bearingS" in listFieldNames:
        print("Field 'bearingS' already exists...existing values will be overwritten!")
        arcpy.AddMessage("Field 'bearingS' already exists...existing values will be overwritten!")
    else:
        arcpy.management.AddField(gpsPoints, "bearingS", "FLOAT")

    # Use a cursor to calculate and write bearings
    with arcpy.da.UpdateCursor(gpsPoints, ["SHAPE@XY", "bearingN", "bearingS"]) as cursor:
        for row in cursor:
            x, y = row[0]
            row[1] = compass_bearing((y, x), northYX)
            row[2] = compass_bearing((y, x), southYX)
            cursor.updateRow(row)
            updatedRecords += 1
    print("Calculated compass bearings added to GPS point feature class...")
    arcpy.AddMessage("Calculated compass bearings added to GPS point feature class...")

except arcpy.ExecuteError:
    for i in range(0, arcpy.GetMessageCount()):
        arcpy.AddMessage("{0}:  {1}".format(arcpy.GetSeverity(i), arcpy.GetMessage(i)))
        
except ProjectionError:
    print("Destination files are not in GCS WGS 1984 spatial reference!  Reproject and start again...")
    arcpy.AddError("Destination files are not in GCS WGS 1984 spatial reference!  Reproject and start again...")
    
except:
    print("An unexpected error occurred processing the input file {0}".format(arcpy.Describe(gpsPoints).baseName))
    arcpy.AddError("An unexpected error occurred processing the input file {0}".format(arcpy.Describe(gpsPoints).baseName))
    
finally:    
    # Report script tool execution time if an exception is encountered
    if "end" in locals():
        pass
    else:
        end = time.time()
        print("Total bearings calculated = {0}".format(str(updatedRecords)))    
        arcpy.AddMessage("Total bearings calculated = {0}".format(str(updatedRecords)))    
        print("Total execution time (secs) = {0}".format(str(round(end - start, 3))))    
        arcpy.AddMessage("Total execution time (secs) = {0}".format(str(round(end - start, 3))))