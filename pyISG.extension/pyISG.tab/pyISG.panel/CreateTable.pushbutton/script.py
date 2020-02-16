"""Create Table"""

from pyrevit import revit, DB
# from pyrevit import script

def mmToFoot(mm):
    inchToMm = 25.4
    footToMm = 12 * inchToMm
    return mm / footToMm

def applyViewScale(mm):
    return mmToFoot(mm) * revit.active_view.Scale
    

width = applyViewScale(701.0)
height = applyViewScale(554.0)
colCount = 3
rowCount = 3
rowHeight = height/rowCount
fieldColWidth = applyViewScale(50.0)
fieldRowCount = 4
fieldRowHeight = applyViewScale(10.0)
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

# def createHlines():
#     cArray = DB.CurveArray()
#     vn = direction(vline)
#     fValue = list(frange(0, fieldRowCount+1, fieldRowHeight))
#     rValue = list(frange(0, rowCount, rowHeight))
#     for i in fValue:
#         line = hline.CreateTransformed(DB.Transform.CreateTranslation(vn*i))
#         for j in rValue:
#             rowline = line.CreateTransformed(DB.Transform.CreateTranslation(vn*j))
#             cArray.Append(rowline)
#     revit.doc.Create.NewDetailCurveArray(revit.active_view, cArray) 


# def createVlines():
#     cArray = DB.CurveArray()
#     vn = direction(hline)
#     c1 = vn*fieldColWidth
#     c2 = vn*colWidth
#     cArray.Append(vline)
#     # revit.doc.Create.NewDetailCurve(revit.active_view, vline)
#     for i in range(colCount+1):
#         t = DB.Transform.CreateTranslation(c1 + c2 *i)
#         line = vline.CreateTransformed(t)
#         cArray.Append(line)
#     revit.doc.Create.NewDetailCurveArray(revit.active_view, cArray) 

with revit.Transaction("Create Parallel Section"):
    createVlines()
    createHlines()