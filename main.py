import configparser as configparser
import kivy
import time
import re
import smtplib
import traceback

import sys

from Adafruit_Thermal import Adafruit_Thermal
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import partial
from PIL import Image
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.settings import SettingsWithTabbedPanel
from kivy.core.window import Window

from settingsjson import settings_json
from settings import SettingPassword, SettingFileChooser

kivy.require('1.10.0')

settings_config = configparser.ConfigParser()
sm = ScreenManager(transition=NoTransition())
photos = []
base_width = 384

# printer = Adafruit_Thermal('/dev/ttyUSB0', 9600, timeout=5) # Linux
# printer = Adafruit_Thermal('COM5', 9600, timeout=5) # Windows


class HomeScreen(Screen):
    def bind_settings(self):
        Window.bind(on_key_up=self.KeyboardShortcut)

    def KeyboardShortcut(self, window, key, *args):
        if key == 115:
            if self.ids.settings.disabled:
                self.ids.settings.disabled = False
                self.ids.settings.opacity = 1
            else:
                self.ids.settings.disabled = True
                self.ids.settings.opacity = 0



class PictureScreen(Screen):
    event = None
    start_time = None
    countdown_value = 5

    def countdown(self, dt):
        self.countdown_value -= 1
        if self.countdown_value == 0:
            self.ids['number'].text = ''
        elif self.countdown_value == -1:
            self.event.cancel()
            self.capture_photo()
            return
        else:
            self.ids['number'].text = str(self.countdown_value)

    def schedule_countdown(self):
        self.start_time = time.strftime("%Y%m%d%H%M%S")
        self.event = Clock.schedule_interval(partial(self.countdown), 1)

    def capture_photo(self):
        # Capture picture here
        photo_name = "IMG_{}_{}.png".format(self.start_time, len(photos))
        camera = self.ids['camera']
        camera.export_to_png(photo_name)

        photos.append(photo_name)
        print(photos)
        print("capture {}".format(len(photos)))

        settings_config.read('photobooth.ini')
        number_pictures = int(settings_config.get('photos', 'max'))

        if len(photos) < number_pictures:
            self.ids['number'].text = "5"
            self.countdown_value = 5
            self.event = Clock.schedule_interval(partial(self.countdown), 1)
        else:
            self.countdown_value = 5
            sm.current = 'print'

    def info_popup_text(self):
        settings_config.read('photobooth.ini')
        event_name = settings_config.get('event', 'title')
        number_pictures = settings_config.get('photos', 'max')
        info_text = "Welcome to the {}!\n" \
                    "There will be a 5 second countdown\nbefore each picture.\n" \
                    "A total of {} picture(s) will be taken.\nEnjoy!".format(event_name, number_pictures)
        popup_text = self.ids['info_popup_text']
        popup_text.text = info_text


class PrintScreen(Screen):
    print_picture = None

    def generate_collage(self):
        image = self.ids['preview']
        images = map(Image.open, photos)
        widths, heights = zip(*(i.size for i in images))

        total_height = sum(heights)
        max_width = max(widths)

        settings_config.read('photobooth.ini')
        selected_header = settings_config.get('photos', 'selected_header')
        banner_image = Image.open(selected_header)
        banner_image = banner_image.resize((max_width, banner_image.height), Image.ANTIALIAS)

        collage = Image.new('RGB', (max_width, total_height+banner_image.height), Image.ANTIALIAS)
        collage.paste(banner_image, (0, 0))
        y_offset = banner_image.height
        for im in images:
            collage.paste(im, (0, y_offset))
            y_offset += im.size[1]

        start_time = photos[0].split("_")[1]
        collage_name = "IMG_{}_collage.png".format(start_time)
        collage.save(collage_name)
        image.source = collage_name

        slider = self.ids['slider_id']
        slider.max = self.get_print_number()

        if printer is None:
            slider.disabled = True
            slider.opacity = 0
            self.ids['slider_text'].opacity = 0
            self.ids['print_button'].disabled = True
            self.ids['print_button'].opacity = 0
            self.ids['copies_text'].text = 'Printer is not connected.  Please proceed to Email.'

    def scale_print_collage(self):
        image = self.ids['preview']
        collage_picture = Image.open(image.source)

        width_percent = (base_width / float(collage_picture.size[0]))
        height_size = int((float(collage_picture.size[1]) * float(width_percent)))
        self.print_picture = collage_picture.resize((base_width, height_size), Image.ANTIALIAS)

        # Save print file
        print_filename = "IMG_{}_print.png".format(photos[0].split("_")[1])
        self.print_picture.save(print_filename)

        for i in range(int(self.ids['slider_id'].value)):
            self.print_collage()

        sm.current = 'email'

    def print_collage(self):
        if printer is not None:
            printer.begin(90)                               # Warmup time
            printer.setTimes(40000, 3000)                   # Set print and feed times
            printer.justify('C')                            # Center alignment
            printer.feed(1)                                 # Add a blank line
            printer.printImage(self.print_picture, True)    # Specify image to print
            printer.feed(3)                                 # Add a few blank lines
        else:
            print('Printer not connected.')
            return

    def get_print_number(self):
        settings_config.read('photobooth.ini')
        number_prints = int(settings_config.get('prints', 'max'))
        return number_prints


