"""Create Table"""

from pyrevit import revit, DB
# from pyrevit import script

width = 701.0
height = 554.0
colCount = 3
rowCount = 3
rowHeight = height/3
fieldColWidth = 50.0
fieldRowCount = 4
fieldRowHeight = 10.0
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
    iValue = list(frange(0, fieldRowCount+1, fieldRowHeight))
    rValue = list(frange(rowHeight, rowCount, rowHeight))
    
    for i in iValue:
        line = hline.CreateTransformed(DB.Transform.CreateTranslation(vn*i))
        for j in rValue:
            t = DB.Transform.CreateTranslation(vn*j)
            rowline = line.CreateTransformed(DB.Transform.CreateTranslation(vn*j))
            cArray.Append(rowline)
    revit.doc.Create.NewDetailCurveArray(revit.active_view, cArray) 

# vlist = []

# for i in range(colCount):
#     vlist.append(colWidth)

def createVlines():
    cArray = DB.CurveArray()
    vn = direction(hline)
    c1 = vn*fieldColWidth
    c2 = vn*colWidth
    cArray.Append(vline)
    # revit.doc.Create.NewDetailCurve(revit.active_view, vline)
    for i in range(colCount+1):
        t = DB.Transform.CreateTranslation(c1 + c2 *i)
        line = vline.CreateTransformed(t)
        cArray.Append(line)
    revit.doc.Create.NewDetailCurveArray(revit.active_view, cArray) 

with revit.Transaction("Create Parallel Section"):
    createVlines()
    createHlines()