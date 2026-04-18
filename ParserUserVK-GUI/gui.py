import dearpygui.dearpygui as dpg
from vk_parser import fucking_parse_vk
import json
import os
import webbrowser

# Constants
CONFIG_FILE = "vk_parser_config.json"
DEFAULT_FONT = "Russia2"  # Основной шрифт для русского языка
DEFAULT_FONT_SIZE = 15

class VKParserGUI:
    def __init__(self):
        self.config = {
            "token": "",
            "cities": "",
            "groups": "",
            "window_size": [700, 500]
        }
        self.load_config()
        dpg.create_context()
        self.setup_font()
        self.create_gui()
    
    def setup_font(self):
        """Установка шрифта Russia.ttf"""
        with dpg.font_registry():
            try:
                self.main_font = dpg.add_font("Russia2.ttf", DEFAULT_FONT_SIZE)
                with dpg.font("Russia2.ttf", 13, default_font=True, tag="Default font") as f:
                    dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
                dpg.bind_font("Default font")
            except Exception as e:
                print(f"Ошибка загрузки шрифта: {e}")
                # Fallback на стандартный шрифт если Russia.ttf не найден
                self.main_font = dpg.add_font("Arial.ttf", DEFAULT_FONT_SIZE)
    
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    for key in self.config:
                        if key in loaded_config:
                            self.config[key] = loaded_config[key]
            except Exception as e:
                print(f"Ошибка загрузки конфига: {e}")
    
    
    def open_url(self):
        webbrowser.open("https://t.me/onevology")
    def start_parsing(self):
        self.config['token'] = dpg.get_value("token_input")
        self.config['cities'] = dpg.get_value("cities_input")
        self.config['groups'] = dpg.get_value("groups_input")
        
        cities = [city.strip() for city in self.config['cities'].split(',') if city.strip()]
        groups = [group.strip() for group in self.config['groups'].split(',') if group.strip()]
        
        if not self.config['token']:
            dpg.set_value("status_text", "Ошибка: Введите токен VK")
            return
        
        if not cities:
            dpg.set_value("status_text", "Ошибка: Введите хотя бы один город")
            return
        
        if not groups:
            dpg.set_value("status_text", "Ошибка: Введите хотя бы одну группу")
            return
        
        dpg.set_value("status_text", "Парсинг начат...")
        
        try:

            result_parse = fucking_parse_vk(cities, groups, self.config['token'])
            dpg.set_value("status_text", f"Результат сохранен в {result_parse}")
        except Exception as e:
            dpg.set_value("status_text", f"Ошибка: {str(e)}")
    
    def create_gui(self):
        with dpg.window(tag="main_window", label="VK Parser", 
                       width=self.config['window_size'][0], 
                       height=self.config['window_size'][1]):
            
            # Меню
            #with dpg.menu_bar():
                #with dpg.menu(label="Подробнее"):
                    #dpg.add_menu_item(label="О программе", callback=lambda: dpg.show_item("about_window"))
            
            # Основной контент
            dpg.add_text("Парсер групп VK", color=(0, 200, 255))
            dpg.add_spacer(height=10)
            
            # Поля ввода
            with dpg.group(horizontal=True):
                dpg.add_text("Токен VK:")
                dpg.add_input_text(tag="token_input", width=400, password=True, 
                                 default_value=self.config['token'])
            
            with dpg.group(horizontal=True):
                dpg.add_text("Города (через запятую)(чтобы парсить все города, укажите -):")
                dpg.add_input_text(tag="cities_input", width=400, 
                                 default_value=self.config['cities'])
            
            with dpg.group(horizontal=True):
                dpg.add_text("Группы (URL через запятую):")
                dpg.add_input_text(tag="groups_input", width=400, 
                                 default_value=self.config['groups'])
            
            dpg.add_spacer(height=20)
            dpg.add_button(label="Начать парсинг", callback=self.start_parsing)
                
            dpg.add_spacer(height=10)
            dpg.add_text(tag="status_text", default_value="Готов к работе")
            
            # Окно "О программе"
            with dpg.window(tag="about_window", label="О программе", show=False, pos=[150, 150]):
                dpg.add_text("VK Парсер v1.0")
                dpg.add_text("Разработано для анализа данных VK")
        
        # Применяем основной шрифт
        dpg.bind_font(self.main_font)
    
    def run(self):
        dpg.create_viewport(
            title='VK Parser',
            width=self.config['window_size'][0],
            height=self.config['window_size'][1],
            min_width=600,
            min_height=400
        )
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)
        dpg.start_dearpygui()
        dpg.destroy_context()

if __name__ == "__main__":
    app = VKParserGUI()
    app.run()