from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from datetime import datetime
import os
import shutil
from collections import OrderedDict

class KebabInventoryApp(App):
    def __init__(self):
        super().__init__()
        self.products = OrderedDict([
            ('کباب کوبیده', 0),
            ('فیله زعفرانی', 0),
            ('فیله ماستی', 0),
            ('با استخوان', 0),
            ('شیشلیک', 0),
            ('برگ', 0),
        ])
        self.initialize_tables()
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.load_data()
    
    def initialize_tables(self):
        self.initial_inventory = self.products.copy()
        self.production = self.products.copy()
        self.shipment = self.products.copy()
        self.returns = self.products.copy()
        self.final_inventory = self.products.copy()
    
    def build(self):
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        return self.create_main_screen()
    
    def create_main_screen(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        title = Label(
            text='سیستم مدیریت موجودی کباب',
            size_hint_y=None,
            height=60,
            font_size='20sp',
            bold=True,
            color=(0.2, 0.4, 0.6, 1)
        )
        layout.add_widget(title)
        
        date_label = Label(
            text=f'تاریخ: {self.current_date}',
            size_hint_y=None,
            height=40,
            font_size='16sp'
        )
        layout.add_widget(date_label)
        
        buttons = [
            ('ثبت موجودی اولیه', self.show_initial_inventory),
            ('ثبت تولیدات', self.show_production),
            ('ثبت ارسالی‌ها', self.show_shipment),
            ('ثبت مرجوعی', self.show_returns),
            ('نمایش گزارش کامل', self.show_full_report),
            ('ذخیره داده‌ها', self.save_data),
            ('خروجی HTML', self.export_to_html),
            ('بازیابی اضطراری', self.emergency_recovery),
            ('خروج', self.exit_app)
        ]
        
        for text, callback in buttons:
            btn = Button(
                text=text,
                size_hint_y=None,
                height=60,
                font_size='16sp',
                background_color=(0.3, 0.6, 0.9, 1)
            )
            btn.bind(on_press=callback)
            layout.add_widget(btn)
        
        return layout

    def show_initial_inventory(self, instance=None):
        self.root.clear_widgets()
        self.root.add_widget(self.create_input_screen("ثبت موجودی اولیه", self.initial_inventory))
    
    def show_production(self, instance=None):
        self.root.clear_widgets()
        self.root.add_widget(self.create_input_screen("ثبت تولیدات", self.production))
    
    def show_shipment(self, instance=None):
        self.root.clear_widgets()
        self.root.add_widget(self.create_input_screen("ثبت ارسالی‌ها", self.shipment))
    
    def show_returns(self, instance=None):
        self.root.clear_widgets()
        self.root.add_widget(self.create_input_screen("ثبت مرجوعی", self.returns))
    
    def create_input_screen(self, title, table_data):
        layout = ScrollView()
        grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        title_label = Label(
            text=title,
            size_hint_y=None,
            height=60,
            font_size='20sp',
            bold=True
        )
        grid.add_widget(title_label)
        
        self.input_fields = {}
        for product, current_value in table_data.items():
            product_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=60)
            
            label = Label(
                text=f'{product}:',
                size_hint_x=0.5,
                font_size='16sp'
            )
            
            input_field = TextInput(
                text=str(current_value),
                size_hint_x=0.3,
                font_size='16sp',
                multiline=False,
                input_filter='int'
            )
            self.input_fields[product] = input_field
            
            product_layout.add_widget(label)
            product_layout.add_widget(input_field)
            grid.add_widget(product_layout)
        
        save_btn = Button(
            text='ذخیره',
            size_hint_y=None,
            height=70,
            font_size='18sp',
            background_color=(0.2, 0.8, 0.2, 1)
        )
        save_btn.bind(on_press=lambda x: self.save_input_data(table_data))
        grid.add_widget(save_btn)
        
        back_btn = Button(
            text='بازگشت',
            size_hint_y=None,
            height=60,
            font_size='16sp'
        )
        back_btn.bind(on_press=lambda x: self.show_main_screen())
        grid.add_widget(back_btn)
        
        layout.add_widget(grid)
        return layout
    
    def save_input_data(self, table_data):
        try:
            for product, input_field in self.input_fields.items():
                value = input_field.text.strip()
                if value:
                    table_data[product] = int(value)
            
            self.calculate_final_inventory()
            self.show_message('داده‌ها با موفقیت ذخیره شد')
        except ValueError:
            self.show_message('لطفاً فقط عدد وارد کنید')
    
    def calculate_final_inventory(self):
        for product in self.products:
            self.final_inventory[product] = (
                self.initial_inventory[product] +
                self.production[product] +
                self.returns[product] -
                self.shipment[product]
            )
    
    def show_full_report(self, instance=None):
        layout = ScrollView()
        grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        title = Label(
            text='گزارش کامل موجودی',
            size_hint_y=None,
            height=60,
            font_size='20sp',
            bold=True
        )
        grid.add_widget(title)
        
        tables = [
            ('موجودی اولیه', self.initial_inventory),
            ('تولیدات', self.production),
            ('ارسالی‌ها', self.shipment),
            ('مرجوعی', self.returns)
        ]
        
        for table_name, table_data in tables:
            grid.add_widget(Label(
                text=f'{table_name}',
                size_hint_y=None,
                height=40,
                font_size='16sp',
                bold=True
            ))
            
            for product, value in table_data.items():
                grid.add_widget(Label(
                    text=f'{product}: {value} سیخ',
                    size_hint_y=None,
                    height=40,
                    font_size='14sp'
                ))
        
        grid.add_widget(Label(
            text='موجودی نهائی:',
            size_hint_y=None,
            height=50,
            font_size='18sp',
            bold=True,
            color=(0.2, 0.6, 0.2, 1)
        ))
        
        total = 0
        for product, value in self.final_inventory.items():
            color = (0.2, 0.8, 0.2, 1) if value >= 0 else (0.8, 0.2, 0.2, 1)
            status = '✅' if value >= 0 else '❌'
            grid.add_widget(Label(
                text=f'{status} {product}: {value} سیخ',
                size_hint_y=None,
                height=40,
                font_size='14sp',
                color=color
            ))
            total += value
        
        grid.add_widget(Label(
            text=f'جمع کل: {total} سیخ',
            size_hint_y=None,
            height=50,
            font_size='16sp',
            bold=True,
            color=(0.3, 0.5, 0.8, 1)
        ))
        
        back_btn = Button(
            text='بازگشت',
            size_hint_y=None,
            height=60,
            font_size='16sp'
        )
        back_btn.bind(on_press=lambda x: self.show_main_screen())
        grid.add_widget(back_btn)
        
        layout.add_widget(grid)
        self.root.clear_widgets()
        self.root.add_widget(layout)
    
    def save_data(self, instance=None):
        try:
            with open('kebab_inventory.txt', 'w', encoding='utf-8') as f:
                f.write(f"DATE:{self.current_date}\n")
                for product, value in self.initial_inventory.items():
                    f.write(f"INIT:{product}:{value}\n")
                for product, value in self.production.items():
                    f.write(f"PROD:{product}:{value}\n")
                for product, value in self.shipment.items():
                    f.write(f"SHIP:{product}:{value}\n")
                for product, value in self.returns.items():
                    f.write(f"RET:{product}:{value}\n")
            
            self.show_message('داده‌ها با موفقیت ذخیره شد')
        except Exception as e:
            self.show_message(f'خطا در ذخیره‌سازی: {e}')
    
    def load_data(self):
        try:
            if os.path.exists('kebab_inventory.txt'):
                with open('kebab_inventory.txt', 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('DATE:'):
                            self.current_date = line.strip().split(':')[1]
                        elif line.startswith('INIT:'):
                            parts = line.strip().split(':')
                            if len(parts) >= 3:
                                self.initial_inventory[parts[1]] = int(parts[2])
                        elif line.startswith('PROD:'):
                            parts = line.strip().split(':')
                            if len(parts) >= 3:
                                self.production[parts[1]] = int(parts[2])
                        elif line.startswith('SHIP:'):
                            parts = line.strip().split(':')
                            if len(parts) >= 3:
                                self.shipment[parts[1]] = int(parts[2])
                        elif line.startswith('RET:'):
                            parts = line.strip().split(':')
                            if len(parts) >= 3:
                                self.returns[parts[1]] = int(parts[2])
                
                self.calculate_final_inventory()
        except:
            pass
    
    def export_to_html(self, instance=None):
        try:
            html_content = f"""<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <title>گزارش موجودی کباب</title>
    <style>
        body {{ font-family: Tahoma; direction: rtl; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid black; padding: 8px; text-align: center; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>گزارش موجودی کباب - {self.current_date}</h1>
    <table>
        <tr><th>محصول</th><th>موجودی اولیه</th><th>تولیدات</th><th>ارسالی‌ها</th><th>مرجوعی</th><th>موجودی نهائی</th></tr>"""
            
            for product in self.products:
                final = self.final_inventory[product]
                html_content += f"""
        <tr>
            <td>{product}</td>
            <td>{self.initial_inventory[product]}</td>
            <td>{self.production[product]}</td>
            <td>{self.shipment[product]}</td>
            <td>{self.returns[product]}</td>
            <td>{final}</td>
        </tr>"""
            
            html_content += """
    </table>
</body>
</html>"""
            
            with open('inventory_report.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.show_message('گزارش HTML ایجاد شد')
        except Exception as e:
            self.show_message(f'خطا در ایجاد گزارش: {e}')
    
    def emergency_recovery(self, instance=None):
        try:
            if os.path.exists('kebab_inventory.txt'):
                self.load_data()
                self.show_message('بازیابی با موفقیت انجام شد')
            else:
                self.show_message('فایل داده‌ای پیدا نشد')
        except Exception as e:
            self.show_message(f'خطا در بازیابی: {e}')
    
    def show_message(self, message):
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_layout.add_widget(Label(text=message, font_size='16sp'))
        
        ok_btn = Button(text='باشه', size_hint_y=None, height=50)
        popup_layout.add_widget(ok_btn)
        
        popup = Popup(
            title='پیام سیستم',
            content=popup_layout,
            size_hint=(0.8, 0.4)
        )
        ok_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_main_screen(self, instance=None):
        self.root.clear_widgets()
        self.root.add_widget(self.create_main_screen())
    
    def exit_app(self, instance=None):
        self.stop()

if __name__ == '__main__':
    KebabInventoryApp().run()
