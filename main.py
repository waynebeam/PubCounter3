import kivy
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from publisher import Publisher
from kivy.metrics import dp
import json
import re
from kivy.uix.textinput import TextInput
# from kivy.config import Config
# Config.set('graphics', 'width', '500')
# Config.set('graphics', 'height', '700')
from kivy.core.window import Window

Window.size = (500, 700)


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
        self.all_tags = self.find_all_tags()
        self.main_menu_screen = self.current_screen

    def find_all_tags(self) -> []:
        all_tags = []
        for pub in self.publishers:
            for tag in self.publishers[pub]["tags"]:
                if tag not in all_tags:
                    all_tags.append(tag)

        all_tags.sort()
        return all_tags

    def show_all_names_screen(self):
        names = [name for name in self.publishers]
        names.sort(key=lambda entry: entry.split()[1])
        self.show_name_list_screen(names)

    def show_name_list_screen(self, names: [], title_decoration: str = "in all"):
        screen = NameListScreen(names, title_decoration)
        self.change_screens(screen)

    def show_single_name_screen(self, name: str):
        pub = self.publishers[name]
        screen = SingleNameScreen(pub)
        self.change_screens(screen)

    def show_add_tags_screen(self, pub: Publisher):
        screen = AddTagScreen(pub, self.all_tags)
        self.change_screens(screen)

    def show_all_tags_screen(self):

        screen = AllTagsScreen(self.all_tags)
        self.change_screens(screen)

    def create_matching_pubs_screen(self, tags: []):
        matching_pubs = []
        pubs = self.publishers
        if "or" in tags:
            for pub in pubs:
                if pub not in matching_pubs:
                    if any(tag.lower() in pubs[pub]["tags"] for tag in tags):
                        matching_pubs.append(pub.title())
        else:
            for pub in pubs:
                if pub not in matching_pubs:
                    if all(tag.lower() in pubs[pub]["tags"] for tag in tags if tag != "and"):
                        matching_pubs.append(pub.title())
        if matching_pubs:
            title_str = "who match " + ", ".join(tags)
            return True, matching_pubs, title_str
        else:
            return False, [], "No matches found"

    def return_to_main_menu_screen(self):
        self.transition.direction = "right"
        self.screen_stack.clear()
        self.add_widget(self.main_menu_screen)
        self.remove_widget(self.current_screen)
        self.current = "main_menu_screen"

    def change_screens(self, next_screen: Screen):
        if next_screen.name != self.current:
            self.screen_stack.append(self.current_screen)
            self.add_widget(next_screen)
            self.remove_widget(self.current_screen)
            self.transition.direction = "left"
            self.current = next_screen.name

    def go_back(self):
        current = self.current_screen
        self.transition.direction = "right"
        self.add_widget(self.screen_stack[-1])
        self.current = self.screen_stack[-1].name
        self.remove_widget(current)
        self.screen_stack.pop()


class BasicScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical")
        navigation_bar_top = TopNavigationBar()
        navigation_bar_top.back_btn.bind(on_release=self.back_btn_bind)
        self.header = BoxLayout(size_hint=(1, .2))
        self.body = BoxLayout(orientation="vertical")
        navigation_bar_bottom = BottomNavigationBar()
        navigation_bar_bottom.home_btn.bind(on_release=self.bind_home_btn)
        navigation_bar_bottom.tag_screen_btn.bind(on_release=self.all_tags_btn)
        navigation_bar_bottom.all_pub_screen_btn.bind(on_release=self.all_pubs_btn)
        self.layout.add_widget(navigation_bar_top)
        self.layout.add_widget(self.header)
        self.layout.add_widget(self.body)
        self.layout.add_widget(navigation_bar_bottom)

    def bind_home_btn(self, btn):
        self.manager.return_to_main_menu_screen()

    def back_btn_bind(self, btn):
        self.manager.go_back()

    def bind_tag_btn(self, btn):
        tag = [btn.text]
        result, title_str, matching_pubs = self.manager.create_matching_pubs_screen(tag)
        self.manager.show_name_list_screen(title_str, matching_pubs)

    def bind_scroll_bottom_button(self, btn):
        self.body_scroller.scroll_y = 0

    def bind_name_btn(self, btn):
        self.manager.show_single_name_screen(btn.text.lower())

    def all_tags_btn(self, btn):
        self.manager.show_all_tags_screen()

    def all_pubs_btn(self, btn):
        self.manager.show_all_names_screen()


class TopNavigationBar(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, .1)
        self.back_btn = Button(text="back", size_hint=(.2, 1))
        self.add_widget(self.back_btn)
        title = Label(text="PubCounter")
        self.add_widget(title)
        self.add_widget(Widget(size_hint=(.2, 1)))


class BottomNavigationBar(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, .1)
        self.home_btn = Button(text="home")
        self.add_widget(self.home_btn)
        self.all_pub_screen_btn = Button(text="All Pubs")
        self.tag_screen_btn = Button(text="All Tags")
        self.add_widget(self.tag_screen_btn)
        self.add_widget(self.all_pub_screen_btn)


