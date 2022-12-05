import os 
import processing
from PyQt5 import QtGui
#add filepath and files
filepath = "/Users/61410/SIS/VM/"
inputFileList = []
outputFileList = []
suffix = "_slope"
buffer = "_buff"
drFileName = "drainrast.sdat"
outputFileList.append(drFileName)
wtFileName = "weighted.tif"
outputFileList.append(wtFileName)
cpFileName = "clip.tif"
outputFileList.append(cpFileName)
bcFileName = "PRIORITY_RIVERS.shp"
vcFileName = "VLR_POINT.shp"
fn = "newlandfill.shp"
outputFileList.append(fn)
#create for statement to add raster and shapefiles
for file in os.listdir(filepath):
    if file.endswith(".tif"):
        layer = iface.addRasterLayer((filepath + file), file[:-4])
        if not suffix in file:
            inputFileList.append(file)
            #rename file to include suffix
            outputFileName = file[:-4] + suffix + file[-4:]
            
            #add file name to output list
            outputFileList.append(outputFileName)
            parameterDict = {'INPUT': (filepath + file),'Z_FACTOR':1,'OUTPUT':(filepath + outputFileName)}
            print(parameterDict)
            processing.runAndLoadResults("native:slope", parameterDict)
            
            #calculates the drainage density using the DEM
            param = { 'BASIN' : (filepath + drFileName) , 'BASINS' : 'TEMPORARY_OUTPUT', 
            'CONNECTION' : 'TEMPORARY_OUTPUT',  'DEM' : layer,
            'DIRECTION' : 'TEMPORARY_OUTPUT',  'NODES' : 'TEMPORARY_OUTPUT', 
            'ORDER' : 'TEMPORARY_OUTPUT',  'SEGMENTS' : 'TEMPORARY_OUTPUT',  'THRESHOLD' : 5 }
            processing.runAndLoadResults("saga:channelnetworkanddrainagebasins", param)
            
            #calculates the weighted sum using slope layer and drainage density
            paramCalc = { 'CELLSIZE' : 7, 'CRS' : None,'EXPRESSION' : ' ( \"drainrast@1\" * 0.4) + ( \"clipped_slope@1\" * 0.6)', 
            'EXTENT' : None, 'LAYERS' : [filepath + outputFileName], 'OUTPUT' : filepath + wtFileName}
            processing.runAndLoadResults("qgis:rastercalculator", paramCalc)
            wtLayer = iface.addRasterLayer(filepath + wtFileName, wtFileName[:-4])
            
            #symbolize output
            wtLayer = iface.addRasterLayer(filepath + wtFileName, wtFileName[:-4])
            s = QgsRasterShader()
            c = QgsColorRampShader()
            c.setColorRampType(QgsColorRampShader.Interpolated)
            i =[]
            i.append(QgsColorRampShader.ColorRampItem(5, QtGui.QColor("#d7191c"), "5"))
            i.append(QgsColorRampShader.ColorRampItem(15, QtGui.QColor("#fdae61"), "15"))
            i.append(QgsColorRampShader.ColorRampItem(25, QtGui.QColor("#ffffbf"), "25"))
            i.append(QgsColorRampShader.ColorRampItem(35, QtGui.QColor("#abdda4"), "35"))
            c.setColorRampItemList(i)
            s.setRasterShaderFunction(c)
            ps = QgsSingleBandPseudoColorRenderer(wtLayer.dataProvider(), 1, s)
            wtLayer.setRenderer(ps)
    #adds vector layers for buffering
    elif file.endswith(".shp"):
        layer = iface.addVectorLayer(filepath + file, file[:-4], "ogr")
        if not buffer in file:
            inputFileList.append(file)
            outputFileName = file[:-4] + buffer + file[-4:]
            outputFileList.append(outputFileName)
            #buffer algorithm buffers vector layers
            parameterDict = {'INPUT':(filepath + file),'DISTANCE':30,'SEGMENTS':5,'END_CAP_STYLE':0,'JOIN_STYLE':0,'MITER_LIMIT':2,
                            'DISSOLVE':False,'OUTPUT':(filepath + outputFileName)}
            processing.runAndLoadResults("native:buffer", parameterDict)
            #clips the weithed raster layer using hte buffered features
            parameterClip = {'INPUT':wtLayer,'MASK':(filepath + outputFileName),'NO DATA': "",
                'ALPHA_BAND':False,'CROP_TO_CUTLINE':True,'KEEP_RESOLUTION':True,
                'OPTIONS':'','DATA_TYPE': 0, 'OUTPUT':(filepath + cpFileName)}
            processing.runAndLoadResults("native:clip", parameterClip)
            clipLayer = iface.addRasterLayer(filepath + cpFileName)
            bcLayer = iface.addVectorLayer(filepath + bcFileName, bcFileName[:-4], "ogr")
            vcLayer = iface.addVectorLayer(filepath + vcFileName, vcFileName[:-4], "ogr")
            
            #calculate length of priority rivers
            data_pr = bcLayer.dataProvider()
            layer = bcLayer
            pv = layer.dataProvider()
            pv.addAttributes([QgsField('length', QVariant.Double),\
            QgsField('calc', QVariant.Double),\
            QgsField('area', QVariant.Double)])

            layer.updateFields()

            expression1 = QgsExpression('$length')
            expression2 = QgsExpression('"lengthm"/""length"')

            context = QgsExpressionContext()
            context.appendScopes(\
            QgsExpressionContextUtils.globalProjectLayerScopes(layer))

            with edit(layer):
                for f in layer.getFeatures():
                    context.setFeature(f)
                    f['length'] = expression1.evaluate(context)
                    layer.updateFeature(f)
                    
            with edit(layer):
                for f in layer.getFeatures():
                    context.setFeature(f)
                    f['calc'] = expression2.evaluate(context)
                    layer.updateFeature(f)

            layer.commitChanges()
            #filters rivers by priority level
            list = []
            my_char = "Y"
            bcLayer.setSubsetString("PRIORTYRVR LIKE '"+my_char+"%'")
            print("The following rivers are priority {}:".format(my_char))
            for feature in bcLayer.getFeatures():
                list.append(feature['RIVERNAME'])
            
            
            #add new landfill in suitable area
            layerFields = QgsFields()
            layerFields.append(QgsField('id', QVariant.Int))
            layerFields.append(QgsField('value', QVariant.Double))
            layerFields.append(QgsField('name', QVariant.String))

            writer = QgsVectorFileWriter(fn, 'UTF-8', layerFields, QgsWkbTypes.Point,\
            QgsCoordinateReferenceSystem('ESPG:28354'),'ESRI Shapefile')

            feat = QgsFeature()
            feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(747930, 5724503)))
            feat.setAttributes([1, 1.1, 'name'])

            writer.addFeature(feat)

            iface.addVectorLayer(fn, '', 'ogr')

            del(writer)
    
           













