"""Activates selection tool that picks a specific type of element.

Shift-Click:
Pick favorites from all available categories
"""
# pylint: disable=E0401,W0703,C0103
from collections import namedtuple
import revitron
from revitron import _
import sys
from pyrevit import revit, DB, UI
from pyrevit import forms
from pyrevit import script

# import this script's configurator
# import pick_config
logger = script.get_logger()
# selection = revitron.Selection.get()
# my_config = script.get_config()
# output = script.get_output()

# FREQUENTLY_SELECTED_CATEGORIES = [
#     DB.BuiltInCategory.OST_Areas,
#     DB.BuiltInCategory.OST_AreaTags,
#     DB.BuiltInCategory.OST_AreaSchemeLines,
#     DB.BuiltInCategory.OST_Columns,
#     DB.BuiltInCategory.OST_StructuralColumns,
#     DB.BuiltInCategory.OST_Dimensions,
#     DB.BuiltInCategory.OST_Doors,
#     DB.BuiltInCategory.OST_Floors,
#     DB.BuiltInCategory.OST_StructuralFraming,
#     DB.BuiltInCategory.OST_Furniture,
#     DB.BuiltInCategory.OST_Grids,
#     DB.BuiltInCategory.OST_Rooms,
#     DB.BuiltInCategory.OST_RoomTags,
#     DB.BuiltInCategory.OST_Truss,
#     DB.BuiltInCategory.OST_Walls,
#     DB.BuiltInCategory.OST_Windows,
#     DB.BuiltInCategory.OST_Ceilings,
#     DB.BuiltInCategory.OST_SectionBox,
#     DB.BuiltInCategory.OST_ElevationMarks,
#     DB.BuiltInCategory.OST_Parking
# ]

cat_names = [x.Name for x in list(set(revit.query.get_all_category_set()))]

# def load_configs():
#     """Load list of frequently selected categories from configs or defaults"""
#     # fscats = my_config.get_option('fscats', [])
#     revit_cats = [revit.query.get_category(x)
#                   for x in FREQUENTLY_SELECTED_CATEGORIES]
#     return filter(None, revit_cats)

# CategoryOption = namedtuple('CategoryOption', ['name', 'revit_cat'])

# source_categories = load_configs()

# ask user to select a category to select by

# if source_categories:
# category_opts = [CategoryOption(name=x.Name, revit_cat=x)
#                     for x in source_categories]

selected_category = \
    forms.CommandSwitchWindow.show(
        # sorted([x.name for x in category_opts]),
        sorted(cat_names),
        message='Pick only elements of type:'
    )

scopeids = revitron.Filter().noTypes().byCategory(selected_category).getElementIds()


parameters = revitron.ParameterNameList().get()


selected_param = \
    forms.CommandSwitchWindow.show(
        sorted(parameters),
        message='Pick only elements of type:'
    )

selected_value = \
    forms.ask_for_string(
        default='some-tag',
        prompt='Enter new tag name:',
        title='Tag Manager'
    )

    # if selected_category:


ids = revitron.Filter(scopeids).noTypes().byStringContains(selected_param, selected_value).getElementIds()

revitron.Selection.set(ids)