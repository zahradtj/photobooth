import kivy
import time
from kivy._event import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition

kivy.require('1.10.0')


sm = ScreenManager(transition=NoTransition())
number_pictures = 3


class HomeScreen(Screen):
    pass


class PreviewScreen(Screen):
    pass


class PictureScreen(Screen):
    event = None
    photos = []
    start_time = None

    def countdown(self, dt):
        current = int(self.ids['number'].text)
        current -= 1
        if current == 0:
            self.ids['number'].text = ""
            self.event.cancel()
            self.capture_photo()
            return
        self.ids['number'].text = str(current)

    def schedule_countdown(self):
        self.start_time = time.strftime("%Y%m%d%H%M%S")
        self.event = Clock.schedule_interval(partial(self.countdown), 1)

    def capture_photo(self):
        # Capture picture here
        photoName = self.start_time + "_{}.jpg".format(len(self.photos))
        Window.screenshot(name=photoName)

        self.photos.append("picture")
        print "capture {}".format(len(self.photos))
        if len(self.photos) < number_pictures:
            self.ids['number'].text = "5"
            self.event = Clock.schedule_interval(partial(self.countdown), 1)
        else:
            print "print"


class PhotoBoothApp(App):

    def build(self):
        sm.add_widget(HomeScreen(name='home', transition=NoTransition()))
        sm.add_widget(PictureScreen(name='picture', transition=NoTransition()))
        return sm

    # Callback for thumbnail refresh
    def callback(self, instance):
        # self.photo.reload()
        pass

if __name__ == '__main__':
    PhotoBoothApp().run()
