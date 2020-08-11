import rpw
import pyrevit
from rpw import doc, uidoc
from System.Collections.Generic import List



# walls = rpw.db.Collector(of_class='Wall', where=lambda x: x.parameters['ROOMFIN'] == "wall")
walls = rpw.db.Collector(is_not_type=True)

wallids = List[rpw.DB.ElementId](walls.get_element_ids())
print len(wallids)