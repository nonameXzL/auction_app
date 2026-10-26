from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
import requests

API_URL = "http://127.0.0.1:8000/api"


# Уведомления (сообщения об ошибках и успехе)
def show_msg(title, text):
    Popup(title=title, content=Label(text=str(text)), size_hint=(0.8, 0.3)).open()


# --- 1. АВТОРИЗАЦИЯ ---
class LoginScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        layout.add_widget(Label(text="Вход в аукцион", font_size=28))

        self.email = TextInput(hint_text="Email", multiline=False, size_hint_y=None, height=50)
        self.password = TextInput(hint_text="Пароль", password=True, multiline=False, size_hint_y=None, height=50)
        layout.add_widget(self.email)
        layout.add_widget(self.password)

        btn = Button(text="Войти", size_hint_y=None, height=50, background_color=(0, 0.7, 1, 1))
        btn.bind(on_press=self.login)
        layout.add_widget(btn)

        btn_reg = Button(text="Регистрация", size_hint_y=None, height=50)
        btn_reg.bind(on_press=lambda x: setattr(self.manager, 'current', 'register'))
        layout.add_widget(btn_reg)
        self.add_widget(layout)

    def login(self, instance):
        try:
            res = requests.post(f"{API_URL}/login", json={"email": self.email.text, "password": self.password.text})
            if res.status_code == 200:
                self.manager.user = res.json()
                self.manager.current = 'main'
            else:
                show_msg("Ошибка", res.json().get('detail', 'Ошибка'))
        except:
            show_msg("Ошибка", "Сервер недоступен")


# --- 2. РЕГИСТРАЦИЯ ---
class RegisterScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        layout.add_widget(Label(text="Регистрация", font_size=28))

        self.name_input = TextInput(hint_text="Имя", multiline=False, size_hint_y=None, height=50)
        self.email_input = TextInput(hint_text="Email", multiline=False, size_hint_y=None, height=50)
        self.password_input = TextInput(hint_text="Пароль", password=True, multiline=False, size_hint_y=None, height=50)
        self.role_spinner = Spinner(text='buyer', values=('buyer', 'seller'), size_hint_y=None, height=50)

        layout.add_widget(self.name_input)
        layout.add_widget(self.email_input)
        layout.add_widget(self.password_input)
        layout.add_widget(self.role_spinner)

        btn = Button(text="Создать аккаунт", size_hint_y=None, height=50, background_color=(0, 0.8, 0, 1))
        btn.bind(on_press=self.register)
        layout.add_widget(btn)

        btn_back = Button(text="Назад", size_hint_y=None, height=50)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'login'))
        layout.add_widget(btn_back)
        self.add_widget(layout)

    def register(self, instance):
        try:
            res = requests.post(f"{API_URL}/register", json={
                "name": self.name_input.text, "email": self.email_input.text,
                "password": self.password_input.text, "role": self.role_spinner.text
            })
            if res.status_code == 200:
                show_msg("Успех", "Аккаунт создан! Войдите.")
                self.manager.current = 'login'
            else:
                show_msg("Ошибка", res.json().get('detail', 'Ошибка'))
        except:
            show_msg("Ошибка", "Сервер недоступен")


