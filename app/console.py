import urwid
from installer import get_software_objects


def menu_button(caption, callback):
    button = urwid.Button(caption)
    urwid.connect_signal(button, 'click', callback)
    return urwid.AttrMap(button, None, focus_map='reversed')


def sub_menu(caption, choices):
    contents = menu(caption, choices)

    def open_menu(button):
        return top.open_box(contents)

    return menu_button([caption, "..."], open_menu)


def menu(title, choices):
    body = [urwid.Text(title), urwid.Divider()]
    body.extend(choices)
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))


def item_chosen(button):
    response = urwid.Text(['You chose {}\n'.format(button.label)])
    done = menu_button('OK', exit_program)
    top.open_box(urwid.Filler(urwid.Pile([response, done])))


def exit_program(button):
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
            bottom=(self.max_box_levels - self.box_level - 1) * 2
        )
        self.box_level += 1

    def keypress(self, size, key):
        if key == 'esc' and self.box_level > 1:
            self.original_widget = self.original_widget[0]
            self.box_level -= 1
        else:
            super().keypress(size, key)


packages = get_software_objects()
menu_top = menu('Maker-Hub', [
    sub_menu('Install software', [menu_button(name, item_chosen) for name in packages.keys()])
])
top = CascadingBoxes(menu_top)


def start_app():
    urwid.MainLoop(top, palette=[('reversed', 'standout', '')]).run()