class ListScreen(BasicScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.body_scroller = ScrollView(bar_width=10, bar_margin=5, effect_cls="ScrollEffect")
        self.body.add_widget(self.body_scroller)


class SingleNameScreen(ListScreen):
    def __init__(self, pub: Publisher, **kwargs):
        super().__init__(**kwargs)
        self.name = "name_screen"
        self.publisher = pub
        name_label = Label(text=pub["name"].title(), size_hint=(1, .3))
        self.header.add_widget(name_label)
        self.bind(on_pre_enter=self.setup_tag_list)

        add_remove_layout = BoxLayout(size_hint=(1, .3))
        add_tag_btn = Button(text="Add tags")
        add_tag_btn.bind(on_release=self.bind_add_tags_btn)
        remove_tag_btn = Button(text="Remove tags (coming soon)")
        add_remove_layout.add_widget(add_tag_btn)
        add_remove_layout.add_widget(remove_tag_btn)
        self.body.add_widget(add_remove_layout)
        self.add_widget(self.layout)

    def setup_tag_list(self,target):
        self.body_scroller.clear_widgets()
        tags_grid = GridLayout(cols=1, size_hint_y=None, spacing=2)
        tags_grid.bind(minimum_height=tags_grid.setter("height"))
        for tag in self.publisher["tags"]:
            btn = Button(text=tag.title(), size_hint_y=None, height=dp(50))
            tags_grid.add_widget(btn)
            btn.bind(on_release=self.bind_tag_btn)
        self.body_scroller.add_widget(tags_grid)

    def bind_add_tags_btn(self,btn):
        self.manager.show_add_tags_screen(self.publisher)


class AddTagScreen(ListScreen):
    def __init__(self, pub: Publisher, all_tags: [], **kwargs):
        super().__init__(**kwargs)
        self.name = 'add_tag_screen'
        self.publisher = pub
        self.new_tags = []
        self.title_label = Label(text=f"Add tags to {pub['name'].title()}")
        self.header.orientation = "vertical"
        self.header.add_widget(self.title_label)
        self.enter_new_tag_layout = BoxLayout()
        self.enter_new_tag_field = NewTagTextInput(hint_text="Type new tag or select from below", multiline=False,
                                                   size_hint_x=.8)
        self.enter_new_tag_btn = Button(text="Enter", size_hint_x=.2)
        self.enter_new_tag_field.bind(on_text_validate=self.bind_enter_new_tag)
        self.enter_new_tag_btn.bind(on_release=self.bind_enter_new_tag)
        self.enter_new_tag_layout.add_widget(self.enter_new_tag_field)
        self.enter_new_tag_layout.add_widget(self.enter_new_tag_btn)
        self.header.add_widget(self.enter_new_tag_layout)
        self.tags_grid = GridLayout(cols=2, size_hint_y=None)
        self.tags_grid.bind(minimum_height=self.tags_grid.setter("height"))
        for tag in all_tags:
            if tag not in pub["tags"]:
                new_tag_btn = Button(text=tag,size_hint_y=None, height=dp(50))
                self.tags_grid.add_widget(new_tag_btn)
                new_tag_btn.bind(on_release=self.bind_add_tag_btn)

        self.body_scroller.add_widget(self.tags_grid)
        self.accept_changes_btn = Button(text="Save changes", size_hint_y=.2, disabled=True)
        self.accept_changes_btn.bind(on_release=self.bind_accept_changes_button)
        self.tags_to_add_label = Label(text=f"New tags: ", size_hint_y=.2)
        self.body.add_widget(self.tags_to_add_label)
        self.body.add_widget(self.accept_changes_btn)
        self.add_widget(self.layout)

    def bind_add_tag_btn(self, btn):
        new_tag = btn.text.lower()
        self.add_new_tag_to_list(new_tag)
        self.update_tags_to_add_label()

    def add_new_tag_to_list(self, new_tag):
        if new_tag not in self.new_tags:
            self.new_tags.append(new_tag)
        else:
            self.new_tags.remove(new_tag)

    def bind_enter_new_tag(self, btn):
        new_tag = self.enter_new_tag_field.text.lower()
        if new_tag and new_tag not in self.new_tags and not any(new_tag == x.text for x in self.tags_grid.children) and not any(new_tag == t for t in self.publisher["tags"]):
            new_btn = Button(text=new_tag,size_hint_y=None, height=dp(50))
            self.tags_grid.add_widget(new_btn)
            new_btn.bind(on_release=self.bind_add_tag_btn)
            self.new_tags.append(new_tag)
            self.update_tags_to_add_label()
            self.enter_new_tag_field.text = ""
            self.enter_new_tag_field.hint_text = "Type new tag or select from below"
        else:
            self.enter_new_tag_field.text = ""
            self.enter_new_tag_field.hint_text = "Enter a new tag"

    def update_tags_to_add_label(self):
        if self.new_tags:
            self.tags_to_add_label.text = str(self.new_tags)
            self.accept_changes_btn.disabled = False
        else:
            self.tags_to_add_label.text = "No new tags selected"
            self.accept_changes_btn.disabled = True

    def bind_accept_changes_button(self, btn):
        for tag in self.new_tags:
            self.publisher["tags"].append(tag)
        self.manager.go_back()


class NewTagTextInput(TextInput):
    pat = re.compile(r'[a-zA-Z]')

    def insert_text(self, substring, from_undo=False):
        if self.pat.match(substring):
            super().insert_text(substring, from_undo=from_undo)


class NameListScreen(ListScreen):
    def __init__(self, names: [], list_type: str = "in all", **kwargs):
        super().__init__(**kwargs)
        self.name = "namelist"

        title_label = Label(text=f"{len(names)} Publishers {list_type}", size_hint=(.8, 1))
        self.header.add_widget(title_label)

        if len(names) >= 40:
            scroll_bottom_btn = Button(text="Scroll down", size_hint=(.2, 1))
            scroll_bottom_btn.bind(on_release=self.bind_scroll_bottom_button)
            self.header.add_widget(scroll_bottom_btn)

        names_grid = GridLayout(cols=2, size_hint_y=None, spacing=2)
        names_grid.bind(minimum_height=names_grid.setter("height"))
        for name in names:
            btn = Button(text=name.title(), size_hint_y=None, height=dp(50))
            names_grid.add_widget(btn)
            btn.bind(on_release=self.bind_name_btn)
        self.body_scroller.add_widget(names_grid)
        self.add_widget(self.layout)


class AllTagsScreen(ListScreen):
    def __init__(self, tags: [], **kwargs):
        super().__init__(**kwargs)
        self.number_of_tags = len(tags)
        self.tags_to_search = []
        self.search_or = False

        self.title_label = Label(text=f"Choose from the {self.number_of_tags} tags", size_hint=(.8, 1))
        or_toggle_btn = Button(text="[AND]/or", size_hint=(.2, 1))
        or_toggle_btn.bind(on_release=self.bind_or_toggle_btn)
        self.header.add_widget(self.title_label)
        self.header.add_widget(or_toggle_btn)
        tags_grid = GridLayout(cols=2, size_hint_y=None, spacing=2)
        tags_grid.bind(minimum_height=tags_grid.setter("height"))
        for tag in tags:
            btn = Button(text=tag.title(), size_hint_y=None, height=dp(50))
            tags_grid.add_widget(btn)
            btn.bind(on_release=self.bind_tag_btn)
        self.body_scroller.add_widget(tags_grid)
        self.search_btn = Button(text="Search", size_hint=(1, .2), disabled=True)
        self.search_btn.bind(on_release=self.bind_search_btn)
        self.body.add_widget(self.search_btn)
        self.add_widget(self.layout)

    def bind_tag_btn(self, btn):
        if btn.text not in self.tags_to_search:
            self.tags_to_search.append(btn.text)
        else:
            self.tags_to_search.remove(btn.text)
            if len(self.tags_to_search) == 2:
                if "or" in self.tags_to_search:
                    self.tags_to_search.remove("or")
                elif "and" in self.tags_to_search:
                    self.tags_to_search.remove("and")
        num_tags = len(self.tags_to_search)
        if self.tags_to_search:
            self.search_btn.disabled = False
            if len(self.tags_to_search) > 1:
                if self.search_or:
                    if "or" in self.tags_to_search:
                        self.tags_to_search.remove("or")
                    self.tags_to_search.insert(-1, "or")
                else:
                    if "and" in self.tags_to_search:
                        self.tags_to_search.remove("and")
                    self.tags_to_search.insert(-1, "and")
            self.search_btn.text = f"Search for {num_tags - 1 if num_tags > 2 else num_tags} tags"
            new_title = ""
            for i, tag in enumerate(self.tags_to_search):
                new_title += tag
                if i < len(self.tags_to_search) - 1:
                    new_title += ", "
            self.title_label.text = new_title
        else:
            self.title_label.text = f"Choose from the {self.number_of_tags} tags"
            self.search_btn.text = "Search"
            self.search_btn.disabled = True

    def bind_or_toggle_btn(self, btn):
        if self.search_or:
            self.search_or = False
            btn.text = "[AND]/or"
        else:
            self.search_or = True
            btn.text = "and/[OR]"
        if "or" in self.tags_to_search:
            self.tags_to_search.remove("or")
            self.tags_to_search.insert(-1, "and")
            self.title_label.text = str.replace(self.title_label.text, "or", "and")
        elif "and" in self.tags_to_search:
            self.tags_to_search.remove("and")
            self.tags_to_search.insert(-1, "or")
            self.title_label.text = str.replace(self.title_label.text, "and", "or")

    def bind_search_btn(self, btn):
        result, title_str, matching_pubs = self.manager.create_matching_pubs_screen(self.tags_to_search)
        if result:
            self.manager.show_name_list_screen(title_str, matching_pubs)
        else:
            self.title_label.text = "No matches found"
            self.tags_to_search.clear()


if __name__ == '__main__':
    PubCounter3().run()