# --- 3. ГЛАВНЫЙ ЭКРАН (СПИСОК + ПОИСК) ---
class MainScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        header = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.info_label = Label(text="Лоты", font_size=20)
        header.add_widget(self.info_label)

        btn_notif = Button(text="Уведомления", size_hint_x=0.5, background_color=(0.5, 0.5, 0.5, 1))
        btn_notif.bind(on_press=lambda x: setattr(self.manager, 'current', 'notifications'))
        header.add_widget(btn_notif)

        btn_logout = Button(text="Выход", size_hint_x=0.3, background_color=(1, 0.3, 0.3, 1))
        btn_logout.bind(on_press=self.logout)
        header.add_widget(btn_logout)
        self.layout.add_widget(header)

        search_bar = BoxLayout(size_hint_y=None, height=50, spacing=5)
        self.search_input = TextInput(hint_text="Поиск по названию...", multiline=False)
        search_bar.add_widget(self.search_input)
        btn_search = Button(text="Найти", size_hint_x=0.3, background_color=(0, 0.7, 1, 1))
        btn_search.bind(on_press=lambda x: self.load_lots())
        search_bar.add_widget(btn_search)
        self.layout.add_widget(search_bar)

        self.btn_create = Button(text="+ Создать лот", size_hint_y=None, height=50, background_color=(0, 0.6, 0, 1))
        self.btn_create.bind(on_press=lambda x: setattr(self.manager, 'current', 'create'))
        self.layout.add_widget(self.btn_create)

        self.scroll = ScrollView()
        self.list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        self.scroll.add_widget(self.list_layout)
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)

    def on_enter(self):
        self.btn_create.opacity = 1 if self.manager.user.get('role') == 'seller' else 0
        self.btn_create.disabled = self.manager.user.get('role') != 'seller'
        self.load_lots()

    def load_lots(self):
        self.list_layout.clear_widgets()
        try:
            search_query = self.search_input.text.strip()
            params = {}
            if search_query:
                params['search'] = search_query

            res = requests.get(f"{API_URL}/lots", params=params)
            lots = res.json()

            if not lots:
                self.list_layout.add_widget(Label(text="Ничего не найдено", size_hint_y=None, height=50))
                return

            for lot in lots:
                row = BoxLayout(size_hint_y=None, height=60, spacing=5)
                row.add_widget(Label(text=f"{lot['title']} | {lot['price']} р."))

                btn_open = Button(text="Войти", size_hint_x=0.3)
                btn_open.bind(on_press=lambda x, l=lot: self.open_lot(l))
                row.add_widget(btn_open)

                if self.manager.user.get('role') == 'seller':
                    btn_edit = Button(text="Ред.", size_hint_x=0.2, background_color=(1, 0.8, 0, 1))
                    btn_edit.bind(on_press=lambda x, l=lot: self.open_edit(l))
                    row.add_widget(btn_edit)

                    btn_del = Button(text="Удал.", size_hint_x=0.2, background_color=(1, 0.3, 0.3, 1))
                    btn_del.bind(on_press=lambda x, l=lot: self.delete_lot(l))
                    row.add_widget(btn_del)

                self.list_layout.add_widget(row)
        except Exception as e:
            self.list_layout.add_widget(Label(text=f"Ошибка сервера"))

    def open_lot(self, lot):
        self.manager.current_lot = lot
        self.manager.current = 'detail'

    def open_edit(self, lot):
        self.manager.current_lot = lot
        self.manager.current = 'edit'

    def delete_lot(self, lot):
        def confirm(instance):
            try:
                requests.delete(f"{API_URL}/lots/{lot['id']}")
                popup.dismiss()
                show_msg("Успех", "Запись удалена")
                self.load_lots()
            except:
                show_msg("Ошибка", "Не удалось удалить")

        box = BoxLayout(orientation='vertical', spacing=10, padding=10)
        box.add_widget(Label(text=f"Удалить {lot['title']}?"))
        btn = Button(text="Да, удалить", background_color=(1, 0.3, 0.3, 1))
        btn.bind(on_press=confirm)
        box.add_widget(btn)
        popup = Popup(title="Подтверждение", content=box, size_hint=(0.8, 0.4))
        popup.open()

    def logout(self):
        self.manager.user = {}
        self.manager.current = 'login'


# --- 4. ПРОСМОТР ЗАПИСИ (ДЕТАЛИ + СТАВКА) ---
class LotDetailScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        self.title_label = Label(text="", font_size=24)
        self.price_label = Label(text="", font_size=20, color=(0, 1, 0, 1))
        layout.add_widget(self.title_label)
        layout.add_widget(self.price_label)

        self.bid_input = TextInput(hint_text="Сумма ставки", input_filter='int', multiline=False, size_hint_y=None,
                                   height=50)
        layout.add_widget(self.bid_input)

        btn_bid = Button(text="Сделать ставку", size_hint_y=None, height=50, background_color=(0, 0.7, 1, 1))
        btn_bid.bind(on_press=self.make_bid)
        layout.add_widget(btn_bid)

        btn_back = Button(text="Назад к списку", size_hint_y=None, height=50)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(btn_back)
        self.add_widget(layout)

    def on_enter(self):
        lot = self.manager.current_lot
        self.title_label.text = lot['title']
        self.price_label.text = f"Цена: {lot['price']} (Шаг: {lot['step']})"

    def make_bid(self, instance):
        lot = self.manager.current_lot
        try:
            amount = int(self.bid_input.text)
            res = requests.post(f"{API_URL}/lots/{lot['id']}/bids",
                                json={"amount": amount, "user_id": self.manager.user['id']})
            if res.status_code == 200:
                show_msg("Успех", "Ставка принята!")
                self.manager.current = 'main'
            else:
                show_msg("Ошибка", res.json().get('detail', 'Ошибка'))
        except ValueError:
            show_msg("Ошибка", "Введите число")
        except Exception as e:
            show_msg("Ошибка", str(e))


