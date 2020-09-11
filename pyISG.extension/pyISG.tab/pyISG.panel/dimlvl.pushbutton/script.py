# # coding: utf8

# # from rpw import revit, db, ui, DB, UI

# from Autodesk.Revit.DB import Reference, ReferenceArray, XYZ, Line, Options, FamilyInstance, Point, \
#     FamilyInstanceReferenceType, Edge, Level, Grid
# from Autodesk.Revit import Exceptions
# from Autodesk.Revit.UI.Selection import ObjectType, ISelectionFilter

# from pyrevit import script, forms

# import rpw
# from rpw import revit

# doc = revit.doc
# uidoc = revit.uidoc
# logger = script.get_logger()


# selection = [doc.GetElement(id) for id in uidoc.Selection.GetElementIds()]


# # crv = el.GetCurvesInView(DB.DatumExtentType.ViewSpecific, doc.ActiveView)

# class CustomFilter(ISelectionFilter):
#     def AllowElement(self, elem):
#         return True

#     def AllowReference(self, reference, position):
#         return True


# class CurveLineFilter(ISelectionFilter):
#     def AllowElement(self, elem):
#         try:
#             if isinstance(elem.Location.Curve, Line):
#                 return True
#             else:
#                 return False
#         except AttributeError:
#             return False

#     def AllowReference(self, reference, position):
#         try:
#             if isinstance(doc.GetElement(reference).Location.Curve, Line):
#                 return True
#             else:
#                 return False
#         except AttributeError:
#             return False

# if not selection:
#     try:
#         selection = [doc.GetElement(reference) for reference in uidoc.Selection.PickObjects(
#             ObjectType.Element, CustomFilter(), "Pick")]
#     except Exceptions.OperationCanceledException:
#         import sys
#         sys.exit()




from Autodesk.Revit.DB import DatumExtentType, FilteredElementCollector, BuiltInCategory, Line, Reference, ReferenceArray, Options, XYZ

import rpw
from rpw import revit

doc = revit.doc
uidoc = revit.uidoc

selection = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType()

# All reference in reference will be dimensioned
reference_array = ReferenceArray()

options = Options(ComputeReferences=True, IncludeNonVisibleObjects=True)

for element in selection:
    reference_array.Append(Reference(element))

crvs = []

ends = []

for element in selection:
    crvs.extend(element.GetCurvesInView(DatumExtentType.ViewSpecific, doc.ActiveView))

for crv in crvs:
    ends.append(crv.GetEndPoint(0))

line = Line.CreateBound(ends[0], ends[-1])

with rpw.db.Transaction("QuickDimensionPipe"):
    # logger.debug([reference for reference in reference_array])
    dim = doc.Create.NewDimension(doc.ActiveView, line, reference_array)