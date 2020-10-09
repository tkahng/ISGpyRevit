
import revitron
from revitron import _

from pyrevit import revit
from rpw import db, ui, DB, UI


cws = db.Collector(elements=ids.get_element_ids(),of_class='Wall', where=lambda x:x.get_family().name=='Curtain')

els = db.Collector(of_category='OST_Walls', level='1')