import kivy
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from publisher import Publisher
import json


def load_file():
    pubs = {}
    try:
        with open("publishers.txt") as f:
            raw_data = f.read()
        raw_data = json.loads(raw_data)
        for pub in raw_data:
            new_pub = Publisher(**pub)
            pubs[new_pub["name"]] = new_pub
        return pubs

    except FileNotFoundError:
        return pubs


class PubCounter3(App):
    manger = ObjectProperty(None)

    def build(self):
        pubs = load_file()
        self.manager = NavigationScreenManager(pubs)
        screen = NameScreen(pubs["ulysses ashton"])
        return screen


class NavigationScreenManager(ScreenManager):
    def __init__(self, pubs, **kwargs):
        super().__init__(**kwargs)
        self.screen_stack = []
        self.publishers = pubs

    def show_name_screen(self):
        pass


class NameScreen(Screen):
    def __init__(self, pub: Publisher, **kwargs):
        super().__init__(**kwargs)
        self.name = "name_screen"
        layout = BoxLayout(orientation="vertical")
        back_btn = Button(text="back", size_hint=(1,.2))
        layout.add_widget(back_btn)
        name_label = Label(text=pub["name"], size_hint=(1,.3))
        layout.add_widget(name_label)
        tags_scroll_section = ScrollView()
        layout.add_widget(tags_scroll_section)
        tags_grid = GridLayout(cols=1, size_hint_y=None, spacing=2)
        tags_grid.bind(minimum_height=tags_grid.setter("height"))
        for tag in pub["tags"]:
            btn = Button(text=tag, size_hint_y=None, height=50)
            tags_grid.add_widget(btn)
        tags_scroll_section.add_widget(tags_grid)
        self.add_widget(layout)


if __name__ == '__main__':
    PubCounter3().run()
