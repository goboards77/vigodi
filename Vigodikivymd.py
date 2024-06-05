import sqlite3
from kivy.lang import Builder
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivy.properties import ObjectProperty
from kivy.metrics import dp
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivy.clock import mainthread


KV_BASE = '''
MDScreen:
    MDNavigationLayout:
        MDScreenManager:
            MDScreen:
                SuggestionTextField:
                    id: txtname
                    mode: "round"
                    hint_text: "Name"
                    pos_hint: {"center_x": .24, "center_y": .96}
                    size_hint_x: 0.40
                    size_hint_y: 0.05
                    multiline: False
                    
                SuggestionTextField:
                    id: txtfather
                    mode: "round"
                    hint_text: "Father"
                    pos_hint: {"center_x": .24, "center_y": .90}
                    size_hint_x: 0.40
                    size_hint_y: 0.05
                    multiline: False
                    
                SuggestionTextField:
                    id: txtmother
                    mode: "round"
                    hint_text: "Mother"
                    pos_hint: {"center_x": .66, "center_y": .90}
                    size_hint_x: 0.40
                    size_hint_y: 0.05
                    multiline: False
                    
                SuggestionTextField:
                    id: txtgrandfather
                    mode: "round"
                    hint_text: "GrandFather"
                    pos_hint: {"center_x": .24, "center_y": .84}
                    size_hint_x: 0.40
                    size_hint_y: 0.05
                    multiline: False
                    
                SuggestionTextField:
                    id: txtgrandmother
                    mode: "round"
                    hint_text: "GrandMother"
                    pos_hint: {"center_x": .66, "center_y": .84}
                    size_hint_x: 0.40
                    size_hint_y: 0.05
                    multiline: False
                    
                MDRoundFlatButton:
                    text: "Open Drawer"
                    size_hint_x: 0.40
                    size_hint_y: 0.01
                    pos_hint: {"center_x": 0.24, "center_y": 0.78}
                    on_release: 
                        nav_drawer.set_state("toggle")
                        app.update_label()
                
                MDRoundFlatButton:
                    text: "View"
                    size_hint_x: 0.40
                    size_hint_y: 0.01
                    pos_hint: {"center_x": 0.66, "center_y": 0.78}
                    on_release: app.view()

        MDNavigationDrawer:
            id: nav_drawer
            radius: [0, 50, 50, 0]
            on_state: app.on_drawer_state(self, self.state)

            MDNavigationDrawerMenu:
                MDNavigationDrawerHeader:
                    title: "Vigodi@Glance"

                MDNavigationDrawerDivider:
'''

LABELS = [
    ('jansankhya_label', "Jansankhya"),
    ('purush_sankhya_label', "Purush Sankhya"),
    ('strii_sankhya_label', "Strii Sankhya"),
    ('kunvari_niyani_label', "Kunvari Niyani"),
    ('parneli_niyani_label', "Parneli Niyani"),
    ('kul_nokh_label', "Kul Nokh"),
    ('bahargam_label', "(bahar)Ketla Gamoma"),
    ('vis_varsh_niche_label', "20varsh Niche"),
    ('varsh_21_40_label', "21 to 40 varsh"),
    ('varsh_41_60_label', "41 to 60 varsh"),
    ('varsh_61_80_label', "61 to 80 varsh"),
    ('varsh_81_100_label', "81 to 100 varsh"),
    ('mobile', 'Change? 9998814014')
]

KV = KV_BASE + ''.join(f'''
                MDNavigationDrawerLabel:
                    id: {label_id}
                    text: "{label_text}"

                MDNavigationDrawerDivider:
''' for label_id, label_text in LABELS)

class SuggestionTextField(MDTextField):
    dropdown = ObjectProperty(None)
    suggestions = []

    def __init__(self, **kwargs):
        super(SuggestionTextField, self).__init__(**kwargs)
        self.dropdown = DropDown()
        self.suggestions = self.fetch_suggestions()
        self.bind(text=self.on_text)

    def fetch_suggestions(self):
        suggestions = []
        try:
            conn = sqlite3.connect('Vigodi.db')
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT name FROM (SELECT Name AS name FROM Data UNION "
                        "SELECT Father AS name FROM Data UNION "
                        "SELECT Mother AS name FROM Data UNION "
                        "SELECT Grandfather AS name FROM Data UNION "
                        "SELECT Grandmother AS name FROM Data)")
            rows = cur.fetchall()
            suggestions = [row[0] for row in rows]
            conn.close()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        return suggestions

    def on_text(self, instance, value):
        self.dropdown.dismiss()
        self.dropdown = DropDown()

        if value:
            filtered_suggestions = [s for s in self.suggestions if s.lower().startswith(value.lower())]
            if filtered_suggestions:
                for suggestion in filtered_suggestions:
                    btn = Button(text=suggestion, size_hint_y=None, height=90)
                    btn.bind(on_release=lambda btn: self.select_suggestion(btn.text))
                    self.dropdown.add_widget(btn)
                self.dropdown.open(self)

    def select_suggestion(self, text):
        self.text = text
        self.dropdown.dismiss()

