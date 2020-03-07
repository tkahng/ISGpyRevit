"""Create Table"""

from pyrevit import revit, DB
from rpw.ui.forms import Button, ComboBox, FlexForm, CheckBox, Label, TextBox, Separator
# import os
# from pyrevit import script

def mmToFoot(mm):
    inchToMm = 25.4
    footToMm = 12 * inchToMm
    return mm / footToMm

def applyViewScale(mm):
    return mmToFoot(mm) * revit.active_view.Scale
    
components = [
            Label('width'),
            TextBox('width', default='701.0'),
            Label('height'),
            TextBox('height', default='554.0'),
            Label('colCount'),
            TextBox('colCount', default='3'),
            Label('rowCount'),
            TextBox('rowCount', default='3'),
            Label('fieldColWidth'),
            TextBox('fieldColWidth', default='50.0'),
            Label('fieldRowCount'),
            TextBox('fieldRowCount', default='4'),
            Label('fieldRowHeight'),
            TextBox('fieldRowHeight', default='10.0'),
            Separator(),
            Button('Create foundation')]

ff = FlexForm("Set Table Dimensions", components)
ff.show()

width = applyViewScale(float(ff.values['width']))
height = applyViewScale(float(ff.values['height']))
colCount = int(ff.values['colCount'])
rowCount = int(ff.values['rowCount'])
rowHeight = height/rowCount
fieldColWidth = applyViewScale(float(ff.values['fieldColWidth']))
fieldRowCount = int(ff.values['fieldRowCount'])
fieldRowHeight = applyViewScale(float(ff.values['fieldRowHeight']))
colWidth = (width-fieldColWidth)/colCount

def frange(start, count, step=1.0):
    ''' "range()" like function which accept float type''' 
    i = start
    for c in range(count):
        yield i
        i += step

origin = DB.XYZ()
vline = DB.Line.CreateBound(DB.XYZ(origin.X, origin.Y, origin.Z), DB.XYZ(origin.X, origin.Y + height, origin.Z))
hline = DB.Line.CreateBound(DB.XYZ(origin.X, origin.Y, origin.Z), DB.XYZ(origin.X + width, origin.Y, origin.Z))

def direction(line):
    p = line.GetEndPoint(0)
    q = line.GetEndPoint(1)
    v = q-p
    vn = v.Normalize()
    return vn

def createHlines():
    cArray = DB.CurveArray()
    vn = direction(vline)
    xFormValues = []

    for i in list(frange(0, rowCount, rowHeight)):
        [xFormValues.append(j) for j in list(frange(i, fieldRowCount+1, fieldRowHeight))]
    
    for i in xFormValues:
        cArray.Append(hline.CreateTransformed(DB.Transform.CreateTranslation(vn*i)))

    revit.doc.Create.NewDetailCurveArray(revit.active_view, cArray) 


def createVlines():
    cArray = DB.CurveArray()
    vn = direction(hline)
    xFormValues = [0]
    
    [xFormValues.append(j) for j in list(frange(fieldColWidth, colCount+1, colWidth))]
    
    for i in xFormValues:
        cArray.Append(vline.CreateTransformed(DB.Transform.CreateTranslation(vn*i)))

    revit.doc.Create.NewDetailCurveArray(revit.active_view, cArray) 


if ff.values:
    # main()
    with revit.Transaction("Create Parallel Section"):
        createVlines()
        createHlines()