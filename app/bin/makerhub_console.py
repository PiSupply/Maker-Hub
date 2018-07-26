#!/usr/bin/python3
import threading
import logging
import queue
import urwid
import requests
from os import system
from makerhub import installer
from makerhub.installer import get_software_objects, install_package, uninstall_package, DESTINATION_FOLDER



logging.basicConfig(level=logging.DEBUG)


def menu_button(caption, callback, package_name=None):

    button = urwid.Button(caption, user_data=package_name)
    urwid.connect_signal(button, 'click', callback, package_name)
    return urwid.AttrMap(button, None, focus_map='reversed')


def sub_menu(caption, choices):
    contents = menu(caption, choices)

    def open_menu(button):
        return top.open_box(contents)

    return menu_button([caption], open_menu)


def menu(title, choices):
    body = [urwid.Text(title), urwid.Divider()]
    body.extend(choices)
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))


def item_chosen(button, package= None):

    response = urwid.Text(['Installing {}...\n'.format(package['title'])])
    install_thread = threading.Thread(target=install_package, args=[package['name'],packages])
    done = menu_button('OK', exit_program)
    top.open_box(urwid.Filler(urwid.Pile([response,done])))
    install_thread.start()
    install_thread.join()


def item_chosen_txt (button, package = None):
    # text_list = package['description_short']
    my_file = open("/tmp/information.txt", "w")
    my_file.write(package['description_full'])
    my_file.close()
    response = urwid.Text("information in new console")
    done = menu_button(u'exit', exit_program)
    top.open_box(urwid.Filler(urwid.Pile([response, done])))
    system("x-terminal-emulator -e less /tmp/information.txt")
    #term = urwid.Terminal(["echo " + package['description_full']])
    #top.open_box(term)

def item_chosen_uninst(button, package = None):
    check_install = None
    response = None
    done = menu_button(u'exit', exit_program)
    check_install = system("test -f " + package['check_link'])
    if check_install == 0:
        response = urwid.Text(package['title']+" uninstalling....")
        install_thread = threading.Thread(target=uninstall_package, args=[package['name'], packages])
        install_thread.start()
        install_thread.join()
    else:
        response = urwid.Text("This package is not installed")

    top.open_box(urwid.Filler(urwid.Pile([response, done])))








def install_end_cb(success):
    logging.debug("SUCCESS: %s", (success))
    top.keypress(None, 'esc')
    done = menu_button('OK', exit_program)
    top.open_box(
        urwid.Filler(
            urwid.Pile([
                urwid.Text('Installation ' + [
                    'failed. Please, check logs for additional info.\n',
                    'succeeded\n'
                ][success]), done
            ])))
    logging.debug("Queue size: %s", (QUEUE.qsize()))
    for _ in range(QUEUE.qsize()):
        stdout, stderr = QUEUE.get()
        logging.debug("STDOUT: %s\nSTDERR: %s\n" % (stdout, stderr))


def not_available(button):
    top.open_box(
        urwid.Filler(
            urwid.Pile([
                urwid.Text("This feature is not available yet"),
                menu_button('OK', lambda x: top.keypress(None, 'esc'))
            ])))


def exit_program(button):
    raise urwid.ExitMainLoop()


def exit_on_q(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()


class CascadingBoxes(urwid.WidgetPlaceholder):
    max_box_levels = 4

    def __init__(self, box):
        super().__init__(urwid.SolidFill())
        self.box_level = 0
        self.open_box(box)

    def open_box(self, box):
        self.original_widget = urwid.Overlay(
            urwid.LineBox(box),
            self.original_widget,
            align='center', width=('relative', 80),
            valign='middle', height=('relative', 80),
            min_width=24, min_height=8,
            left=self.box_level * 3,
            right=(self.max_box_levels - self.box_level - 1) * 3,
            top=self.box_level * 2,
            bottom=(self.max_box_levels - self.box_level - 1) * 2)
        self.box_level += 1

    def keypress(self, size, key):
        if key == 'esc' and self.box_level > 1:
            self.original_widget = self.original_widget[0]
            self.box_level -= 1
        else:
            super().keypress(size, key)


packages = get_software_objects()
current_package = None
menu_top = menu('Maker-Hub', [sub_menu(p["name"], [menu_button("Install", item_chosen, p),menu_button("Uninstall", item_chosen_uninst, p), menu_button("Information", item_chosen_txt, p)]) for p in packages])
top = CascadingBoxes(menu_top)
QUEUE = queue.Queue()


def start_app():
    try:
        loop = urwid.MainLoop(top, palette=[('reversed', 'standout', '')],
                              unhandled_input=exit_on_q)
        loop.run()
    except KeyboardInterrupt:
        loop.stop()


if __name__ == "__main__":
    start_app()