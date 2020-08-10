"""Create section parallel to the plane of selected walls or planar element."""
#pylint: disable=import-error,invalid-name,broad-except
from pyrevit import revit, DB
# from pyrevit import script

# adapted from https://thebuildingcoder.typepad.com/blog/2012/06/create-section-view-parallel-to-wall.html
__author__ = 'Source: Jeremy Tammik\nAdapted by: {{author}}'

# logger = script.get_logger()
# output = script.get_output()

def get_walls():
    """retrieve wall from selection set"""
    return [x for x in revit.get_selection() if isinstance(x, DB.Wall)]

def isParallel(v1,v2):
    return v1.CrossProduct(v2).IsAlmostEqualTo(DB.XYZ(0,0,0))

def cwrefs(cw):

    refArray = DB.ReferenceArray()
    faces = []
    options = DB.Options()
    options.ComputeReferences = True
    options.IncludeNonVisibleObjects = True

    geoElement = cw.get_Geometry(options)

    for obj in geoElement:
        if isinstance(obj,DB.Solid):
            for f in obj.Faces:
                faces.Append(f)
    return faces

def create_dim(wall, line, view):
    line = wall.Location.Curve
    lineDir = line.GetEndPoint(1) - line.GetEndPoint(0)

    refArray = DB.ReferenceArray()

    # doc = DocumentManager.Instance.CurrentDBDocument

    options = DB.Options()
    options.ComputeReferences = True
    options.IncludeNonVisibleObjects = True

    geoElement = wall.get_Geometry(options)

    #get side references
    for obj in geoElement:
        if isinstance(obj,DB.Solid):
            for f in obj.Faces:
                faceNormal = f.FaceNormal
                if isParallel(faceNormal,lineDir):
                    refArray.Append(f.Reference)
                    
    #get grid references
    for id in wall.CurtainGrid.GetVGridLineIds():
        gridLine = revit.doc.GetElement(id)
        gridGeo = gridLine.get_Geometry(options)
        for obj in gridGeo:
            if isinstance(obj,DB.Line):
                refArray.Append(obj.Reference)

    revit.doc.Create.NewDimension(view, line, refArray)


with revit.Transaction("Create Parallel Section"):
    for selected_wall in get_walls():
        dimline = selected_wall.Location.Curve
        create_dim(selected_wall, dimline, revit.active_view)