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
    curve = wall.Location.Curve
    # determine section box
    curve_transform = curve.ComputeDerivatives(0.5, True)

    origin = curve_transform.Origin
    wall_direction = curve_transform.BasisX.Normalize()  # type: XYZ
    up = DB.XYZ.BasisZ
    section_direction = wall_direction.CrossProduct(up)
    right = up.CrossProduct(section_direction)

    transform = DB.Transform.Identity
    transform.Origin = origin
    transform.BasisX = wall_direction
    transform.BasisY = up
    transform.BasisZ = section_direction

    section_box = DB.BoundingBoxXYZ()
    section_box.Transform = transform

    # Try to retrieve element height, width and lenght
    try:
        el_depth =  wall.WallType.Width
    except AttributeError:
        el_depth = 2

    el_width = curve.Length

    el_bounding_box = wall.get_BoundingBox(None)
    z_min = el_bounding_box.Min.Z
    z_max = el_bounding_box.Max.Z
    el_height = z_max - z_min

    depth_offset = 1
    height_offset = 1   
    width_offset = 1

    # Get Wall Offset Params
    base_offset = wall.Parameter[DB.BuiltInParameter.WALL_BASE_OFFSET].AsDouble()


    # Set BoundingBoxXYZ's boundaries
    section_box.Min = DB.XYZ(-el_width / 2 - width_offset,
                          -height_offset + base_offset,
                          -el_depth / 2 - depth_offset)
    section_box.Max = DB.XYZ(el_width / 2 + width_offset,
                          el_height + height_offset + base_offset,
                          el_depth / 2 + depth_offset)

    return DB.ViewSection.CreateSection(revit.doc, section_type, section_box)


# def get_walls():
#     """retrieve wall from selection set"""
#     return [x for x in revit.get_selection() if isinstance(x, DB.Wall)]

def get_cw():
    wc = DB.FilteredElementCollector(revit.doc)\
                    .OfCategory(DB.BuiltInCategory.OST_Walls)\
                    .WhereElementIsNotElementType()\
                    .ToElements()
    return [w for w in wc if w.WallType.Kind.ToString() == 'Curtain']

def isParallel(v1,v2):
  return v1.CrossProduct(v2).IsAlmostEqualTo(DB.XYZ(0,0,0))    

def get_section_viewfamily():
    return revit.doc.GetDefaultElementTypeId(
        DB.ElementTypeGroup.ViewTypeSection
        )

def create_dim(wall, line, view):
    t = DB.Transform.CreateTranslation(DB.XYZ(0,0,-1))
    line = wall.Location.Curve.CreateTransformed(t)
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

doc_section_type = get_section_viewfamily()

with revit.Transaction("Create Parallel Section"):
    for selected_wall in get_cw():
        dimline = selected_wall.Location.Curve
        sec = create_section(selected_wall, doc_section_type)
        create_dim(selected_wall, dimline, sec)