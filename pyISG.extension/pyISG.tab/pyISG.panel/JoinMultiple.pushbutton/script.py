# -*- coding: utf-8 -*-
__title__ = 'Unjoin many'

__doc__ = """Unjoins all selected geometry. (undo Join command)
Useful to get rid of warnings "Highlighted Elements are Joined but do not Intersect"
 Context: Some elements should be selected

Разъединяет все выбранные элементы. (отменяет команду Соединить)
Полезно в случаях, когда нужно избавиться от предупреждения "Элементы соединены, но не пересекаются"
Контекст: Должно быть выбрано несколько элементов"""

__helpurl__ = "https://apex-project.github.io/pyApex/help#unjoin-many"

__context__ = 'Selection'

try:
    from pyrevit.versionmgr import PYREVIT_VERSION
except:
    from pyrevit import versionmgr
    PYREVIT_VERSION = versionmgr.get_pyrevit_version()

pyRevitNewer44 = PYREVIT_VERSION.major >=4 and PYREVIT_VERSION.minor >=5

if pyRevitNewer44:
    from pyrevit.revit import doc, selection
    selection = selection.get_selection()
else:
    from revitutils import doc, selection

selected_ids = selection.element_ids

from Autodesk.Revit.DB import BuiltInCategory, ElementId, JoinGeometryUtils, Transaction
from Autodesk.Revit.UI import TaskDialog

def overlap1D(a1, a2, b1, b2):
  if a2>=b1 and b2>=a1:
    return True
  return False
  
def bbIntersect(bbA, bbB):
  return overlap1D(bbA.Min.X,bbA.Max.X,bbB.Min.X,bbB.Max.X) and overlap1D(bbA.Min.Y,bbA.Max.Y,bbB.Min.Y,bbB.Max.Y) and overlap1D(bbA.Min.Z,bbA.Max.Z,bbB.Min.Z,bbB.Max.Z)

output = []

for a in listA:
  bbA = a.get_BoundingBox(None)
  if not bbA is None:
    for b in listB:
      bbB = b.get_BoundingBox(None)
      if not bbB is None:
        if bbIntersect(bbA,bbB):
          output.append([a,b])


c = 0

if len(selected_ids) > 0:
    t = Transaction(doc)
    t.Start(__title__)
    for x in selected_ids:
        for y in selected_ids:
            try:
                JoinGeometryUtils.JoinGeometry(doc,doc.GetElement(x),doc.GetElement(y))
                c+=1
            except:
                pass
    t.Commit()

TaskDialog.Show(__title__,"%d pairs of elements unjoined" % c)
