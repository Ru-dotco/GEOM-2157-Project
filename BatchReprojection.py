# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProject,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterString,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
from qgis import (processing,
                  os)
from qgis.utils import iface

class BatchReprojectLayers(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    SUFFIX = 'SUFFIX'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return BatchReprojectLayers()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'batchreprojectlayers'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('reproject all layers in a folder')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Example scripts')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'examplescripts'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr(" tool reprojects all shapefiles in a folder to match the coordinate system of a shapefile selected"
        "from that folder. As inputs it requires a shapefile selcted from a file picker and a suffix to amend the name of the projected shapefiles")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('select a shapefile with the correct coordinate system'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterString(
                self.SUFFIX,
                self.tr('Enter the suffix you want to append to the reprojected filenames')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )

        # If source was not found, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSourceError method to return a standard
        # helper text for when a source cannot be evaluated
        suffix = self.parameterAsString(
            parameters,
            self.SUFFIX,
            context
        )


        # Send some information to the user
        feedback.pushInfo('CRS is {}'.format(source.sourceCrs().authid()))
    

        chosenFile = self.parameterDefinition('INPUT').valueAsPythonString(parameters['INPUT'], context)
        filepath = os.path.dirname(chosenFile[1:]) + '/'
        feedback.pushInfo(filepath) 
        
        inputFileList = []
        outputFileList = []
        
        coordRefSystem = source.sourceCrs().authid()
        
        #loop throug files and get file name, add to list
        for file in os.listdir(filepath):
            if file.endswith(".shp"):#to get only shapefiles
                #add layer to view and get coord
                layer = iface.addVectorLayer((filepath + file), file[:-4], "ogr")
                layerCRS = layer.sourceCrs().authid()
                #if layer not in coord system include it in list for processing
                if layerCRS != coordRefSystem:
                    print(layer.name())
                    #check for files that already have suffix
                    if not suffix in file:
                        inputFileList.append(file)
                        #rename file to include suffix
                        outputFileName = file[:-4] + suffix + file[-4:]
                        #add file name to output list
                        outputFileList.append(outputFileName)
                        #construct dictionary
                        parameterDict = {"INPUT":(filepath + file),"TARGET_CRS" : coordRefSystem, "OUTPUT" : (filepath + outputFileName)}
                        print(parameterDict)
                        #run reprojection tool
                        processing.run("native:reprojectlayer", parameterDict)
        QgsProject.instance().clear()
        return {}
