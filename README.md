# Whooping Crane Stopover Habitat Assessment
Repository for Whooping Crane stopover habitat modeling and assessment project being conducted with the Kansas Department of Wildlife and Parks and funded by the U.S. Fish and Wildlife Service.

## Contents
<ul>
  <li>arcpy-CalculateGPSBearings.py</li>
</ul>

## arcpy-CalculateGPSBearings.py

Python script formatted as an ArcGIS Pro script-based tool that calculates bearings (in degrees) to summer and winter migration destinations.  Bearing data can be used as an explanatory variable in Whooping Crane habitat selection models.  The script contains a custom "compass_bearing" functions based on the Haversine formula and adapted from a user contribution posted to [Stack Overflow](https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points):

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
