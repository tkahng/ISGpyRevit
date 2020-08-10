# from gtalarico AU17
import clr
# Import RevitAPI Classes
clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import *
# As explained in the previous section, replace * with the class you need separatedby comma.
clr.AddReference("RevitNodes")
import Revit
# Adds ToDSType (bool) extension method to Wrapped elements
clr.ImportExtensions(Revit.Elements)
# Adds ToProtoType, ToRevitType geometry conversion extension methods to objects
clr.ImportExtensions(Revit.GeometryConversion)
# Import DocumentManager and TransactionManager
clr.AddReference("RevitServices")
from RevitServices.Transactions import TransactionManager
from RevitServices.Persistence import DocumentManager
# Create variable for Revit Document
doc = DocumentManager.Instance.CurrentDBDocument
# Start Transaction
TransactionManager.Instance.EnsureInTransaction(doc)
# Code that modifies Revit Database goes Here
# End Transaction
TransactionManager.Instance.TransactionTaskDone()
OUT = None