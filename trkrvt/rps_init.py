# these commands get executed in the current scope
# of each new shell (but not for canned commands)
#pylint: disable=all
import clr
clr.AddReferenceByPartialName('PresentationCore')
clr.AddReferenceByPartialName("PresentationFramework")
clr.AddReferenceByPartialName('System')
clr.AddReferenceByPartialName('System.Windows.Forms')

# from Autodesk.Revit import DB
# from Autodesk.Revit import UI

from rpw import revit, db, ui, DB, UI

# creates variables for selected elements in global scope
# e1, e2, ...
max_elements = 5
gdict = globals()
uidoc = revit.uidoc
if uidoc:
    doc = revit.doc
    selection = [doc.GetElement(x) for x in uidoc.Selection.GetElementIds()]
    for idx, el in enumerate(selection):
        if idx < max_elements:
            gdict['e{}'.format(idx+1)] = el
        else:
            break

# alert function
def alert(msg):
    TaskDialog.Show('RPS', msg)

# quit function
def quit():
    __window__.Close()