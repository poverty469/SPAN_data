import processing
import json
import os

# Created by Jackson Baker Ryan
# May 09, 2019

# Processes the currently active layer (highlighted layer in the layers panel)
# and saves a JSON file that contains a list of the data IDs and a dictionary
# of fields, each with summary statistics, the field data (ordered to correspond with
# the data ID order), and a field alias.
#
# Preconditions to use: (NO WARNINGS ARE GIVEN IF FAILED TO FOLLOW THESE)
#    - Curation of fields must already be done
#    - Fields have been given web ready alias names
#    - Title of the layer is descriptive and includes the geography
#        e.g. percentBelowPovertyLevel_Counties
#    - Id field name must be changed to universal name
#       - Id field name must be universal to all other exports
#
# Output:
#     Saves the JSON to the the user's Download folder within their HOME path
#     with a file name of the layer's name appended with "_summary".
#
#     Format Example:
#        {
#            "ids": [1,2,3],
#            "field_1": {
#                "name": "Field One's Alias",
#                "stats": {
#                    "MEAN": 5,
#                    "MEDIAN": 5,
#                    ...
#                },
#                "data": [0,5,10]
#            },
#            "field_2": { ... }
#        }

ID_FIELD_NAME = "id"

USER_HOME = os.environ['HOME']  # Path to the user's home
SAVE_FILE_PATH = USER_HOME + "/Downloads/"  # Path to save the files to


# Statistics to NOT be included in the summary
UNWANTED_STAT_FIELDS = [
    "UNIQUE",
    "MINORITY",
    "MAJORITY",
    "EMPTY",
    "FILLED",
    "OUTPUT_HTML_FILE"
]

# Returns the summary statistics of the given layer.
# Includes:
#        count, sum, mean, median, standard deviation, coefficient of variance,
#        min, max, range, first quartile, third quartile, interquartile range


def getFieldStats(layer, layerPath, fieldName):
    stats = processing.run("qgis:basicstatisticsforfields", {
        'FIELD_NAME': fieldName,
        'INPUT_LAYER': layerPath,
        'OUTPUT_HTML_FILE': SAVE_FILE_PATH + 'QGIS_SummarizeLayerToJSON_tempfile.html'
    })

    # Remove unwanted fields from the calculated statistics
    for unwantedField in UNWANTED_STAT_FIELDS:
        if hasattr(stats, unwantedField):
            del stats[unwantedField]

    return stats

# Returns a list of the data of the provided field


def getFieldData(layer, fieldName):
    features = layer.getFeatures()
    data = []

    for feature in features:
        dataPiece = feature.attribute(fieldName)
        if (dataPiece == NULL):
            dataPiece = None

        data.append(dataPiece)

    return data

# Returns a list of upper values from class break methods results
#       data = Data to be classified
#       numberOfClasses = number of classes


def getClassBreaks(data, numberOfClasses):
    symbol = qgis.core.QgsLineSymbol()
    colorRamp = qgis.core.QgsGradientColorRamp()

    classBreakModeObjects = {
        "quantile": qgis.core.QgsGraduatedSymbolRenderer.Quantile,
        "equalInterval": qgis.core.QgsGraduatedSymbolRenderer.EqualInterval,
        "jenks": qgis.core.QgsGraduatedSymbolRenderer.Jenks
    }
    classBreakModeNames = list(classBreakModeObjects.keys())

    classBreaks = {}

    for breakModeName in classBreakModeNames:
        mode = classBreakModeObjects[breakModeName]
        renderer = qgis.core.QgsGraduatedSymbolRenderer.createRenderer(
            layer, fieldName, numberOfClasses, mode, symbol, colorRamp)
        ranges = renderer.ranges()

        upperValues = []
        for range in ranges:
            upperValues.append(range.upperValue())

        classBreaks[breakModeName] = upperValues

    return classBreaks


layer = iface.activeLayer()  # Currently active layer (highlighted in layers panel)
layerPath = layer.dataProvider().dataSourceUri()  # Path to layer source file
fields = layer.fields()  # Fields of the active layer

layerSummary = {}  # Summary of layer to be exported

for field in fields:
    fieldName = field.name()
    fieldSummary = {}

    if (ID_FIELD_NAME in fieldName):
        layerSummary[fieldName + "s"] = getFieldData(layer, fieldName)
    elif ("display" in fieldName):
        layerSummary["labels"] = getFieldData(layer, fieldName)
    else:
        fieldSummary = {}
        fieldSummary["title"] = field.alias()
        fieldSummary["stats"] = getFieldStats(layer, layerPath, fieldName)

        data = getFieldData(layer, fieldName)
        fieldSummary["classBreaks"] = getClassBreaks(data, 5)
        fieldSummary["data"] = data

        layerSummary[fieldName] = fieldSummary

with open(SAVE_FILE_PATH + layer.sourceName() + '_summary.json', 'w+') as outfile:
    json.dump(layerSummary, outfile)
