#Author- George Roberts
#Description-Create a component containing the oriented bounding box of the root component

import adsk.core, adsk.fusion, adsk.cam, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        doc = app.activeDocument
        prods = doc.products
        des = adsk.fusion.Design.cast(prods.itemByProductType("DesignProductType"))

        ## Get the root component and get it's minimum bounding box
        rootComp = des.rootComponent
        bound = rootComp.orientedMinimumBoundingBox
        ## get the details of the bounding box
        centre = bound.centerPoint
        height = bound.height
        up = bound.heightDirection
        length = bound.length
        left = bound.lengthDirection
        ## calculate the right vector
        right = left.crossProduct(up)
        width = bound.width
        rotationMatrix = adsk.core.Matrix3D.create()
        
        ## add a new component
        allOccs = rootComp.occurrences
        newOcc = allOccs.addNewComponent(rotationMatrix)
        newComp = adsk.fusion.Component.cast(newOcc.component)
        ## calculate the rotation matrix for the points
        rotationMatrix.setToAlignCoordinateSystems(adsk.core.Point3D.create(0,0,0), 
                                                   adsk.core.Vector3D.create(1,0,0), 
                                                   adsk.core.Vector3D.create(0,1,0), 
                                                   adsk.core.Vector3D.create(0,0,1), 
                                                   centre, 
                                                   left, 
                                                   right, 
                                                   up)
    
        ## create a new sketch
        sketches = newComp.sketches
        xyPlane = newComp.xYConstructionPlane
        sketch = sketches.add(xyPlane)

        ## set the points of the rectangle
        sketchLines = sketch.sketchCurves.sketchLines
        point0 = adsk.core.Point3D.create(-length/2, width/2, 0)
        point1 = adsk.core.Point3D.create(length/2, width/2, 0)
        point2 = adsk.core.Point3D.create(length/2, -width/2, 0)
        point3 = adsk.core.Point3D.create(-length/2, -width/2, 0)
        ## transform the points to be correctly orientated
        point0.transformBy(rotationMatrix)
        point1.transformBy(rotationMatrix)
        point2.transformBy(rotationMatrix)
        point3.transformBy(rotationMatrix)
        ## draw the box
        sketchLines.addByTwoPoints(point0, point1)
        sketchLines.addByTwoPoints(point1, point2)
        sketchLines.addByTwoPoints(point2, point3)
        sketchLines.addByTwoPoints(point3, point0)
        prof = sketch.profiles.item(0)
        extrudes = newComp.features.extrudeFeatures
        extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        # Create a symetric extrude for the box
        distance = adsk.core.ValueInput.createByReal(height / 2)
        extInput.setSymmetricExtent(distance, False)
        extrudes.add(extInput)

        ## name it and make it look good
        newComp.name = "Bounding box"
        yellow = adsk.core.Color.create(255,255,0,128)
        appearances = des.appearances
        if appearances.itemByName("StockColor"):
            yellowAppearance = appearances.itemByName("StockColor")
            newComp.bRepBodies.item(0).appearance = yellowAppearance
            newComp.opacity = 0.5
            return
        
        defaultAppearance = appearances.item(0)
        yellowAppearance = appearances.addByCopy(defaultAppearance, "StockColor")
        appearanceProps = yellowAppearance.appearanceProperties
        colorProperty = adsk.core.ColorProperty.cast(appearanceProps.itemByName('Color'))
        if colorProperty:
            colorProperty.value = yellow
        newComp.bRepBodies.item(0).appearance = yellowAppearance
        newComp.opacity = 0.5

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
