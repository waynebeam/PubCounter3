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
    manager = ObjectProperty(None)

    def build(self):
        pubs = load_file()
        self.manager = NavigationScreenManager(pubs)
        screen = SingleNameScreen(pubs["wayne beam"])
        return self.manager


class NavigationScreenManager(ScreenManager):
    def __init__(self, pubs, **kwargs):
        super().__init__(**kwargs)
        self.screen_stack = []
        self.publishers = pubs

    def show_all_names_screen(self):
        names = [name for name in self.publishers]
        self.show_name_list_screen(names)

    def show_name_list_screen(self, names: []):
        screen = NameListScreen(names)
        self.change_screens(screen)

    def show_single_name_screen(self, name: str):
        pub = self.publishers[name]
        screen = SingleNameScreen(pub)
        self.change_screens(screen)

    def show_all_tags_screen(self):
        all_tags = []
        for pub in self.publishers:
            for tag in self.publishers[pub]["tags"]:
                if tag not in all_tags:
                    all_tags.append(tag)

        screen = AllTagsScreen(all_tags)
        self.change_screens(screen)

    def change_screens(self, next_screen: Screen):
        self.screen_stack.append(self.current_screen)
        self.add_widget(next_screen)
        self.transition.direction = "left"
        self.current = next_screen.name

    def go_back(self):
        current = self.current_screen
        self.transition.direction = "right"
        self.current = self.screen_stack[-1].name
        self.remove_widget(current)
        self.screen_stack.pop()


class SingleNameScreen(Screen):
    def __init__(self, pub: Publisher, **kwargs):
        super().__init__(**kwargs)
        self.name = "name_screen"
        layout = BoxLayout(orientation="vertical")
        back_btn = BackButton()
        back_btn.bind(on_release=self.back_btn_bind)
        layout.add_widget(back_btn)
        name_label = Label(text=pub["name"], size_hint=(1, .3))
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

    def back_btn_bind(self, btn):
        self.manager.go_back()


class BackButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = "back"
        self.size_hint = (1, .2)


class NameListScreen(Screen):
    def __init__(self, names: [], list_type: str = "in all", **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical")
        back_btn = BackButton()
        back_btn.bind(on_release=self.back_btn_bind)
        layout.add_widget(back_btn)
        layout.add_widget(Label(text=f"{len(names)} Publishers {list_type}", size_hint=(1, .2)))
        names_scroll_section = ScrollView()
        names_grid = GridLayout(cols=2, size_hint_y=None, spacing=2)
        names_grid.bind(minimum_height=names_grid.setter("height"))
        for name in names:
            btn = Button(text=name.title(), size_hint_y=None, height=50)
            names_grid.add_widget(btn)
            btn.bind(on_release=self.bind_name_btn)
        names_scroll_section.add_widget(names_grid)
        layout.add_widget(names_scroll_section)
        self.add_widget(layout)

    def bind_name_btn(self, btn):
        self.manager.show_single_name_screen(btn.text.lower())

    def back_btn_bind(self, btn):
        self.manager.go_back()


class AllTagsScreen(Screen):
    def __init__(self, tags: [], **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical")
        back_btn = BackButton()
        back_btn.bind(on_release=self.back_btn_bind)
        layout.add_widget(back_btn)
        self.number_of_tags = len(tags)
        self.title_label = Label(text=f"Choose one of the {self.number_of_tags} tags", size_hint=(1, .2))
        self.tags_to_search = []
        layout.add_widget(self.title_label)
        tags_scroll_section = ScrollView()
        tags_grid = GridLayout(cols=2, size_hint_y=None, spacing=2)
        tags_grid.bind(minimum_height=tags_grid.setter("height"))
        for tag in tags:
            btn = Button(text=tag.title(), size_hint_y=None, height=50)
            tags_grid.add_widget(btn)
            btn.bind(on_release=self.bind_tag_btn)
        tags_scroll_section.add_widget(tags_grid)
        layout.add_widget(tags_scroll_section)
        self.search_btn = Button(text="Search", size_hint=(1,.2))
        layout.add_widget(self.search_btn)
        self.add_widget(layout)

    def bind_tag_btn(self, btn):
        if btn.text not in self.tags_to_search:
            self.tags_to_search.append(btn.text)
        else:
            self.tags_to_search.remove(btn.text)

        if self.tags_to_search:
            self.search_btn.text = f"Search for {len(self.tags_to_search)} tags"
            new_title = ""
            for tag in self.tags_to_search:
                new_title += f"{tag}, "
            self.title_label.text = new_title
        else:
            self.title_label.text = f"Choose one of the {self.number_of_tags} tags"
            self.search_btn.text = "Search"



    def back_btn_bind(self, btn):
        self.manager.go_back()


if __name__ == '__main__':
    PubCounter3().run()
