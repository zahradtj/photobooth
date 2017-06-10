import kivy
from kivy._clock import ClockEvent
from kivy._event import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition

kivy.require('1.10.0')  # replace with your current kivy version !


class HomeScreen(Screen):
    pass


class PreviewScreen(Screen):
    pass


class PictureScreen(Screen):
    event = None

    def countdown(self, dt):
        current = int(self.ids['number'].text)
        current -= 1
        if current == 0:
            self.ids['number'].text = ""
            self.event.cancel()
            return
        self.ids['number'].text = str(current)

    def schedule_countdown(self):
        self.event = Clock.schedule_interval(partial(self.countdown), 1)


class CountdownScreen(Screen):
    pass


sm = ScreenManager(transition=NoTransition())


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
