import uerrno
import uasyncio
from display_logo import START_LOGO_2 as START_LOGO
from machine import SoftI2C
from models import events
from models.devices import Level2Device
from primitives.queue import Queue


class Label:
    def __init__(self, label_name, value: str = "---", dev_name=None):
        self._name = label_name
        self._value = value
        self._dev_name = dev_name

    def set_value(self, value):
        self._value = value

    def get_value(self):
        return self._value

    def get_name(self):
        return self._name

    def get_dev_name(self):
        return self._dev_name

    def get_display_msg(self):
        spacing = ' ' * (10 - len(self._name))
        return self._name + spacing + ": " + self._value


class Display:
    def __init__(self, i2c, width=128, height=64):
        from ssd1306 import SSD1306_I2C
        self._d = SSD1306_I2C(width, height, i2c)
        self._d.fill(0)
        self._labels = []

    def set_labels(self, labels: list(Label)):
        self._labels = labels

    def add_label(self, label: Label):
        self._labels.append(label)

    def show_labels(self):
        self._d.fill(0)

        h_offset = 2
        v_offset = 2
        v_distance = 10

        v = v_offset
        h = h_offset
        for label in self._labels:
            self._d.text(label.get_display_msg(), h, v, 1)
            v += v_distance

        self._d.show()

    def update_device_value(self, device_name, value):
        for l in self._labels:
            if l.get_dev_name() == device_name:
                l.set_value(value)
        self.show_labels()

    def update_value(self, name, value):
        for l in self._labels:
            if l.get_name() == name:
                l.set_value(value)
        self.show_labels()

    def background(self, value: bool):
        # 0: black, 1: white
        self._d.invert(value)

    def show_logo(self, input_logo, inverted_input=False):
        self._d.fill(0)

        def show(display, img):
            i = 0
            x = 0
            y = 0
            for pix in img:
                x = i % 128
                if i % 128 == 0:
                    y += 1
                display.pixel(x, y, pix)
                i += 1

        def show_inverted(display, img):
            i = 0
            x = 128
            y = 0
            for pix in img:
                y = i % 64
                if i % 64 == 0:
                    x -= 1
                display.pixel(x, y, pix)
                i += 1

        if inverted_input:
            show_inverted(self._d, input_logo)
        else:
            show(self._d, input_logo)

        self._d.show()

    def clean(self):
        self._d.fill(0)
        self._d.show()


class DisplayGui:
    def __init__(self, i2c, width=128, height=64):
        import gui.fonts.font6 as font
        from gui.core.nanogui import refresh
        from gui.core.writer import Writer
        from gui.widgets.label import Label as gui_label
        from ssd1306 import SSD1306_I2C
        self._d = SSD1306_I2C(width, height, i2c)

        self._font = font
        self._gui_label = gui_label
        self._gui_refresh = refresh

        self._d.fill(0)
        self._gui_refresh(self._d)
        # In case previous tests have altered it
        Writer.set_textpos(self._d, 0, 0)
        self._gui_writer = Writer(self._d, self._font, verbose=False)
        self._gui_writer.set_clip(False, False, False)

        self._labels = []

    def set_labels(self, labels: list(Label)):
        self._labels = labels

    def add_label(self, label: Label):
        self._labels.append(label)

    def show_labels(self):
        self._gui_refresh(self._d)

        nfields = []
        y_offset = 3
        dy = self._font.height() + 0

        x_offset_label_names = 2
        x_offset_label_values = 90
        width_label_values = self._gui_writer.stringlen('OK!')

        for lab in self._labels:
            self._gui_label(self._gui_writer, y_offset,
                            x_offset_label_names, lab.get_name())
            f = self._gui_label(self._gui_writer, y_offset,
                                x_offset_label_values, width_label_values, bdcolor=None)
            f.value(lab.get_value())
            nfields.append(f)
            y_offset += dy

        self._gui_refresh(self._d)

    def update_device_value(self, device_name, value):
        for l in self._labels:
            if l.get_dev_name() == device_name:
                l.set_value(value)
        self.show_labels()

    def update_value(self, name, value):
        for l in self._labels:
            if l.get_name() == name:
                l.set_value(value)
        self.show_labels()

    def background(self, value: bool):
        # 0: black, 1: white
        self._d.invert(value)

    def show_logo(self, input_logo, inverted_input=False):
        self._d.fill(0)

        def show(display, img):
            i = 0
            x = 0
            y = 0
            for pix in img:
                x = i % 128
                if i % 128 == 0:
                    y += 1
                display.pixel(x, y, pix)
                i += 1

        def show_inverted(display, img):
            i = 0
            x = 128
            y = 0
            for pix in img:
                y = i % 64
                if i % 64 == 0:
                    x -= 1
                display.pixel(x, y, pix)
                i += 1

        if inverted_input:
            show_inverted(self._d, input_logo)
        else:
            show(self._d, input_logo)

        self._d.show()

    def clean(self):
        self._d.fill(0)
        self._d.show()


async def display_coro(i2c: SoftI2C, outgoing_display_queue: Queue, dev_to_process: list(Level2Device), display_labels: list(str)):
    try:
        # display = Display(i2c)
        display = DisplayGui(i2c)
    except OSError as e:
        if e.errno == uerrno.ENODEV:
            print("display_coro: no display found. Skipping...")
        return
    display.background(1)

    # Associate labels with devices
    for dev_name, dev_label in zip([dev._name for dev in dev_to_process], display_labels):
        print(
            f"display_coro: associating '{dev_name}' with label '{dev_label}'")
        display.add_label(Label(dev_name=dev_name, label_name=dev_label))

    # Add battery label
    _BATTERY_LABEL = 'BATTERIA'
    display.add_label(Label(label_name=_BATTERY_LABEL))

    # Show startup logo for 6s
    display.show_logo(START_LOGO, True)
    await uasyncio.sleep(6)
    display.clean()

    # Show labels
    display.show_labels()

    # Update labels based on events
    while True:
        e = await outgoing_display_queue.get()
        e_type = type(e)

        if e_type == events.RssiOkEvent:
            display.update_device_value(e.get_device_name(), 'OK!')

        elif e_type == events.RssiLowEvent:
            display.update_device_value(e.get_device_name(), 'NO!')

        elif e_type == events.RssiObsoleteEvent:
            display.update_device_value(e.get_device_name(), '---')

        elif e_type == events.BatteryEvent:
            display.update_device_value(_BATTERY_LABEL, e.get_voltage())
