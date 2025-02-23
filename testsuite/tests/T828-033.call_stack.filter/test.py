"""
Test the filter in the Call Stack view.
"""

import platform
import GPS
from gs_utils.internal.utils import *


@run_test_driver
def test_driver():
    GPS.execute_action("Build & Debug Number 1")
    yield hook('debugger_started')
    d = GPS.Debugger.get()
    for s in ["b hidden.adb:8",
              "run"]:
        yield wait_until_not_busy(d)
        d.send(s)

    yield wait_until_not_busy(d)

    win = GPS.MDI.get("Call Stack").pywidget()
    tree = get_widgets_by_type(Gtk.TreeView, win)[0]
    selection = tree.get_selection()

    host_name = GPS.Process("hostnamectl").get_result()
    is_red_hat = "Red Hat" in host_name
    is_ubuntu_22 = "Ubuntu 22" in host_name

    # The call stack could different depending on the OS
    if platform.system().lower() == 'windows':
        gps_assert(dump_tree_model(tree.get_model(), 0),
               ['0', '1', '2'],
               "Incorrect Callstack tree (Windows)")
    else:
        if is_red_hat or is_ubuntu_22:
            gps_assert(dump_tree_model(tree.get_model(), 0),
                       ['0', '1', '2', '3', '4', '5', '6'],
                       "Incorrect Callstack tree (RHES or Ubuntu 22)")
        else:
            gps_assert(dump_tree_model(tree.get_model(), 0),
                       ['0', '1', '2', '3', '4', '5'],
                       "Incorrect Callstack tree (Ubuntu 20)")

    # Filter the Call Stack
    get_widget_by_name("Call Stack Filter").set_text("main")
    yield timeout(500)
    if platform.system().lower() == 'windows':
        gps_assert(dump_tree_model(tree.get_model(), 0),
                   ['2'],
                   "Incorrect Callstack tree when filtered")
    else:
        if is_red_hat or is_ubuntu_22:
            gps_assert(dump_tree_model(tree.get_model(), 0),
                   ['2', '3', '4', '5'],
                   "Incorrect Callstack tree when filtered (RHES or Ubuntu 22)")
        else:
            gps_assert(dump_tree_model(tree.get_model(), 0),
                   ['2', '3', '4'],
                   "Incorrect Callstack tree when filtered (Ubuntu 20)")

    # Frame 0 is filtered out => it should select nothing
    d.send("frame 0")
    yield wait_until_not_busy(d)
    gps_assert(selection.get_selected()[1],
               None,
               "This frame is hidden and can't be selected")

    if platform.system().lower() == 'windows':
        # Frame 1 is visible => it should select it
        d.send("frame 2")
        yield wait_until_not_busy(d)
        model, iter = selection.get_selected()
        gps_assert(model.get_value(iter, 0),
                   "2",
                   "This frame is visible and should be selected")
    else:
        # Frame 2 is visible => it should select it
        d.send("frame 2")
        yield wait_until_not_busy(d)
        model, iter = selection.get_selected()
        gps_assert(model.get_value(iter, 0),
                   "2",
                   "This frame is visible and should be selected")

    d.send('q')

    yield wait_tasks()
