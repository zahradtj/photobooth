from kivy.uix.filechooser import FileChooser, FileChooserIconView, FileChooserIconLayout, FileChooserListView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.settings import SettingString, SettingPath
import configparser as configparser

settings_config = configparser.ConfigParser()


class PasswordLabel(Label):
    pass


class SettingPassword(SettingString):
    def _create_popup(self, instance):
        super(SettingPassword, self)._create_popup(instance)
        self.textinput.password = True

    def add_widget(self, widget, *largs):
        if self.content is None:
            super(SettingString, self).add_widget(widget, *largs)
        if isinstance(widget, PasswordLabel):
            return self.content.add_widget(widget, *largs)


class HeaderLabel(Label):
    def set_label(self):
        settings_config.read('photobooth.ini')
        selected_header = str(settings_config.get('photos', 'selected_header'))
        header_path = str(settings_config.get('photos', 'header_path'))
        filename = 'header file'
        if selected_header:
            filename = selected_header.split(header_path)[1].split("\\")[1]
        return filename


class SettingFileChooser(SettingPath):
    def _create_popup(self, instance):
        super(SettingFileChooser, self)._create_popup(instance)
        for child in self.popup.content.children:
            if isinstance(child, FileChooserListView):
                settings_config.read('photobooth.ini')
                path = settings_config.get('photos', 'header_path')
                child.rootpath = path
                child.path = path
                break

    def add_widget(self, widget, *largs):
        if self.content is None:
            super(SettingPath, self).add_widget(widget, *largs)
        if isinstance(widget, HeaderLabel):
            return self.content.add_widget(widget, *largs)