# --- 5. ЭКРАН РЕДАКТИРОВАНИЯ ---
class EditScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        layout.add_widget(Label(text="Редактирование лота", font_size=24))

        self.title_input = TextInput(hint_text="Название", multiline=False, size_hint_y=None, height=50)
        self.price_input = TextInput(hint_text="Цена", input_filter='int', multiline=False, size_hint_y=None, height=50)
        self.step_input = TextInput(hint_text="Шаг", input_filter='int', multiline=False, size_hint_y=None, height=50)

        layout.add_widget(self.title_input)
        layout.add_widget(self.price_input)
        layout.add_widget(self.step_input)

        btn_save = Button(text="Обновить (PUT)", size_hint_y=None, height=50, background_color=(1, 0.8, 0, 1))
        btn_save.bind(on_press=self.save)
        layout.add_widget(btn_save)

        btn_cancel = Button(text="Отмена", size_hint_y=None, height=50)
        btn_cancel.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(btn_cancel)
        self.add_widget(layout)

    def on_enter(self):
        lot = self.manager.current_lot
        self.title_input.text = lot['title']
        self.price_input.text = str(lot['price'])
        self.step_input.text = str(lot['step'])

    def save(self, instance):
        lot = self.manager.current_lot
        try:
            res = requests.put(f"{API_URL}/lots/{lot['id']}", json={
                "title": self.title_input.text,
                "price": int(self.price_input.text or 0),
                "step": int(self.step_input.text or 0)
            })
            if res.status_code == 200:
                show_msg("Успех", "Лот обновлен")
                self.manager.current = 'main'
            else:
                show_msg("Ошибка", "Не удалось обновить")
        except:
            show_msg("Ошибка", "Сервер недоступен")


# --- 6. ЭКРАН УВЕДОМЛЕНИЙ ---
class NotificationsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text="Уведомления", font_size=24))

        self.scroll = ScrollView()
        self.list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        self.scroll.add_widget(self.list_layout)
        layout.add_widget(self.scroll)

        btn_back = Button(text="Назад", size_hint_y=None, height=50)
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(btn_back)
        self.add_widget(layout)

    def on_enter(self):
        self.list_layout.clear_widgets()
        try:
            notifs = requests.get(f"{API_URL}/users/{self.manager.user['id']}/notifications").json()
            if not notifs:
                self.list_layout.add_widget(Label(text="Уведомлений нет", size_hint_y=None, height=50))
            for n in notifs:
                lbl = Label(text=n['message'], size_hint_y=None, height=50, text_size=(300, None))
                self.list_layout.add_widget(lbl)
        except:
            self.list_layout.add_widget(Label(text="Ошибка загрузки"))


# --- 7. ЭКРАН СОЗДАНИЯ ---
class CreateScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
        layout.add_widget(Label(text="Создание лота", font_size=24))

        self.title_input = TextInput(hint_text="Название", multiline=False, size_hint_y=None, height=50)
        self.price_input = TextInput(hint_text="Начальная цена", input_filter='int', multiline=False, size_hint_y=None,
                                     height=50)
        self.step_input = TextInput(hint_text="Шаг ставки", input_filter='int', multiline=False, size_hint_y=None,
                                    height=50)

        layout.add_widget(self.title_input)
        layout.add_widget(self.price_input)
        layout.add_widget(self.step_input)

        btn_save = Button(text="Опубликовать", size_hint_y=None, height=50, background_color=(0, 0.6, 0, 1))
        btn_save.bind(on_press=self.save)
        layout.add_widget(btn_save)

        btn_cancel = Button(text="Отмена", size_hint_y=None, height=50)
        btn_cancel.bind(on_press=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(btn_cancel)
        self.add_widget(layout)

    def save(self, instance):
        try:
            requests.post(f"{API_URL}/lots", json={
                "title": self.title_input.text, "price": int(self.price_input.text or 0),
                "step": int(self.step_input.text or 0), "seller_id": self.manager.user['id']
            })
            show_msg("Успех", "Лот создан")
            self.manager.current = 'main'
        except:
            show_msg("Ошибка", "Заполните поля")


# --- СБОРКА ПРИЛОЖЕНИЯ ---
class AuctionApp(App):
    def build(self):
        sm = ScreenManager()
        sm.user = {}
        sm.current_lot = {}

        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(LotDetailScreen(name='detail'))
        sm.add_widget(EditScreen(name='edit'))
        sm.add_widget(NotificationsScreen(name='notifications'))
        sm.add_widget(CreateScreen(name='create'))
        return sm


if __name__ == '__main__':
    AuctionApp().run()