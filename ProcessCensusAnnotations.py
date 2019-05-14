# Created by Jackson Baker Ryan
# May 09, 2019

# Processes the currently active layer of Census provided data and
# creates field aliases from the annotations and converts data field types to a
# numeric type.
# These field aliases are useful for exporting the data and including a brief
# description.
# Preconditions:
#     - Must be Census data formatted
#     - Data must include annotations (single-line explanations of what each field is)
#     - First row of data must have been imported as the field name (automatic usually)
#     - One row must be the annotations
#     - Empty columns (with values of '(X)') must have been removed

layer = iface.activeLayer()


def processDataAliases():
    features = layer.getFeatures()

    for feature in features:
        if (feature.attribute(0) == "Id"):
            aliases = feature.attributes()

            for index, alias in enumerate(aliases):
                layer.setFieldAlias(index, alias.replace("GEO.", ""))

            layer.deleteFeature(feature.id())
            break

# Applies the correct field type to imported census data


def updateFields():
    layerAddedError = False

    fields = layer.fields()

    for currentFieldIndex, field in enumerate(fields):
        values = []
        # Save field data in 'values'
        for feature in layer.getFeatures():
            values.append(feature.attribute(0))

        # Delete field from layer
        layer.deleteAttribute(0)
        # for every field that doesn't include "id" or "display"
        if ("id" not in field.name() and "display" not in field.name()):
            # Set field type to real or integer depending on example value
            field.setType(QVariant.Double)
        else:
            # Set field type to string
            field.setType(QVariant.String)

        # Add updated field back to layer
        fieldAdded = layer.addAttribute(field)

        if (not layerAddedError and not fieldAdded):
            layerAddedError = True

        # add values to field in layer
        for featureIndex, feature in enumerate(layer.getFeatures()):
            layer.changeAttributeValue(
                feature.id(), fields.size() - 1, values[featureIndex])

    return layerAddedError


layer.startEditing()

# Rename id fields by removing "GEO." if it exists
fields = layer.fields()
for index, field in enumerate(fields):
    if ("GEO." in field.name()):
        layer.renameAttribute(index, field.name().replace("GEO.", ""))

processDataAliases()

error = updateFields()

if (error):
    print("AN ERROR OCCURRED, A 'LAYER' WAS LOST")
else:
    print("Review and save the edits in the layer's attribute table")
