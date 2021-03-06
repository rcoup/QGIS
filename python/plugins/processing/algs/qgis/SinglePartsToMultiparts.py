# -*- coding: utf-8 -*-

"""
***************************************************************************
    SinglePartsToMultiparts.py
    ---------------------
    Date                 : August 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.PyQt.QtGui import QIcon

from qgis.core import Qgis, QgsFeature, QgsGeometry, QgsWkbTypes

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.core.parameters import ParameterVector
from processing.core.parameters import ParameterTableField
from processing.core.outputs import OutputVector
from processing.tools import dataobjects, vector

pluginPath = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]


class SinglePartsToMultiparts(GeoAlgorithm):

    INPUT = 'INPUT'
    FIELD = 'FIELD'
    OUTPUT = 'OUTPUT'

    def getIcon(self):
        return QIcon(os.path.join(pluginPath, 'images', 'ftools', 'single_to_multi.png'))

    def defineCharacteristics(self):
        self.name, self.i18n_name = self.trAlgorithm('Singleparts to multipart')
        self.group, self.i18n_group = self.trAlgorithm('Vector geometry tools')

        self.addParameter(ParameterVector(self.INPUT, self.tr('Input layer')))
        self.addParameter(ParameterTableField(self.FIELD,
                                              self.tr('Unique ID field'), self.INPUT))

        self.addOutput(OutputVector(self.OUTPUT, self.tr('Multipart')))

    def processAlgorithm(self, progress):
        layer = dataobjects.getObjectFromUri(self.getParameterValue(self.INPUT))
        fieldName = self.getParameterValue(self.FIELD)

        geomType = self.singleToMultiGeom(layer.wkbType())

        writer = self.getOutputFromName(self.OUTPUT).getVectorWriter(
            layer.fields().toList(), geomType, layer.crs())

        inFeat = QgsFeature()
        outFeat = QgsFeature()
        inGeom = QgsGeometry()
        outGeom = QgsGeometry()

        index = layer.fieldNameIndex(fieldName)
        unique = vector.getUniqueValues(layer, index)

        current = 0
        features = vector.features(layer)
        total = 100.0 / (len(features) * len(unique))
        if not len(unique) == layer.featureCount():
            for i in unique:
                multi_feature = []
                first = True
                features = vector.features(layer)
                for inFeat in features:
                    atMap = inFeat.attributes()
                    idVar = atMap[index]
                    if unicode(idVar).strip() == unicode(i).strip():
                        if first:
                            attrs = atMap
                            first = False
                        inGeom = inFeat.geometry()
                        vType = inGeom.type()
                        feature_list = self.extractAsMulti(inGeom)
                        multi_feature.extend(feature_list)

                    current += 1
                    progress.setPercentage(int(current * total))

                outFeat.setAttributes(attrs)
                outGeom = QgsGeometry(self.convertGeometry(multi_feature,
                                                           vType))
                outFeat.setGeometry(outGeom)
                writer.addFeature(outFeat)

            del writer
        else:
            raise GeoAlgorithmExecutionException(
                self.tr('At least two features must have same attribute '
                        'value! Please choose another field...'))

    def singleToMultiGeom(self, wkbType):
        try:
            if wkbType in (QgsWkbTypes.Point, QgsWkbTypes.MultiPoint,
                           QgsWkbTypes.Point25D, QgsWkbTypes.MultiPoint25D):
                return QgsWkbTypes.MultiPoint
            elif wkbType in (QgsWkbTypes.LineString, QgsWkbTypes.MultiLineString,
                             QgsWkbTypes.MultiLineString25D,
                             QgsWkbTypes.LineString25D):

                return QgsWkbTypes.MultiLineString
            elif wkbType in (QgsWkbTypes.Polygon, QgsWkbTypes.MultiPolygon,
                             QgsWkbTypes.MultiPolygon25D, QgsWkbTypes.Polygon25D):

                return QgsWkbTypes.MultiPolygon
            else:
                return QgsWkbTypes.Unknown
        except Exception:
            pass

    def extractAsMulti(self, geom):
        if geom.type() == QgsWkbTypes.PointGeometry:
            if geom.isMultipart():
                return geom.asMultiPoint()
            else:
                return [geom.asPoint()]
        elif geom.type() == QgsWkbTypes.LineGeometry:
            if geom.isMultipart():
                return geom.asMultiPolyline()
            else:
                return [geom.asPolyline()]
        else:
            if geom.isMultipart():
                return geom.asMultiPolygon()
            else:
                return [geom.asPolygon()]

    def convertGeometry(self, geom_list, vType):
        if vType == QgsWkbTypes.PointGeometry:
            return QgsGeometry().fromMultiPoint(geom_list)
        elif vType == QgsWkbTypes.LineGeometry:
            return QgsGeometry().fromMultiPolyline(geom_list)
        else:
            return QgsGeometry().fromMultiPolygon(geom_list)