class Test(MDApp):
    data_table = None
    layout = None

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        self.layout = Builder.load_string(KV)

        self.data_table = MDDataTable(
            size_hint=(0.90, 0.73),
            pos_hint={"center_x": 0.42, "center_y": 0.38},
            rows_num=15,
            column_data=[
                ("Name", dp(30)),
                ("Father", dp(30)),
                ("Mother", dp(30)),
                ("Grandfather", dp(30)),
                ("Grandmother", dp(30))
            ]
        )
        self.layout.add_widget(self.data_table)

        def on_stop(self):
            self.conn.close()

        return self.layout

    @mainthread
    def update_label(self):
        queries = {
            "jansankhya_label": ("SELECT COUNT(Name) FROM Data WHERE NOT ((Relation = 'Putri' AND MaritalStatus = 'M') "
                                 "OR (Relation = 'Pautri' AND MaritalStatus = 'M') OR (Relation = 'Jamai') OR (Place='Vaikunth'))",
                                 "Jansankhya := {}"),
            "purush_sankhya_label": ("SELECT COUNT(Name) FROM Data WHERE Relation IN ('Pote', 'Putra', 'Pautra') AND Place<>'Vaikunth'",
                                     "Purush Sankhya := {}"),
            "strii_sankhya_label": ("SELECT COUNT(Name) FROM Data WHERE Relation IN ('Patni', 'Putravadhu', 'Pautravadhu') AND Place<>'Vaikunth'",
                                    "Strii Sankhya := {}"),
            "kunvari_niyani_label": (
                                    "SELECT COUNT(Name) FROM Data WHERE Relation IN ('Bahen', 'Putri', 'Pautri', 'Padpautri') AND (Maritalstatus <> 'M' AND Place <> 'Vaikunth')",
                                    "Kunvari Niyani := {}"),
            "parneli_niyani_label": (
                                    "SELECT COUNT(Name) FROM Data WHERE Relation IN ('Bahen', 'Putri', 'Pautri', 'Padpautri') AND (Maritalstatus = 'M' AND Place <> 'Vaikunth')",
                                    "Parneli Niyani := {}"),
            "kul_nokh_label": ("SELECT COUNT(DISTINCT Nokh) FROM Data WHERE Relation = 'Pote'",
                               "Kul Nokh := {}"),
            "bahargam_label": ("SELECT COUNT(DISTINCT Place) FROM Data WHERE Relation IN ('Pote', 'Putra', 'Pita', 'Pautra') AND (Place<>'Vaikunth')",
                               "(bahar)Ketla Gamoma := {}"),
            "vis_varsh_niche_label": ("SELECT COUNT(Name) FROM Data WHERE (julianday('now') - julianday(DoB)) / 365.25 < 20",
                                      "20 Varsh Thi Niche := {}"),
            "varsh_21_40_label": ("SELECT COUNT(Name) FROM Data WHERE (julianday('now') - julianday(DoB)) / 365.25 BETWEEN 21 AND 40 "
                                  "AND Place <> 'Vaikunth' AND NOT (Relation IN ('Putri', 'Pautri', 'Bahen') AND Maritalstatus = 'M')",
                                  "21 to 40 := {}"),
            "varsh_41_60_label": ("SELECT COUNT(Name) FROM Data WHERE (julianday('now') - julianday(DoB)) / 365.25 BETWEEN 41 AND 60 "
                                  "AND Place <> 'Vaikunth' AND NOT (Relation IN ('Putri', 'Pautri', 'Bahen') AND Maritalstatus = 'M')",
                                  "41 to 60 := {}"),
            "varsh_61_80_label": ("SELECT COUNT(Name) FROM Data WHERE (julianday('now') - julianday(DoB)) / 365.25 BETWEEN 61 AND 80 "
                                  "AND Place <> 'Vaikunth' AND NOT (Relation IN ('Putri', 'Pautri', 'Bahen') AND Maritalstatus = 'M')",
                                  "61 to 80 := {}"),
            "varsh_81_100_label": ("SELECT COUNT(Name) FROM Data WHERE (julianday('now') - julianday(DoB)) / 365.25 > 81 "
                                   "AND Place <> 'Vaikunth' AND NOT (Relation IN ('Putri', 'Pautri', 'Bahen') AND Maritalstatus = 'M')",
                                   "81 Upar := {}")}

        for label_id, (query, text_template) in queries.items():
            try:
                conn = sqlite3.connect('Vigodi.db')
                cur = conn.cursor()
                cur.execute(query)
                res = cur.fetchone()[0]
                self.root.ids[label_id].text = text_template.format(res)
            except sqlite3.Error as e:
                print(f"Database error: {e}")

    def on_drawer_state(self, instance, state):
        if state == "open":
            self.layout.remove_widget(self.data_table)
        else:
            self.layout.add_widget(self.data_table)

    def view(self):
        # Get text input values
        name = self.root.ids.txtname.text
        father = self.root.ids.txtfather.text
        mother = self.root.ids.txtmother.text
        grandfather = self.root.ids.txtgrandfather.text
        grandmother = self.root.ids.txtgrandmother.text

        # Fetch data from the database
        data_rows = []
        conn = sqlite3.connect('Vigodi.db')
        cur = conn.cursor()

        try:
            cur.execute("SELECT Name, Father, Mother, Grandfather, Grandmother FROM Data WHERE Name=? AND Father=? AND Mother=? AND Grandfather=? AND Grandmother=?",
                        (name, father, mother, grandfather, grandmother))
            res = cur.fetchone()

            if res:
                data_rows.append(res)
                gopal = res[1]
                parbat = res[3]
                puri = res[4]

                for i in range(25):
                    cur.execute("SELECT Name, Father, Mother, Grandfather, Grandmother FROM Data WHERE Name=? AND Father=? AND Mother=?",
                                (gopal, parbat, puri))
                    additional_res = cur.fetchone()
                    if additional_res:
                        data_rows.append(additional_res)
                        gopal = additional_res[1]
                        parbat = additional_res[3]
                        puri = additional_res[4]
                    else:
                        break
            else:
                self.show_no_data_dialog()

        finally:
            conn.close()

        if data_rows:
            self.data_table.row_data = data_rows
        else:
            self.show_no_data_dialog()

    def show_no_data_dialog(self):
        dialog = MDDialog(title="No Data", text="No matching data found.", size_hint=(0.8, 0.1))
        dialog.open()

Test().run()