class ConfirmPopup(GridLayout):
    text = StringProperty()

    def __init__(self, **kwargs):
        self.register_event_type('on_answer')
        super(ConfirmPopup, self).__init__(**kwargs)

    def on_answer(self, *args):
        pass


class EmailScreen(Screen):
    email = re.compile("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

    def insert(self, value):
        found = False
        for i in self.ids['rv'].data:
            if i['value'] == value:
                found = True
                break

        if self.email.match(value) and not found:
            self.ids['rv'].data.insert(0, {'value': value})

    def test_email(self, value):
        if self.email.match(value):
            self.ids['email_input'].background_color = [0.9,1,0.9,1]
            self.ids['add_email'].disabled = False
        else:
            self.ids['email_input'].background_color = [1,0.9,0.9,1]
            self.ids['add_email'].disabled = True

    def build_email(self):
        start_time = photos[0].split("_")[1]

        emails = ''
        index = 1
        for email in self.ids['rv'].data:
            emails += email['value']
            if not index == len(self.ids['rv'].data):
                emails += ","
            index += 1

        settings_config.read('photobooth.ini')
        username = settings_config.get('email', 'username')
        password = settings_config.get('email', 'password')

        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = emails
        # msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = settings_config.get('email', 'subject')

        msg.attach(MIMEText(settings_config.get('email', 'body')))

        collage = "IMG_{}_collage.png".format(start_time)
        with open(collage, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name="Photobooth_{}.png".format(start_time)
            )
            part['Content-Disposition'] = 'attachment; filename="%s"' % "Photobooth_{}.png".format(start_time)
            msg.attach(part)

        self.send_email(username, password, msg, emails)

    def send_email(self, username, password, msg, emails):
        start_time = photos[0].split("_")[1]

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            try:
                server.ehlo()
                server.starttls()
                server.login(username, password)
                server.sendmail(msg['From'], msg['To'], msg.as_string())
            finally:
                server.close()
        except:
            email_file_name = "EMAILS_{}.txt".format(start_time)
            with open(email_file_name, "w") as output:
                output.write(str(emails))
                output.write(traceback.format_exc().splitlines()[-1])

        del photos[:]
        sm.current = 'home'

    def skip(self):
        if len(self.ids['rv'].data) != 0:
            content = ConfirmPopup(text='You have email addresses listed.\n\nSkip sending email?')
            content.bind(on_answer=self._on_answer)
            popup = Popup(title="Skip Email?",
                          content=content,
                          size_hint=(None, None),
                          size=(480, 250),
                          auto_dismiss=False)
            popup.open()
        else:
            del photos[:]
            sm.current = 'home'

    def _on_answer(self, instance, answer):
        if answer == 'yes':
            del photos[:]
            sm.current = 'home'
        self.popup.dismiss()


class EmailRow(BoxLayout):
    def delete(self, value):
        entries = self.parent.parent.data
        for i in entries:
            if i['value'] == value:
                entries.remove(i)


class PhotoBoothApp(App):
    def build(self):
        sm.add_widget(HomeScreen(name='home', transition=NoTransition()))
        sm.add_widget(PictureScreen(name='picture', transition=NoTransition()))
        sm.add_widget(PrintScreen(name='print', transition=NoTransition()))
        sm.add_widget(EmailScreen(name='email', transition=NoTransition()))

        self.settings_cls = SettingsWithTabbedPanel
        return sm

    def build_config(self, config):
        config.read('photobooth.ini')

    def build_settings(self, settings):
        settings.register_type('password', SettingPassword)
        settings.register_type('filepath', SettingFileChooser)
        settings.add_json_panel('Photobooth', self.config, data=settings_json)

    def on_config_change(self, config, section, key, value):
        print(config, section, key, value)


def connect_printer():
    global printer
    try:
        printer = Adafruit_Thermal('/dev/ttyUSB0', 9600, timeout=5)  # Linux
    except Exception as linux_exception:
        try:
            printer = Adafruit_Thermal('COM5', 9600, timeout=5)  # Windows
        except Exception as windows_exception:
            print(
            'Failed to connect to printer.\n\nLinux Exception: {0}\n\nWindows Exception: {1}'.format(linux_exception,
                                                                                                     windows_exception))
            printer = None


if __name__ == '__main__':
    connect_printer()

    PhotoBoothApp().run()
