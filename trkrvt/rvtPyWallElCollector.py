# coding: utf8

from Autodesk.Revit import DB
# from pyrevit import revit, DB

doc = __revit__.ActiveUIDocument.Document
# doc = revit.doc.ActiveUIDocument.Document

# Creating collector instance and collecting all the walls from the model
# wc = DB.FilteredElementCollector(doc)\
#                     .OfCategory(DB.BuiltInCategory.OST_Walls)\
#                     .WhereElementIsNotElementType()\
#                     .ToElements()

wc = DB.FilteredElementCollector(revit.doc)\
                    .OfCategory(DB.BuiltInCategory.OST_Walls)\
                    .WhereElementIsNotElementType()\
                    .ToElements()

wc = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
wc = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Walls).WhereElementIsElementType().ToElements()

# col = [x for x in wall_collector]

# w1 = col[0]

cws = []
bws = []

# for w in wc:
#     if w.WallType.Kind.ToString() == 'Curtain':
#         cws.append(w)
#     else:
#         bws.append(w)

cws = [w for w in wc if w.WallType.Kind.ToString() == 'Curtain']

# Iterate over wall and collect Volume data
# total_volume = 0.0

# for wall in wall_collector:
#     vol_param = wall.Parameter[DB.BuiltInParameter.HOST_VOLUME_COMPUTED]
#     if vol_param:
#         total_volume = total_volume + vol_param.AsDouble()

# now that results are collected, print the total
# print("Total Volume is: {}".format(total_volume))