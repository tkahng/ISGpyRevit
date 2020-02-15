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


def get_walls():
    """retrieve wall from selection set"""
    return [x for x in revit.get_selection() if isinstance(x, DB.Wall)]


def get_section_viewfamily():
    return revit.doc.GetDefaultElementTypeId(
        DB.ElementTypeGroup.ViewTypeSection
        )


doc_section_type = get_section_viewfamily()

with revit.Transaction("Create Parallel Section"):
    for selected_wall in get_walls():
        create_section(selected_wall, doc_section_type)
