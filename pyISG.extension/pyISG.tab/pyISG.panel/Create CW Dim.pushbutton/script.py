"""Create section parallel to the plane of selected walls or planar element."""
#pylint: disable=import-error,invalid-name,broad-except
from pyrevit import revit, DB
from pyrevit import script

# adapted from https://thebuildingcoder.typepad.com/blog/2012/06/create-section-view-parallel-to-wall.html
__author__ = 'Source: Jeremy Tammik\nAdapted by: {{author}}'

logger = script.get_logger()
output = script.get_output()


def create_section(wall, section_type):
    # ensure wall is straight
    line = wall.Location.Curve
    # determine section box
    p = line.GetEndPoint(0)
    q = line.GetEndPoint(1)
    v = q - p

    bb = wall.get_BoundingBox(None)
    minZ = bb.Min.Z
    maxZ = bb.Max.Z

    w = v.GetLength()
    # h = maxZ - minZ
    # d = wall.WallType.Width
    offset = 0.1 * w

    bbox_min = DB.XYZ(-w, minZ - offset, -offset)
    bbox_max = DB.XYZ(w, maxZ + offset, 0)

    midpoint = p + 0.5 * v
    walldir = v.Normalize()
    up = DB.XYZ.BasisZ
    viewdir = walldir.CrossProduct(up)

    t = DB.Transform.Identity
    t.Origin = midpoint
    t.BasisX = walldir
    t.BasisY = up
    t.BasisZ = viewdir

    section_box = DB.BoundingBoxXYZ()
    section_box.Transform = t
    section_box.Min = bbox_min
    section_box.Max = bbox_max

    return DB.ViewSection.CreateSection(revit.doc, section_type, section_box)


def get_walls():
    """retrieve wall from selection set"""
    return [x for x in revit.get_selection() if isinstance(x, DB.Wall)]

def isParallel(v1,v2):
  return v1.CrossProduct(v2).IsAlmostEqualTo(DB.XYZ(0,0,0))


def get_section_viewfamily():
    return revit.doc.GetDefaultElementTypeId(
        DB.ElementTypeGroup.ViewTypeSection
        )




doc_section_type = get_section_viewfamily()

with revit.Transaction("Create Parallel Section"):
    for selected_wall in get_walls():
        dimline = selected_wall.Location.Curve
        create_section(selected_wall, doc_section_type)


def createdim(wall, line, view):
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


    # TransactionManager.Instance.EnsureInTransaction(doc)
    revit.doc.Create.NewDimension(view, line, refArray)
    # TransactionManager.Instance.TransactionTaskDone()

    #Assign your output to the OUT variable.
    # OUT = 0