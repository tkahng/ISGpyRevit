"""Activates selection tool that picks a specific type of element.

Shift-Click:
Pick favorites from all available categories
"""
# pylint: disable=E0401,W0703,C0103
# from collections import namedtuple
import revitron
from revitron import _
import sys
from pyrevit import revit, DB, UI
from pyrevit import forms
from pyrevit import script
from rpw import db, ui

cat_names = [x.Name for x in list(set(revit.query.get_all_category_set()))]


selected_category = \
    forms.CommandSwitchWindow.show(
        sorted(cat_names),
        message='Pick only elements of type:'
    )

# scope = revitron.Filter().noTypes().byCategory(selected_category).getElements()
scope = db.Collector(of_category=selected_category, is_type=False).get_elements()

parameters = revitron.ParameterNameList().get()

selected_param = \
    forms.CommandSwitchWindow.show(
        sorted(parameters),
        message='Pick only elements of type:'
    )

# vals = list(set(map(lambda x: revitron.Parameter(x, selected_param).getValueString(), scope)))
vals = list(set(map(lambda x: x.parameters[selected_param].value_string, scope)))
vals.append('*other')


selected_value = \
    forms.CommandSwitchWindow.show(
        sorted(vals),
        message='Pick only elements of type:'
    )

if selected_value == '*other':

    selected_value = \
        forms.ask_for_string(
            default='some-tag',
            prompt='Enter new tag name:',
            title='Tag Manager'
        )

# ids = revitron.Filter(list(scope)).noTypes().byStringContains(selected_param, selected_value).getElementIds()
col = db.Collector(scope, of_category=selected_category, where=lambda x: selected_value in x.parameters[selected_param].value_string)

revitron.Selection.set(ids)