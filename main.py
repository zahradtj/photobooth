from functools import partial

import kivy
import time
import re

from PIL import Image
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition

kivy.require('1.10.0')


sm = ScreenManager(transition=NoTransition())
number_pictures = 3
photos = []


class HomeScreen(Screen):
    pass


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
        if len(photos) < number_pictures:
            self.ids['number'].text = "5"
            self.countdown_value = 5
            self.event = Clock.schedule_interval(partial(self.countdown), 1)
        else:
            camera.play = False
            sm.current = 'print'
            print("print")


class PrintScreen(Screen):
    def generate_collage(self):
        image = self.ids['preview']
        images = map(Image.open, photos)
        widths, heights = zip(*(i.size for i in images))

        total_height = sum(heights)
        max_width = max(widths)

        new_im = Image.new('RGB', (max_width, total_height))
        y_offset = 0
        for im in images:
            new_im.paste(im, (0, y_offset))
            y_offset += im.size[1]

        start_time = photos[0].split("_")[1]
        collage_name = "IMG_{}_collage.png".format(start_time)
        new_im.save(collage_name)
        image.source = collage_name


class EmailScreen(Screen):
    def insert(self, value):
        email = re.compile("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

        found = False
        for i in self.ids['rv'].data:
            if i['value'] == value:
                found = True
                break

        if email.match(value) and not found:
            self.ids['rv'].data.insert(0, {'value': value})

    def test_email(self, value):
        email = re.compile("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
        if email.match(value):
            self.ids['email_input'].background_color = [0.9,1,0.9,1]
            self.ids['add_email'].disabled = False
        else:
            self.ids['email_input'].background_color = [1,0.9,0.9,1]
            self.ids['add_email'].disabled = True


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
        return sm


if __name__ == '__main__':
    PhotoBoothApp().run()
