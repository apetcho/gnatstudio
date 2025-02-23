"""
In the thread view, the selection should change the current thread.
"""
import GPS
from gs_utils.internal.utils import *
import re

NUMBER_COLUMN = 0


@run_test_driver
def test_driver():
    mode = "Mode:" + GPS.Preference("GPS6-Debugger-Debugger-Kind").get()
    buf = GPS.EditorBuffer.get(GPS.File("main.adb"))
    buf.current_view().goto(buf.at(23, 1))
    GPS.execute_action("debug set line breakpoint")

    GPS.execute_action("Build & Debug Number 1")
    yield hook('debugger_started')
    yield wait_idle()

    debug = GPS.Debugger.get()
    yield wait_until_not_busy(debug)
    
    if mode == "Mode:Dap":
        debug.start()
        NAME_COLUMN = 1
    else:
        debug.send("run")
        NAME_COLUMN = 2

    GPS.execute_action("open threads debugger window")
    yield wait_for_mdi_child("Threads")
    yield wait_until_not_busy(debug)

    view = GPS.MDI.get("Threads")
    tree = get_widgets_by_type(Gtk.TreeView, view.pywidget())[0]
    model = tree.get_model()
    yield wait_idle()
    gps_assert(dump_tree_model(model, NUMBER_COLUMN),
               ["1", "2", "* 3"],
               "Wrong thread selected when stopping in " + mode)
    gps_assert(dump_tree_model(model, NAME_COLUMN),
               ["main", "foo", "bar"],
               "Wrong thread name when stopping in " + mode)

    click_in_tree(tree, "1")
    yield wait_idle()
    yield wait_until_not_busy(debug)
    gps_assert(dump_tree_model(model, NUMBER_COLUMN),
               ["1", "* 2", "3"],
               "Wrong thread selected when selecting in " + mode)
