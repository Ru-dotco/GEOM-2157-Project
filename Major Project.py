filepath = "/Users/61410/gisprog/LaData/Data/"
rcFileName = "clipped.tif"
bcFileName = "PRIORITY_RIVERS.shp"
dcFileName = "LGA_POLYGON.shp"
vcFileName = "VLR_POINT.shp"
outputList =[]
crs = "EPSG:28354"
buffOutput = "buffered.shp"
outputList.append(buffOutput)

rcLayer = iface.addRasterLayer(filepath + rcFileName, rcFileName[:-4])
bcLayer = iface.addVectorLayer(filepath + bcFileName, bcFileName[:-4], "ogr")
dcLayer = iface.addVectorLayer(filepath + dcFileName, dcFileName[:-4], "ogr")
vcLayer = iface.addVectorLayer(filepath + vcFileName, vcFileName[:-4], "ogr")

parameterDict = {'INPUT': bcLayer,'DISTANCE':100,'SEGMENTS':5,
                'END_CAP_STYLE':0,'JOIN_STYLE':0,'MITER_LIMIT':2,
                'DISSOLVE':False,'OUTPUT':(filepath + buffOutput)}
processing.run("native:buffer", parameterDict)

parameterDict = {'INPUT': bcLayer,'DISTANCE':100,'SEGMENTS':5,
                'END_CAP_STYLE':0,'JOIN_STYLE':0,'MITER_LIMIT':2,
                'DISSOLVE':False,'OUTPUT':(filepath + buffOutput)}
processing.run("native:buffer", parameterDict)