import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import asyncio
from sympy import var, symbols, diff, sympify, E, sin, cos, tan, log, sqrt, exp
import numpy as np
from numpy import pi
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for mobile
import io
import base64

# Import your custom modules (you'll need to include these in your mobile app)
# from interpolation import lagrange, hermitian, cubic
# from ndiff import integrate
# from support import string_to_function

class InterpolationApp(toga.App):
    def startup(self):
        """Initialize the application"""
        self.points = []
        self.derivatives = []
        self.interpolation_type = "lagrange"
        self.current_poly = None
        self.current_func = None
        self.current_spline = None
        
        # Integration variables
        self.integration_type = "single"
        self.integration_method = "simpsons_1/3rd"
        self.integration_results = None
        
        # Create main window
        self.main_window = toga.MainWindow(title=self.formal_name)
        
        # Create main container with tabs
        self.create_main_interface()
        
        self.main_window.content = self.main_container
        self.main_window.show()

    def create_main_interface(self):
        """Create the main interface with tabs"""
        # Create tab container using OptionContainer
        self.tab_container = toga.OptionContainer(
            style=Pack(flex=1, padding=10)
        )
        
        # Create interpolation tab
        self.create_interpolation_tab()
        
        # Create integration tab
        self.create_integration_tab()
        
        # Main container
        self.main_container = toga.Box(
            children=[self.tab_container],
            style=Pack(direction=COLUMN, flex=1)
        )

    def create_interpolation_tab(self):
        """Create the interpolation tab"""
        # Input section
        input_section = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # Interpolation type selection
        type_label = toga.Label(
            "Interpolation Type:",
            style=Pack(padding_bottom=5, font_weight='bold')
        )
        
        self.interp_type_selection = toga.Selection(
            items=["Lagrange", "Hermitian", "Cubic Spline"],
            on_select=self.on_interpolation_type_change,
            style=Pack(padding_bottom=10, width=200)
        )
        
        # Point input section
        points_label = toga.Label(
            "Input Data (comma-separated, supports pi, e, sin, cos, etc.):",
            style=Pack(padding_bottom=5, font_weight='bold')
        )
        
        x_input_label = toga.Label("X values:", style=Pack(padding_bottom=2))
        self.x_input = toga.TextInput(
            placeholder="e.g., 0, pi/2, pi, 3*pi/2",
            style=Pack(padding_bottom=5, width=300)
        )
        
        y_input_label = toga.Label("Y values:", style=Pack(padding_bottom=2))
        self.y_input = toga.TextInput(
            placeholder="e.g., 1, 0, -1, 0",
            style=Pack(padding_bottom=5, width=300)
        )
        
        # Derivative input (initially hidden)
        self.deriv_input_label = toga.Label("Y' values:", style=Pack(padding_bottom=2))
        self.deriv_input = toga.TextInput(
            placeholder="e.g., 0, -1, 0, 1",
            style=Pack(padding_bottom=5, width=300)
        )
        
        # Initially hide derivative input
        self.deriv_input_label.style.display = 'none'
        self.deriv_input.style.display = 'none'
        
        # Buttons
        button_box = toga.Box(style=Pack(direction=ROW, padding=5))
        
        add_points_btn = toga.Button(
            "Add Points",
            on_press=self.add_points,
            style=Pack(padding_right=10)
        )
        
        clear_input_btn = toga.Button(
            "Clear Input",
            on_press=self.clear_input,
            style=Pack(padding_right=10)
        )
        
        calculate_btn = toga.Button(
            "Calculate",
            on_press=self.calculate_interpolation,
            style=Pack(padding_right=10, background_color='#007AFF')
        )
        
        button_box.add(add_points_btn)
        button_box.add(clear_input_btn)
        button_box.add(calculate_btn)
        
        # Points list
        points_label = toga.Label(
            "Current Points:",
            style=Pack(padding_top=10, padding_bottom=5, font_weight='bold')
        )
        
        self.points_list = toga.DetailedList(
            style=Pack(height=150, padding_bottom=10)
        )
        
        # Management buttons
        manage_box = toga.Box(style=Pack(direction=ROW, padding=5))
        
        remove_btn = toga.Button(
            "Remove Selected",
            on_press=self.remove_point,
            style=Pack(padding_right=10)
        )
        
        clear_all_btn = toga.Button(
            "Clear All",
            on_press=self.clear_points,
            style=Pack(padding_right=10)
        )
        
        manage_box.add(remove_btn)
        manage_box.add(clear_all_btn)
        
        # Evaluation section
        eval_label = toga.Label(
            "Evaluate Function:",
            style=Pack(padding_top=10, padding_bottom=5, font_weight='bold')
        )
        
        eval_box = toga.Box(style=Pack(direction=ROW, padding=5))
        
        eval_x_label = toga.Label("x = ", style=Pack(padding_right=5))
        self.eval_input = toga.TextInput(
            placeholder="e.g., pi/4",
            style=Pack(padding_right=10, width=100)
        )
        
        eval_btn = toga.Button(
            "Find Value",
            on_press=self.evaluate_function,
            style=Pack(padding_right=10)
        )
        
        eval_box.add(eval_x_label)
        eval_box.add(self.eval_input)
        eval_box.add(eval_btn)
        
        self.eval_result = toga.Label(
            "Result: ",
            style=Pack(padding_top=5, color='#007AFF', font_weight='bold')
        )
        
        # Results section
        results_label = toga.Label(
            "Results:",
            style=Pack(padding_top=15, padding_bottom=5, font_weight='bold')
        )
        
        self.results_text = toga.MultilineTextInput(
            readonly=True,
            style=Pack(height=200, padding_bottom=10)
        )
        
        # Add all components to input section
        input_section.add(type_label)
        input_section.add(self.interp_type_selection)
        input_section.add(points_label)
        input_section.add(x_input_label)
        input_section.add(self.x_input)
        input_section.add(y_input_label)
        input_section.add(self.y_input)
        input_section.add(self.deriv_input_label)
        input_section.add(self.deriv_input)
        input_section.add(button_box)
        input_section.add(points_label)
        input_section.add(self.points_list)
        input_section.add(manage_box)
        input_section.add(eval_label)
        input_section.add(eval_box)
        input_section.add(self.eval_result)
        input_section.add(results_label)
        input_section.add(self.results_text)
        
        # Create scrollable container
        scroll_container = toga.ScrollContainer(
            content=input_section,
            style=Pack(flex=1)
        )
        
        # Add to tab container
        self.tab_container.add("Interpolation", scroll_container)

    def create_integration_tab(self):
        """Create the integration tab"""
        # Input section
        input_section = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # Integration type selection
        int_type_label = toga.Label(
            "Integration Type:",
            style=Pack(padding_bottom=5, font_weight='bold')
        )
        
        self.int_type_selection = toga.Selection(
            items=["Single Integral", "Double Integral"],
            on_select=self.on_integration_type_change,
            style=Pack(padding_bottom=10, width=200)
        )
        
        # Method selection
        method_label = toga.Label(
            "Integration Method:",
            style=Pack(padding_bottom=5, font_weight='bold')
        )
        
        self.method_selection = toga.Selection(
            items=["Simpson's 1/3", "Trapezoidal", "Simpson's 3/8", "Gaussian", "Romberg"],
            style=Pack(padding_bottom=10, width=200)
        )
        
        # Function input
        func_label = toga.Label(
            "Function f(x) or f(x,y):",
            style=Pack(padding_bottom=2, font_weight='bold')
        )
        
        func_hint = toga.Label(
            "(Use x, y, pi, e, sin, cos, exp, log, sqrt, etc.)",
            style=Pack(padding_bottom=5, font_size=12, color='#666666')
        )
        
        self.function_input = toga.TextInput(
            placeholder="e.g., sin(x), x*y + exp(x)",
            style=Pack(padding_bottom=15, width=300)
        )
        
        # Single integral parameters
        self.single_params_label = toga.Label(
            "Single Integral Parameters:",
            style=Pack(padding_bottom=5, font_weight='bold')
        )
        
        self.single_params_box = toga.Box(style=Pack(direction=COLUMN, padding_bottom=15))
        
        single_row1 = toga.Box(style=Pack(direction=ROW, padding_bottom=5))
        single_row1.add(toga.Label("x₀: ", style=Pack(padding_right=5, width=30)))
        self.x0_input = toga.TextInput(placeholder="0", style=Pack(padding_right=10, width=80))
        single_row1.add(self.x0_input)
        single_row1.add(toga.Label("xₙ: ", style=Pack(padding_right=5, width=30)))
        self.xn_input = toga.TextInput(placeholder="pi", style=Pack(padding_right=10, width=80))
        single_row1.add(self.xn_input)
        single_row1.add(toga.Label("h: ", style=Pack(padding_right=5, width=20)))
        self.h_single_input = toga.TextInput(placeholder="0.1", style=Pack(width=80))
        single_row1.add(self.h_single_input)
        
        self.single_params_box.add(single_row1)
        
        # Double integral parameters
        self.double_params_label = toga.Label(
            "Double Integral Parameters:",
            style=Pack(padding_bottom=5, font_weight='bold')
        )
        
        self.double_params_box = toga.Box(style=Pack(direction=COLUMN, padding_bottom=15))
        
        double_row1 = toga.Box(style=Pack(direction=ROW, padding_bottom=5))
        double_row1.add(toga.Label("x₀: ", style=Pack(padding_right=5, width=30)))
        self.x0_double_input = toga.TextInput(placeholder="0", style=Pack(padding_right=10, width=60))
        double_row1.add(self.x0_double_input)
        double_row1.add(toga.Label("xₙ: ", style=Pack(padding_right=5, width=30)))
        self.xn_double_input = toga.TextInput(placeholder="1", style=Pack(padding_right=10, width=60))
        double_row1.add(self.xn_double_input)
        double_row1.add(toga.Label("h: ", style=Pack(padding_right=5, width=20)))
        self.h_double_input = toga.TextInput(placeholder="0.1", style=Pack(width=60))
        double_row1.add(self.h_double_input)
        
        double_row2 = toga.Box(style=Pack(direction=ROW, padding_top=5))
        double_row2.add(toga.Label("y₀: ", style=Pack(padding_right=5, width=30)))
        self.y0_input = toga.TextInput(placeholder="0", style=Pack(padding_right=10, width=60))
        double_row2.add(self.y0_input)
        double_row2.add(toga.Label("yₙ: ", style=Pack(padding_right=5, width=30)))
        self.yn_input = toga.TextInput(placeholder="1", style=Pack(padding_right=10, width=60))
        double_row2.add(self.yn_input)
        double_row2.add(toga.Label("k: ", style=Pack(padding_right=5, width=20)))
        self.k_input = toga.TextInput(placeholder="0.1", style=Pack(width=60))
        double_row2.add(self.k_input)
        
        self.double_params_box.add(double_row1)
        self.double_params_box.add(double_row2)
        
        # Initially hide double parameters
        self.double_params_label.style.display = 'none'
        self.double_params_box.style.display = 'none'
        
        # Integration buttons
        int_button_box = toga.Box(style=Pack(direction=ROW, padding=10))
        
        calculate_int_btn = toga.Button(
            "Calculate Integration",
            on_press=self.calculate_integration,
            style=Pack(padding_right=10, background_color='#007AFF')
        )
        
        clear_int_btn = toga.Button(
            "Clear All",
            on_press=self.clear_integration,
            style=Pack(padding_right=10)
        )
        
        int_button_box.add(calculate_int_btn)
        int_button_box.add(clear_int_btn)
        
        # Integration results
        int_results_label = toga.Label(
            "Integration Results:",
            style=Pack(padding_top=15, padding_bottom=5, font_weight='bold')
        )
        
        self.integration_results_text = toga.MultilineTextInput(
            readonly=True,
            style=Pack(height=200, padding_bottom=10)
        )
        
        # Array output
        array_label = toga.Label(
            "Array Output:",
            style=Pack(padding_bottom=5, font_weight='bold')
        )
        
        self.array_output_text = toga.MultilineTextInput(
            readonly=True,
            style=Pack(height=150)
        )
        
        # Add all components to input section
        input_section.add(int_type_label)
        input_section.add(self.int_type_selection)
        input_section.add(method_label)
        input_section.add(self.method_selection)
        input_section.add(func_label)
        input_section.add(func_hint)
        input_section.add(self.function_input)
        input_section.add(self.single_params_label)
        input_section.add(self.single_params_box)
        input_section.add(self.double_params_label)
        input_section.add(self.double_params_box)
        input_section.add(int_button_box)
        input_section.add(int_results_label)
        input_section.add(self.integration_results_text)
        input_section.add(array_label)
        input_section.add(self.array_output_text)
        
        # Create scrollable container
        scroll_container = toga.ScrollContainer(
            content=input_section,
            style=Pack(flex=1)
        )
        
        # Add to tab container
        self.tab_container.add("Integration", scroll_container)

    async def on_interpolation_type_change(self, widget):
        """Handle interpolation type change"""
        selected = widget.value
        
        if selected == "Hermitian":
            self.interpolation_type = "hermitian"
            self.deriv_input_label.style.display = 'block'
            self.deriv_input.style.display = 'block'
        else:
            if selected == "Lagrange":
                self.interpolation_type = "lagrange"
            else:
                self.interpolation_type = "spline"
            self.deriv_input_label.style.display = 'none'
            self.deriv_input.style.display = 'none'
        
        self.eval_result.text = "Result: "
        self.update_points_display()

    async def on_integration_type_change(self, widget):
        """Handle integration type change"""
        selected = widget.value
        
        if selected == "Single Integral":
            self.integration_type = "single"
            self.single_params_label.style.display = 'block'
            self.single_params_box.style.display = 'block'
            self.double_params_label.style.display = 'none'
            self.double_params_box.style.display = 'none'
        else:
            self.integration_type = "double"
            self.single_params_label.style.display = 'none'
            self.single_params_box.style.display = 'none'
            self.double_params_label.style.display = 'block'
            self.double_params_box.style.display = 'block'

    async def add_points(self, widget):
        """Add points from comma-separated input"""
        try:
            x_input = self.x_input.value.strip()
            y_input = self.y_input.value.strip()
            
            if not x_input or not y_input:
                await self.main_window.error_dialog("Error", "Please enter both X and Y values")
                return
            
            # Split and convert to float using sympify
            x_values = [float(sympify(x.strip(), locals={'pi': pi, 'e': E})) for x in x_input.split(',') if x.strip()]
            y_values = [float(sympify(y.strip(), locals={'pi': pi, 'e': E})) for y in y_input.split(',') if y.strip()]
            
            if len(x_values) != len(y_values):
                await self.main_window.error_dialog("Error", "Number of X and Y values must be equal")
                return
            
            # Handle derivatives for Hermitian
            if self.interpolation_type == "hermitian":
                deriv_input = self.deriv_input.value.strip()
                if not deriv_input:
                    await self.main_window.error_dialog("Error", "Please enter derivative values for Hermitian interpolation")
                    return
                
                deriv_values = [float(sympify(d.strip(), locals={'pi': pi, 'e': E})) for d in deriv_input.split(',') if d.strip()]
                if len(deriv_values) != len(x_values):
                    await self.main_window.error_dialog("Error", "Number of derivative values must equal number of points")
                    return
                
                # Clear existing derivatives and add new ones
                self.derivatives.clear()
                self.derivatives.extend(deriv_values)
            
            # Clear existing points and add new ones
            self.points.clear()
            for x, y in zip(x_values, y_values):
                self.points.append((x, y))
            
            self.update_points_display()
            
            # Show success message
            await self.main_window.info_dialog("Success", f"Added {len(x_values)} points successfully")
            
        except ValueError:
            await self.main_window.error_dialog("Error", "Please enter valid numeric values or expressions (e.g., 2*pi, e^2, sin(pi/2)) separated by commas")
        except Exception as e:
            await self.main_window.error_dialog("Error", f"Failed to add points: {str(e)}")

    async def clear_input(self, widget):
        """Clear input fields"""
        self.x_input.value = ""
        self.y_input.value = ""
        self.deriv_input.value = ""

    async def remove_point(self, widget):
        """Remove selected point"""
        if self.points_list.selection:
            index = self.points_list.data.index(self.points_list.selection)
            self.points.pop(index)
            if self.interpolation_type == "hermitian" and index < len(self.derivatives):
                self.derivatives.pop(index)
            self.update_points_display()

    async def clear_points(self, widget):
        """Clear all points"""
        self.points.clear()
        self.derivatives.clear()
        self.current_poly = None
        self.current_func = None
        self.current_spline = None
        self.eval_result.text = "Result: "
        self.update_points_display()
        self.results_text.value = ""

    def update_points_display(self):
        """Update the points list display"""
        data = []
        for i, (x, y) in enumerate(self.points):
            if self.interpolation_type == "hermitian" and i < len(self.derivatives):
                title = f"Point {i+1}"
                subtitle = f"({x}, {y}), y'={self.derivatives[i]}"
            else:
                title = f"Point {i+1}"
                subtitle = f"({x}, {y})"
            data.append({"title": title, "subtitle": subtitle})
        
        self.points_list.data = data

    def format_polynomial_clean(self, coeffs):
        """Format polynomial coefficients cleanly"""
        temp = ''
        n = len(coeffs)
        for i in range(n):
            if coeffs[i] != 0:
                temp += f" + {coeffs[i]}*x^{n-i-1}"
        return temp[3:-3] if temp else "0"

    async def calculate_interpolation(self, widget):
        """Calculate and display interpolation"""
        if len(self.points) < 2:
            await self.main_window.error_dialog("Error", "Please enter at least 2 points")
            return
        
        if self.interpolation_type == "hermitian" and len(self.derivatives) != len(self.points):
            await self.main_window.error_dialog("Error", "Please provide derivatives for all points in Hermitian interpolation")
            return
        
        try:
            # Extract x and y values
            x_vals = [p[0] for p in self.points]
            y_vals = [p[1] for p in self.points]
            
            # Check for duplicate x values
            if len(set(x_vals)) != len(x_vals):
                await self.main_window.error_dialog("Error", "Duplicate x values are not allowed")
                return
            
            # Sort points by x value
            sorted_data = sorted(zip(x_vals, y_vals, self.derivatives if self.interpolation_type == "hermitian" else [0]*len(x_vals)))
            x_vals = [d[0] for d in sorted_data]
            y_vals = [d[1] for d in sorted_data]
            if self.interpolation_type == "hermitian":
                self.derivatives = [d[2] for d in sorted_data]
            
            # TODO: Implement actual interpolation calculations
            # You'll need to include your interpolation modules
            
            poly_text = f"Interpolation Type: {self.interpolation_type.title()}\n"
            poly_text += f"Number of points: {len(self.points)}\n\n"
            poly_text += "Data Points:\n"
            
            for i, (x, y) in enumerate(zip(x_vals, y_vals)):
                if self.interpolation_type == "hermitian":
                    poly_text += f"  ({x}, {y}), y'({x}) = {self.derivatives[i]}\n"
                else:
                    poly_text += f"  ({x}, {y})\n"
            
            poly_text += "\nNote: Full interpolation calculation requires the custom modules.\n"
            poly_text += "This is a mobile-friendly interface demo."
            
            self.results_text.value = poly_text
            self.eval_result.text = "Result: "
            
            await self.main_window.info_dialog("Success", f"{self.interpolation_type.title()} interpolation setup complete")
            
        except Exception as e:
            await self.main_window.error_dialog("Error", f"Calculation failed: {str(e)}")

    async def evaluate_function(self, widget):
        """Evaluate the interpolating function at a given point"""
        if not self.current_func and not self.current_spline:
            await self.main_window.error_dialog("Error", "Please calculate interpolation first")
            return
        
        try:
            x_val = float(sympify(self.eval_input.value, locals={'pi': pi, 'e': np.exp(1)}))
            
            # TODO: Implement actual function evaluation
            # For now, show placeholder result
            result = x_val * 2  # Placeholder calculation
            
            self.eval_result.text = f"Result: f({x_val}) = {result:.6f}"
            
        except ValueError:
            await self.main_window.error_dialog("Error", "Please enter a valid numeric value or expression")
        except Exception as e:
            await self.main_window.error_dialog("Error", f"Evaluation failed: {str(e)}")

    async def calculate_integration(self, widget):
        """Calculate numerical integration"""
        try:
            function_str = self.function_input.value.strip()
            if not function_str:
                await self.main_window.error_dialog("Error", "Please enter a function")
                return
            
            method = self.method_selection.value or "Simpson's 1/3"
            method_key = method.lower().replace(" ", "_").replace("'", "")
            
            # Get parameters based on integration type
            if self.integration_type == "single":
                try:
                    x0 = float(sympify(self.x0_input.value, locals={'pi': pi, 'e': E}))
                    xn = float(sympify(self.xn_input.value, locals={'pi': pi, 'e': E}))
                    h = float(sympify(self.h_single_input.value, locals={'pi': pi, 'e': E}))
                    
                    if not all([self.x0_input.value, self.xn_input.value, self.h_single_input.value]):
                        await self.main_window.error_dialog("Error", "Please fill all single integral parameters")
                        return
                    
                    # Display input parameters
                    results_text = f"Single Integration - {method}\n"
                    results_text += f"Function: f(x) = {function_str}\n"
                    results_text += f"Limits: x₀ = {x0}, xₙ = {xn}\n"
                    results_text += f"Step size: h = {h}\n\n"
                    results_text += f"Method: {method}\n"
                    results_text += "\nNote: Full integration calculation requires custom modules.\n"
                    results_text += "This is a mobile-friendly interface demo."
                    
                except ValueError:
                    await self.main_window.error_dialog("Error", "Please enter valid numeric values for single integral parameters")
                    return
                    
            else:  # Double integral
                try:
                    x0 = float(sympify(self.x0_double_input.value, locals={'pi': pi, 'e': E}))
                    xn = float(sympify(self.xn_double_input.value, locals={'pi': pi, 'e': E}))
                    y0 = float(sympify(self.y0_input.value, locals={'pi': pi, 'e': E}))
                    yn = float(sympify(self.yn_input.value, locals={'pi': pi, 'e': E}))
                    h = float(sympify(self.h_double_input.value, locals={'pi': pi, 'e': E}))
                    k = float(sympify(self.k_input.value, locals={'pi': pi, 'e': E}))
                    
                    if not all([self.x0_double_input.value, self.xn_double_input.value, 
                               self.y0_input.value, self.yn_input.value,
                               self.h_double_input.value, self.k_input.value]):
                        await self.main_window.error_dialog("Error", "Please fill all double integral parameters")
                        return
                    
                    # Display input parameters
                    results_text = f"Double Integration - {method}\n"
                    results_text += f"Function: f(x,y) = {function_str}\n"
                    results_text += f"X limits: x₀ = {x0}, xₙ = {xn}, h = {h}\n"
                    results_text += f"Y limits: y₀ = {y0}, yₙ = {yn}, k = {k}\n\n"
                    results_text += f"Method: {method}\n"
                    results_text += "\nNote: Full integration calculation requires custom modules.\n"
                    results_text += "This is a mobile-friendly interface demo."
                    
                except ValueError:
                    await self.main_window.error_dialog("Error", "Please enter valid numeric values for double integral parameters")
                    return
            
            # Display results
            self.integration_results_text.value = results_text
            
            # Placeholder array output
            array_text = "Function values:\n"
            array_text += "Note: Actual array values would be calculated with custom modules.\n"
            array_text += "Sample output format:\n"
            array_text += "f(x₀,y₀) = 1.234\n"
            array_text += "f(x₁,y₀) = 2.345\n"
            array_text += "..."
            
            self.array_output_text.value = array_text
            
            await self.main_window.info_dialog("Success", f"Integration setup complete for {method}")
            
        except Exception as e:
            await self.main_window.error_dialog("Error", f"Integration setup failed: {str(e)}")

    async def clear_integration(self, widget):
        """Clear all integration inputs and results"""
        # Clear input fields
        self.function_input.value = ""
        self.x0_input.value = ""
        self.xn_input.value = ""
        self.h_single_input.value = ""
        self.x0_double_input.value = ""
        self.xn_double_input.value = ""
        self.h_double_input.value = ""
        self.y0_input.value = ""
        self.yn_input.value = ""
        self.k_input.value = ""
        
        # Clear results
        self.integration_results_text.value = ""
        self.array_output_text.value = ""
        
        self.integration_results = None


def main():
    return InterpolationApp(
        'Interpolation & Integration Calculator',
        'org.example.interpolation'
    )


if __name__ == '__main__':
    app = main()
    app.main_loop()