import clr

#The inputs to this node will be stored as a list in the IN variables.
# select model element node for wall
wall = UnwrapElement(IN[0])
# select model element node for line
lineElement = UnwrapElement(IN[1])
# document.current and document.active.view node for view
view = UnwrapElement(IN[2])

clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import *

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Transactions import TransactionManager
from RevitServices.Persistence import DocumentManager

def isParallel(v1,v2):
	return v1.CrossProduct(v2).IsAlmostEqualTo(XYZ(0,0,0))

line = lineElement.GeometryCurve
lineDir = line.GetEndPoint(1) - line.GetEndPoint(0)

refArray = ReferenceArray()

doc = DocumentManager.Instance.CurrentDBDocument

options = Options()
options.ComputeReferences = True
options.IncludeNonVisibleObjects = True

geoElement = wall.get_Geometry(options)

#get side references
for obj in geoElement:
	if isinstance(obj,Solid):
		for f in obj.Faces:
			faceNormal = f.FaceNormal
			if isParallel(faceNormal,lineDir):
				refArray.Append(f.Reference)
				
				
#get grid references
for id in wall.CurtainGrid.GetVGridLineIds():
	gridLine = doc.GetElement(id)
	gridGeo = gridLine.get_Geometry(options)
	for obj in gridGeo:
		if isinstance(obj,Line):
			refArray.Append(obj.Reference)


TransactionManager.Instance.EnsureInTransaction(doc)

doc.Create.NewDimension(view, line, refArray)

TransactionManager.Instance.TransactionTaskDone()

#Assign your output to the OUT variable.
OUT = 0