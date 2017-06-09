import kivy

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition

kivy.require('1.10.0')  # replace with your current kivy version !


class HomeScreen(Screen):
    pass


class PreviewScreen(Screen):
    pass


class PictureScreen(Screen):
    pass


class CountdownScreen(Screen):
    # def countdown(self, dt):
    #     current = int(self.ids['number'].text)
    #     current -= 1
    #     self.ids['number'].text = str(current)
    #     if current == 0:
    #         return
    #         # sm.transition = NoTransition()
    #         # self.ids['number'].text = str(5)
    #         # sm.current = 'countdown'
    #
    # def schedule_countdown(self):
    #     Clock.schedule_interval(partial(self.countdown), 1)
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
