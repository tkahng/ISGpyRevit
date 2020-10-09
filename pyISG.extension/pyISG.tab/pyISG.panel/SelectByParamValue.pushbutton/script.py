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

# import this script's configurator
# import pick_config
# logger = script.get_logger()
# selection = revitron.Selection.get()
# my_config = script.get_config()
# output = script.get_output()
# cat_names = [x.Name for x in FREQUENTLY_SELECTED_CATEGORIES]



cat_names = [x.Name for x in list(set(revit.query.get_all_category_set()))]
# logger.debug(cat_names)

selected_category = \
    forms.CommandSwitchWindow.show(
        # sorted([x.name for x in category_opts]),
        sorted(cat_names),
        message='Pick only elements of type:'
    )

# scope = revitron.Filter().noTypes().byCategory(selected_category).getElementIds()
scope = revitron.Filter().noTypes().byCategory(selected_category).getElements()
# scopeids = map(lambda x: x.Id, cat_els)
logger.debug(scope)

parameters = revitron.ParameterNameList().get()

selected_param = \
    forms.CommandSwitchWindow.show(
        sorted(parameters),
        message='Pick only elements of type:'
    )

# map(lambda x: revitron.Parameter(x, selected_param).getValueString(), scopeids)
# vals = list(set(map(lambda x: _(x).get(selected_param), scopeids)))
vals = list(set(map(lambda x: revitron.Parameter(x, selected_param).getValueString(), scope)))

vals.append('*other')
logger.debug(vals)

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

    # if selected_category:

logger.debug(scope)

ids = revitron.Filter(list(scope)).noTypes().byStringContains(selected_param, selected_value).getElementIds()

revitron.Selection.set(ids)