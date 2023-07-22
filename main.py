from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.utils import platform
import numpy as np
import math
import re


class CalculatorKeyboard(GridLayout):
    def __init__(self, operators, last_was_operator, input_box, output_box, **kwargs):
        super(CalculatorKeyboard, self).__init__(**kwargs)
        self.cols = 4
        self.spacing = 10
        self.padding = (10, 10, 10, 10)
        self.size_hint_y = None
        self.height = 300
        self.operators = operators
        self.last_was_operator = last_was_operator
        self.input_box = input_box
        self.output_box = output_box

        buttons = [
            ["np.sum", "np.subtract", "np.sqrt", "np.divide"],
            ["np.multiply", "np.sin", "np.cos", "np.tan"],
            ["7", "8", "9", "C"],
            ["4", "5", "6", "="],
            ["1", "2", "3", "."],
            ["0", "(", ")", ","],
            ["expo", "log", "AC"],  # Add the "AC" button to the calculator keyboard
        ]

        for row in buttons:
            for button_text in row:
                button = Button(text=button_text, font_size=25, background_color=(0.7, 0.7, 0.7, 1))
                button.bind(on_press=self.on_button_press)
                self.add_widget(button)
    
    def on_button_press(self, instance):
        button_text = instance.text
        if button_text == 'C':
            # Delete the last character in the input field
            self.input_box.text = self.input_box.text[:-1]
        elif button_text == 'AC':
            # Clear both input and output fields
            self.input_box.text = ""
            self.output_box.text = ""
        elif button_text == '=':
            # Evaluate the expression and show the result in the output field
            self.calculate_expression()
            self.last_was_operator = False  # Reset the flag after calculating the result
        else:
            self.handle_input(button_text)

    def calculate_expression(self):
        try:
            expression = self.input_box.text
            print("Expression:", expression)
            result = self.eval_input(expression)
            self.output_box.text = str(result)
        except Exception as e:
            self.output_box.text = "Error"

    def handle_input(self, button_text):
        if button_text in self.operators:
            if self.last_was_operator:
                return
            # Replace the operator name with the function call in the input box
            self.input_box.text += button_text + "("
            self.last_was_operator = True
        elif button_text in {"(", ")"}:
            self.input_box.text += button_text
        else:
            self.input_box.text += button_text
            self.last_was_operator = False
    def eval_input(self, expression):
        try:
            # Replace np functions with actual function calls
            converted_exp = re.sub(r'np.([a-zA-Z_]+)\(([^)]+)\)', r'np.\1(\2)', expression)
            print("Converted Expression:", converted_exp)
            result = eval(converted_exp)
    
            # Check if the result is a single-element array and return the scalar value
            if isinstance(result, np.ndarray) and result.size == 1:
                result = result.item()
    
            print("Result:", result)
            return result
        except ZeroDivisionError:
            return "Error: Division by zero"
        except Exception as e:
            # Print the error message for debugging
            print("Error:", str(e))
            return "Error"

class MainApp(App):
    def build(self):
        self.operators = {
            "np.sum": np.sum,
            "np.subtract": np.subtract,
            "np.sqrt": np.sqrt,
            "np.divide": np.divide,
            "np.multiply": np.multiply,
            "np.sin": np.sin,
            "np.cos": np.cos,
            "np.tan": np.tan,
            "expo": np.exp,
            "log": np.log,
            "rand": np.random.rand,
            "power": math.pow
        }
        self.last_was_operator = False

        # Set the size of the app screen
        Window.size = (640, 860)

        main_layout = BoxLayout(orientation="vertical", spacing=10, padding=(10, 10, 10, 10))

        input_width, input_height = 0.9, 1
        output_width, output_height = 0.9, 1

        # Add title label to the main_layout
        title_label = Label(text="Python Calculator", font_size=25, size_hint=(1, None), height=40, color=(1, 1, 1, 1))
        main_layout.add_widget(title_label)

        # Create a horizontal BoxLayout for input label and text input
        input_layout = BoxLayout(size_hint=(1, None), height=60, spacing=10)

        self.input_label = Label(text="Input:", font_size=20, size_hint=(None, None), height=30, color=(1, 1, 1, 1))
        self.input_box = TextInput(
            multiline=False, halign="center", font_size=30, size_hint=(input_width, input_height),
            background_color=(0.7, 0.7, 0.7, 1), use_bubble=True,
            hint_text="Input"  # Placeholder text for the input box
        )

        # Add widgets to the input_layout
        input_layout.add_widget(self.input_label)
        input_layout.add_widget(self.input_box)

        # Create another horizontal BoxLayout for output label and text input
        output_layout = BoxLayout(size_hint=(1, None), height=60, spacing=10)

        self.output_label = Label(text="Output:", font_size=20, size_hint=(None, None), height=30)
        self.output_box = TextInput(
            multiline=False, readonly=True, halign="center", font_size=30, size_hint=(output_width, output_height),
            background_color=(0.7, 0.7, 0.7, 1), hint_text="Output"  # Placeholder text for the output box
        )

        # Add widgets to the output_layout
        output_layout.add_widget(self.output_label)
        output_layout.add_widget(self.output_box)

        # Center the input and output boxes within their respective layouts
        self.input_box.pos_hint = {"center_x": 0.5}
        self.output_box.pos_hint = {"center_x": 0.5}

        # Add both layouts to the main_layout
        main_layout.add_widget(input_layout)
        main_layout.add_widget(output_layout)

        # Add a spacer Widget
        main_layout.add_widget(Widget())

        # Check the platform to decide whether to use native virtual keyboard (Android) or default Kivy keyboard
        if platform == 'android':
            self.input_box.input_type = 'text'
        else:
            # Add the custom CalculatorKeyboard at the bottom end of the screen for non-Android platforms
            keyboard = CalculatorKeyboard(
                operators=self.operators,
                last_was_operator=self.last_was_operator,
                input_box=self.input_box,
                output_box=self.output_box
            )
            main_layout.add_widget(keyboard)

        return main_layout

    def on_start(self):
        # Bind the input_box to on_text_validate method
        self.input_box.bind(on_text_validate=self.on_text_validate)

    def on_text_validate(self, instance):
        # Called when the user presses the 'Enter' key on the keyboard
        expression = instance.text
        try:
            result = self.eval_input(expression)
            self.output_box.text = str(result)
        except Exception as e:
            self.output_box.text = "Error"

    def eval_input(self, expression):
        try:
            # For numpy functions, we need to handle them separately
            if 'np.' in expression:
                # Replace np.sqrt(a) with np.sqrt(a)
                converted_exp = re.sub(r'np.([a-zA-Z_]+)\(([^)]+)\)', r'np.\1([\2])', expression)
                print("Converted Expression:", converted_exp)
                result = eval(converted_exp)
            else:
                result = eval(expression)
            print("Result:", result)
            return result
        except Exception as e:
            # Print the error message for debugging
            print("Error:", str(e))
            return "Error"


if __name__ == "__main__":
    app = MainApp()
    app.run()
