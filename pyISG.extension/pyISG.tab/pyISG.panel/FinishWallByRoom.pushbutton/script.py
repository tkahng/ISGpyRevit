# -*- coding: utf-8 -*-
__title__ = 'Create Finish Walls\nBy Room'
__author__ = 'htl'
import sys
import clr
clr.AddReference('RevitAPI')

import rpw
from rpw import doc, uidoc
from rpw.ui.forms import ComboBox, Button, Label, FlexForm, TextBox, CheckBox
import Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import Selection
from itertools import izip
import System


class CategoriesFilter(Selection.ISelectionFilter):
    def __init__(self, names):
        self.names = names
    def AllowElement(self, element):
        return element.Category.Name in self.names


def select_objects_by_category(*names):
    prompt = 'Pick {}'.format(', '.join(names))
    references = uidoc.Selection.PickObjects(Selection.ObjectType.Element,
                                           CategoriesFilter(names), prompt)
    return (rpw.db.Element.from_id(reference.ElementId) for reference in references)


def select_object_by_category(name):
    prompt = 'Pick {}'.format(name)
    reference = uidoc.Selection.PickObject(Selection.ObjectType.Element,
                                           CategoriesFilter(name), prompt)
    return rpw.db.Element.from_id(reference.ElementId)


def get_boundaries(room):
    opt = SpatialElementBoundaryOptions()
    opt.SpatialElementBoundaryLocation = SpatialElementBoundaryLocation.Finish
    opt.StoreFreeBoundaryFaces = False
    return room.GetBoundarySegments(opt)


def curveloop_from_boundary(boundary):
    curveloop = CurveLoop()
    for segment in boundary:
        curveloop.Append(segment.GetCurve())
    return curveloop


def form():
    floor_types = rpw.db.Collector(of_category='OST_Floors', is_type=True).get_elements()
    wall_types = rpw.db.Collector(of_category='Walls', is_type=True,
                                  where=lambda x: x.GetParameters('Width')).get_elements()
    components = [
                    Label('Finish floor type:'),
                    ComboBox('floor_type_id',
                            {ft.parameters['Type Name'].AsString(): ft.Id for ft in floor_types}),
                    # Label('No Floors'),
                    CheckBox('make_floors', 'make Floors'),
                    Label('Finish wall type:'),
                    ComboBox('wall_type_id',
                            {wt.parameters['Type Name'].AsString(): wt.Id for wt in wall_types}),
                    Label('Finish wall height (mm):'),
                    TextBox('wall_height', default='3000'),
                    Button('Create Finish Walls')
                  ]

    ff = FlexForm('Create Finish Walls', components)
    ff.show()
    if ff.values['wall_type_id'] and ff.values['wall_height']:
        try:
            floor_type = rpw.db.Element.from_id(ff.values['floor_type_id'])
            wall_type = rpw.db.Element.from_id(ff.values['wall_type_id'])
            wall_height = float(ff.values['wall_height'])
            make_floors = ff.values['make_floors']
            return wall_type, wall_height, floor_type, make_floors
        except:
            return

def is_inside_room(curveloop, room):
    for curve in curveloop:
        end0 = curve.GetEndPoint(0)
        end1 = curve.GetEndPoint(1)
        if room.IsPointInRoom(end0) and room.IsPointInRoom(end1):
            continue
        else:
            return False
    return True


@rpw.db.Transaction.ensure('Make Floor')
def make_floor(floor_type, boundary, level_id):
    floor_curves = CurveArray()
    for boundary_segment in boundary:
        try:
            floor_curves.Append(boundary_segment.Curve)       # 2015, dep 2016
        except AttributeError:
            floor_curves.Append(boundary_segment.GetCurve())  # 2017

    floorType = doc.GetElement(floor_type)
    offset = rpw.db.Element(floorType).parameters['Default Thickness'].AsDouble()
    level = doc.GetElement(level_id)
    normal_plane = XYZ.BasisZ
    floor = doc.Create.NewFloor(floor_curves, floorType, level, False, normal_plane)
    rpw.db.Element(floor).parameters['Height Offset From Level'] = offset
    return floor

# @rpw.db.Transaction.ensure('create finish walls')
def create_finish_wall(room, wall_type, wall_height, floor_type, make_floors):
    offset_distance = wall_type.parameters['Width'].AsDouble() * 0.5
    boundary_loops = get_boundaries(room)
    if make_floors:
        new_floor = make_floor(floor_type.Id, boundary_loops[0], room.LevelId)
    # print(boundary_loops)
    for boundary in boundary_loops:
        curveloop = curveloop_from_boundary(boundary)

        offset_curveloop = CurveLoop.CreateViaOffset(curveloop, offset_distance,
                                                     curveloop.GetPlane().Normal)
        if not is_inside_room(offset_curveloop, room):
            offset_curveloop = CurveLoop.CreateViaOffset(curveloop, -offset_distance,
                                                         curveloop.GetPlane().Normal)
        new_walls = []
        # new_floors = make_floor(floor_type.Id, curveloop, room.LevelId)
        # with rpw.db.TransactionGroup('run def'):

        with rpw.db.Transaction('Create Finish Wall'):
            for curve in offset_curveloop:
                new_wall = Wall.Create(doc, curve, wall_type.Id, room.LevelId,
                                    wall_height/304.8, 0, False, False)
                rpw.db.Wall(new_wall).parameters['Room Bounding'] = False
                # print new_wall.LookupParameter('Room Bounding').AsString()
                # new_wall.parameters['Room Bounding'] = False
                new_walls.append(new_wall)

        with rpw.db.Transaction('Join old-new walls'):
            for idx, new_wall in enumerate(new_walls):
                old_wall = doc.GetElement(boundary[idx].ElementId)
                if old_wall:
                    try:
                        JoinGeometryUtils.JoinGeometry(doc, old_wall, new_wall)
                    except Exception as e:
                        print(e)

        with rpw.db.Transaction('Join floor-new walls'):
            for idx, new_wall in enumerate(new_walls):
                if make_floors:
                    try:
                        JoinGeometryUtils.JoinGeometry(doc, new_floor, new_wall)
                    except Exception as e:
                        print(e)

        with rpw.db.Transaction('Delete short walls'):
            for new_wall in new_walls:
                length = new_wall.LookupParameter('Length').AsDouble() * 304.8
                if length < 50:
                    doc.Delete(new_wall.Id)

def main():
    with rpw.db.TransactionGroup('run def'):
        try:
            wall_type, wall_height, floor_type, make_floors = form()
            rooms = select_objects_by_category('Rooms')
            for room in rooms:
                create_finish_wall(room, wall_type, wall_height, floor_type, make_floors)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
