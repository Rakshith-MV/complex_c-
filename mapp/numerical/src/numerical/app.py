import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import asyncio
from sympy import var, symbols, diff, sympify, E, sin, cos, tan, log, sqrt, exp
import numpy as np
from numpy import pi

# Simplified version without custom imports for testing
# Add your interpolation, ndiff, and support modules later

class numerical(toga.App):
    def startup(self):
        """Initialize the application"""
        self.points = []
        self.derivatives = []
        self.interpolation_type = "lagrange"
        self.current_poly = None
        self.current_func = None
        
        # Integration variables
        self.integration_type = "single"
        self.integration_method = "simpsons_1/3rd"
        
        # Create main window
        self.main_window = toga.MainWindow(title=self.formal_name)
        
        # Create main interface
        self.create_main_interface()
        
        self.main_window.content = self.main_container
        self.main_window.show()

    def create_main_interface(self):
        """Create the main interface"""
        # Main container
        self.main_container = toga.Box(
            style=Pack(direction=COLUMN, flex=1, padding=10)
        )
        
        # Create header
        header = toga.Label(
            "Interpolation & Integration Calculator",
            style=Pack(padding_bottom=20, text_align='center', font_size=18, font_weight='bold')
        )
        
        # Create tab selection
        self.create_tab_selection()
        
        # Create content area
        self.content_area = toga.Box(style=Pack(direction=COLUMN, flex=1))
        
        # Add components to main container
        self.main_container.add(header)
        self.main_container.add(self.tab_selection_box)
        self.main_container.add(self.content_area)
        
        # Show interpolation tab by default
        self.show_interpolation_tab()

    def create_tab_selection(self):
        """Create tab selection buttons"""
        self.tab_selection_box = toga.Box(
            style=Pack(direction=ROW, padding_bottom=20)
        )
        
        self.interp_tab_btn = toga.Button(
            "Interpolation",
            on_press=self.show_interpolation_tab,
            style=Pack(flex=1, padding_right=10, background_color='#007AFF')
        )
        
        self.integration_tab_btn = toga.Button(
            "Integration",
            on_press=self.show_integration_tab,
            style=Pack(flex=1, background_color='#666666')
        )
        
        self.tab_selection_box.add(self.interp_tab_btn)
        self.tab_selection_box.add(self.integration_tab_btn)

    async def show_interpolation_tab(self, widget=None):
        """Show interpolation tab"""
        # Update button colors
        self.interp_tab_btn.style.background_color = '#007AFF'
        self.integration_tab_btn.style.background_color = '#666666'
        
        # Clear content area
        self.content_area.clear()
        
        # Create interpolation content
        self.create_interpolation_content()

    async def show_integration_tab(self, widget=None):
        """Show integration tab"""
        # Update button colors
        self.interp_tab_btn.style.background_color = '#666666'
        self.integration_tab_btn.style.background_color = '#007AFF'
        
        # Clear content area
        self.content_area.clear()
        
        # Create integration content
        self.create_integration_content()

    def create_interpolation_content(self):
        """Create interpolation tab content"""
        # Scrollable container
        scroll_container = toga.ScrollContainer(style=Pack(flex=1))
        content_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # Interpolation type selection
        type_label = toga.Label(
            "Interpolation Type:",
            style=Pack(padding_bottom=10, font_weight='bold')
        )
        
        type_selection_box = toga.Box(style=Pack(direction=ROW, padding_bottom=15))
        
        self.lagrange_btn = toga.Button(
            "Lagrange",
            on_press=self.select_lagrange,
            style=Pack(padding_right=10, background_color='#007AFF')
        )
        
        self.hermitian_btn = toga.Button(
            "Hermitian",
            on_press=self.select_hermitian,
            style=Pack(padding_right=10, background_color='#666666')
        )
        
        self.spline_btn = toga.Button(
            "Cubic Spline",
            on_press=self.select_spline,
            style=Pack(background_color='#666666')
        )
        
        type_selection_box.add(self.lagrange_btn)
        type_selection_box.add(self.hermitian_btn)
        type_selection_box.add(self.spline_btn)
        
        # Point input section
        points_label = toga.Label(
            "Input Data (comma-separated):",
            style=Pack(padding_bottom=5, font_weight='bold')
        )
        
        # X values
        x_label = toga.Label("X values:", style=Pack(padding_bottom=5))
        self.x_input = toga.TextInput(
            placeholder="e.g., 0, 1, 2, 3",
            style=Pack(padding_bottom=10)
        )
        
        # Y values
        y_label = toga.Label("Y values:", style=Pack(padding_bottom=5))
        self.y_input = toga.TextInput(
            placeholder="e.g., 1, 4, 9, 16",
            style=Pack(padding_bottom=10)
        )
        
        # Derivative input (initially hidden)
        self.deriv_label = toga.Label("Y' values:", style=Pack(padding_bottom=5))
        self.deriv_input = toga.TextInput(
            placeholder="e.g., 2, 4, 6, 8",
            style=Pack(padding_bottom=10)
        )
        
        # Initially hide derivative input
        self.deriv_label.style.visibility = 'hidden'
        self.deriv_input.style.visibility = 'hidden'
        
        # Buttons
        button_box = toga.Box(style=Pack(direction=ROW, padding_bottom=15))
        
        add_btn = toga.Button(
            "Add Points",
            on_press=self.add_points,
            style=Pack(padding_right=10, background_color='#28A745')
        )
        
        clear_btn = toga.Button(
            "Clear Input",
            on_press=self.clear_input,
            style=Pack(padding_right=10)
        )
        
        calc_btn = toga.Button(
            "Calculate",
            on_press=self.calculate_interpolation,
            style=Pack(background_color='#DC3545')
        )
        
        button_box.add(add_btn)
        button_box.add(clear_btn)
        button_box.add(calc_btn)
        
        # Points display
        points_display_label = toga.Label(
            "Current Points:",
            style=Pack(padding_bottom=5, font_weight='bold')
        )
        
        self.points_display = toga.MultilineTextInput(
            readonly=True,
            style=Pack(height=100, padding_bottom=15)
        )
        
        # Evaluation section
        eval_label = toga.Label(
            "Evaluate Function:",
            style=Pack(padding_bottom=5, font_weight='bold')
        )
        
        eval_box = toga.Box(style=Pack(direction=ROW, padding_bottom=10))
        
        eval_x_label = toga.Label("x = ", style=Pack(padding_right=5))
        self.eval_input = toga.TextInput(
            placeholder="e.g., 2.5",
            style=Pack(padding_right=10, width=100)
        )
        
        eval_btn = toga.Button(
            "Find Value",
            on_press=self.evaluate_function,
            style=Pack()
        )
        
        eval_box.add(eval_x_label)
        eval_box.add(self.eval_input)
        eval_box.add(eval_btn)
        
        self.eval_result = toga.Label(
            "Result: ",
            style=Pack(padding_bottom=15, color='#007AFF', font_weight='bold')
        )
        
        # Results
        results_label = toga.Label(
            "Results:",
            style=Pack(padding_bottom=5, font_weight='bold')
        )
        
        self.results_text = toga.MultilineTextInput(
            readonly=True,
            style=Pack(height=200)
        )
        
        # Add all components
        content_box.add(type_label)
        content_box.add(type_selection_box)
        content_box.add(points_label)
        content_box.add(x_label)
        content_box.add(self.x_input)
        content_box.add(y_label)
        content_box.add(self.y_input)
        content_box.add(self.deriv_label)
        content_box.add(self.deriv_input)
        content_box.add(button_box)
        content_box.add(points_display_label)
        content_box.add(self.points_display)
        content_box.add(eval_label)
        content_box.add(eval_box)
        content_box.add(self.eval_result)
        content_box.add(results_label)
        content_box.add(self.results_text)
        
        scroll_container.content = content_box
        self.content_area.add(scroll_container)

    def create_integration_content(self):
        """Create integration tab content"""
        # Scrollable container
        scroll_container = toga.ScrollContainer(style=Pack(flex=1))
        content_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # Integration type selection
        type_label = toga.Label(
            "Integration Type:",
            style=Pack(padding_bottom=10, font_weight='bold')
        )
        
        type_box = toga.Box(style=Pack(direction=ROW, padding_bottom=15))
        
        self.single_int_btn = toga.Button(
            "Single Integral",
            on_press=self.select_single_integral,
            style=Pack(padding_right=10, background_color='#007AFF')
        )
        
        self.double_int_btn = toga.Button(
            "Double Integral",
            on_press=self.select_double_integral,
            style=Pack(background_color='#666666')
        )
        
        type_box.add(self.single_int_btn)
        type_box.add(self.double_int_btn)
        
        # Method selection
        method_label = toga.Label(
            "Integration Method:",
            style=Pack(padding_bottom=10, font_weight='bold')
        )
        
        method_box = toga.Box(style=Pack(direction=ROW, padding_bottom=15))
        
        self.simpson_btn = toga.Button(
            "Simpson's 1/3",
            on_press=self.select_simpson,
            style=Pack(padding_right=5, background_color='#007AFF', flex=1)
        )
        
        self.trap_btn = toga.Button(
            "Trapezoidal",
            on_press=self.select_trapezoidal,
            style=Pack(padding_right=5, background_color='#666666', flex=1)
        )
        
        self.gauss_btn = toga.Button(
            "Gaussian",
            on_press=self.select_gaussian,
            style=Pack(background_color='#666666', flex=1)
        )
        
        method_box.add(self.simpson_btn)
        method_box.add(self.trap_btn)
        method_box.add(self.gauss_btn)
        
        # Function input
        func_label = toga.Label(
            "Function f(x) or f(x,y):",
            style=Pack(padding_bottom=5, font_weight='bold')
        )
        
        self.function_input = toga.TextInput(
            placeholder="e.g., x^2, sin(x), x*y + exp(x)",
            style=Pack(padding_bottom=15)
        )
        
        # Parameters section
        params_label = toga.Label(
            "Parameters:",
            style=Pack(padding_bottom=10, font_weight='bold')
        )
        
        # Single integral parameters (shown by default)
        self.single_params_box = toga.Box(style=Pack(direction=COLUMN, padding_bottom=15))
        
        single_row1 = toga.Box(style=Pack(direction=ROW, padding_bottom=10))
        single_row1.add(toga.Label("x₀: ", style=Pack(padding_right=5, width=30)))
        self.x0_input = toga.TextInput(placeholder="0", style=Pack(padding_right=10, width=80))
        single_row1.add(self.x0_input)
        single_row1.add(toga.Label("xₙ: ", style=Pack(padding_right=5, width=30)))
        self.xn_input = toga.TextInput(placeholder="1", style=Pack(padding_right=10, width=80))
        single_row1.add(self.xn_input)
        single_row1.add(toga.Label("h: ", style=Pack(padding_right=5, width=20)))
        self.h_input = toga.TextInput(placeholder="0.1", style=Pack(width=80))
        single_row1.add(self.h_input)
        
        self.single_params_box.add(single_row1)
        
        # Double integral parameters (initially hidden)
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
        self.double_params_box.style.visibility = 'hidden'
        
        # Calculate button
        calc_int_btn = toga.Button(
            "Calculate Integration",
            on_press=self.calculate_integration,
            style=Pack(padding_bottom=15, background_color='#DC3545')
        )
        
        # Results
        results_label = toga.Label(
            "Results:",
            style=Pack(padding_bottom=5, font_weight='bold')
        )
        
        self.integration_results = toga.MultilineTextInput(
            readonly=True,
            style=Pack(height=200)
        )
        
        # Add all components
        content_box.add(type_label)
        content_box.add(type_box)
        content_box.add(method_label)
        content_box.add(method_box)
        content_box.add(func_label)
        content_box.add(self.function_input)
        content_box.add(params_label)
        content_box.add(self.single_params_box)
        content_box.add(self.double_params_box)
        content_box.add(calc_int_btn)
        content_box.add(results_label)
        content_box.add(self.integration_results)
        
        scroll_container.content = content_box
        self.content_area.add(scroll_container)

    # Interpolation type selection methods
    async def select_lagrange(self, widget):
        self.interpolation_type = "lagrange"
        self.lagrange_btn.style.background_color = '#007AFF'
        self.hermitian_btn.style.background_color = '#666666'
        self.spline_btn.style.background_color = '#666666'
        self.deriv_label.style.visibility = 'hidden'
        self.deriv_input.style.visibility = 'hidden'

    async def select_hermitian(self, widget):
        self.interpolation_type = "hermitian"
        self.lagrange_btn.style.background_color = '#666666'
        self.hermitian_btn.style.background_color = '#007AFF'
        self.spline_btn.style.background_color = '#666666'
        self.deriv_label.style.visibility = 'visible'
        self.deriv_input.style.visibility = 'visible'

    async def select_spline(self, widget):
        self.interpolation_type = "spline"
        self.lagrange_btn.style.background_color = '#666666'
        self.hermitian_btn.style.background_color = '#666666'
        self.spline_btn.style.background_color = '#007AFF'
        self.deriv_label.style.visibility = 'hidden'
        self.deriv_input.style.visibility = 'hidden'

    # Integration type selection methods
    async def select_single_integral(self, widget):
        self.integration_type = "single"
        self.single_int_btn.style.background_color = '#007AFF'
        self.double_int_btn.style.background_color = '#666666'
        self.single_params_box.style.visibility = 'visible'
        self.double_params_box.style.visibility = 'hidden'

    async def select_double_integral(self, widget):
        self.integration_type = "double"
        self.single_int_btn.style.background_color = '#666666'
        self.double_int_btn.style.background_color = '#007AFF'
        self.single_params_box.style.visibility = 'hidden'
        self.double_params_box.style.visibility = 'visible'

    # Integration method selection
    async def select_simpson(self, widget):
        self.integration_method = "simpsons_1/3rd"
        self.simpson_btn.style.background_color = '#007AFF'
        self.trap_btn.style.background_color = '#666666'
        self.gauss_btn.style.background_color = '#666666'

    async def select_trapezoidal(self, widget):
        self.integration_method = "trapezoidal"
        self.simpson_btn.style.background_color = '#666666'
        self.trap_btn.style.background_color = '#007AFF'
        self.gauss_btn.style.background_color = '#666666'

    async def select_gaussian(self, widget):
        self.integration_method = "gaussian"
        self.simpson_btn.style.background_color = '#666666'
        self.trap_btn.style.background_color = '#666666'
        self.gauss_btn.style.background_color = '#007AFF'

    async def add_points(self, widget):
        """Add points from input"""
        try:
            x_input = self.x_input.value.strip()
            y_input = self.y_input.value.strip()
            
            if not x_input or not y_input:
                await self.main_window.error_dialog("Error", "Please enter both X and Y values")
                return
            
            # Parse input
            x_values = [float(sympify(x.strip(), locals={'pi': pi, 'e': E})) for x in x_input.split(',')]
            y_values = [float(sympify(y.strip(), locals={'pi': pi, 'e': E})) for y in y_input.split(',')]
            
            if len(x_values) != len(y_values):
                await self.main_window.error_dialog("Error", "Number of X and Y values must be equal")
                return
            
            # Handle derivatives for Hermitian
            if self.interpolation_type == "hermitian":
                deriv_input = self.deriv_input.value.strip()
                if not deriv_input:
                    await self.main_window.error_dialog("Error", "Please enter derivative values")
                    return
                
                deriv_values = [float(sympify(d.strip(), locals={'pi': pi, 'e': E})) for d in deriv_input.split(',')]
                if len(deriv_values) != len(x_values):
                    await self.main_window.error_dialog("Error", "Number of derivative values must equal number of points")
                    return
                
                self.derivatives = deriv_values
            
            # Store points
            self.points = list(zip(x_values, y_values))
            self.update_points_display()
            
            await self.main_window.info_dialog("Success", f"Added {len(x_values)} points")
            
        except Exception as e:
            await self.main_window.error_dialog("Error", f"Failed to add points: {str(e)}")

    async def clear_input(self, widget):
        """Clear input fields"""
        self.x_input.value = ""
        self.y_input.value = ""
        self.deriv_input.value = ""

    def update_points_display(self):
        """Update points display"""
        if not self.points:
            self.points_display.value = "No points added yet"
            return
        
        display_text = ""
        for i, (x, y) in enumerate(self.points):
            if self.interpolation_type == "hermitian" and i < len(self.derivatives):
                display_text += f"Point {i+1}: ({x}, {y}), y'={self.derivatives[i]}\n"
            else:
                display_text += f"Point {i+1}: ({x}, {y})\n"
        
        self.points_display.value = display_text

    async def calculate_interpolation(self, widget):
        """Calculate interpolation"""
        if len(self.points) < 2:
            await self.main_window.error_dialog("Error", "Please add at least 2 points")
            return
        
        try:
            result_text = f"Interpolation Type: {self.interpolation_type.title()}\n"
            result_text += f"Number of points: {len(self.points)}\n\n"
            
            # Sort points by x value
            sorted_points = sorted(self.points, key=lambda p: p[0])
            x_vals = [p[0] for p in sorted_points]
            y_vals = [p[1] for p in sorted_points]
            
            # Check for duplicate x values
            if len(set(x_vals)) != len(x_vals):
                await self.main_window.error_dialog("Error", "Duplicate x values not allowed")
                return
            
            result_text += "Data Points:\n"
            for i, (x, y) in enumerate(sorted_points):
                if self.interpolation_type == "hermitian" and i < len(self.derivatives):
                    result_text += f"  ({x}, {y}), y'({x}) = {self.derivatives[i]}\n"
                else:
                    result_text += f"  ({x}, {y})\n"
            
            result_text += f"\n{self.interpolation_type.title()} interpolation calculated successfully!\n"
            result_text += "\nNote: Full mathematical calculation requires custom modules.\n"
            result_text += "This is a mobile interface demo.\n"
            
            self.results_text.value = result_text
            
            # Store for evaluation
            self.sorted_points = sorted_points
            
            await self.main_window.info_dialog("Success", f"{self.interpolation_type.title()} interpolation complete")
            
        except Exception as e:
            await self.main_window.error_dialog("Error", f"Calculation failed: {str(e)}")

    async def evaluate_function(self, widget):
        """Evaluate interpolating function at a point"""
        if not hasattr(self, 'sorted_points') or not self.sorted_points:
            await self.main_window.error_dialog("Error", "Please calculate interpolation first")
            return
        
        try:
            x_val = float(sympify(self.eval_input.value.strip(), locals={'pi': pi, 'e': np.exp(1)}))
            
            # Simple linear interpolation for demo (replace with actual interpolation)
            x_vals = [p[0] for p in self.sorted_points]
            y_vals = [p[1] for p in self.sorted_points]
            
            if x_val < min(x_vals) or x_val > max(x_vals):
                result = "Extrapolation: " + str(np.interp(x_val, x_vals, y_vals))
            else:
                result = np.interp(x_val, x_vals, y_vals)
            
            self.eval_result.text = f"Result: f({x_val}) = {result:.6f}"
            
        except Exception as e:
            await self.main_window.error_dialog("Error", f"Evaluation failed: {str(e)}")

    async def calculate_integration(self, widget):
        """Calculate numerical integration"""
        try:
            function_str = self.function_input.value.strip()
            if not function_str:
                await self.main_window.error_dialog("Error", "Please enter a function")
                return
            
            if self.integration_type == "single":
                # Get single integral parameters
                if not all([self.x0_input.value, self.xn_input.value, self.h_input.value]):
                    await self.main_window.error_dialog("Error", "Please fill all parameters")
                    return
                
                try:
                    x0 = float(sympify(self.x0_input.value, locals={'pi': pi, 'e': E}))
                    xn = float(sympify(self.xn_input.value, locals={'pi': pi, 'e': E}))
                    h = float(sympify(self.h_input.value, locals={'pi': pi, 'e': E}))
                except ValueError:
                    await self.main_window.error_dialog("Error", "Invalid parameter values")
                    return
                
                result_text = f"Single Integration - {self.integration_method.replace('_', ' ').title()}\n"
                result_text += f"Function: f(x) = {function_str}\n"
                result_text += f"Limits: x₀ = {x0}, xₙ = {xn}\n"
                result_text += f"Step size: h = {h}\n"
                result_text += f"Number of intervals: {int((xn - x0) / h)}\n\n"
                
            else:  # Double integral
                # Get double integral parameters
                required_inputs = [
                    self.x0_double_input.value, self.xn_double_input.value,
                    self.y0_input.value, self.yn_input.value,
                    self.h_double_input.value, self.k_input.value
                ]
                
                if not all(required_inputs):
                    await self.main_window.error_dialog("Error", "Please fill all parameters")
                    return
                
                try:
                    x0 = float(sympify(self.x0_double_input.value, locals={'pi': pi, 'e': E}))
                    xn = float(sympify(self.xn_double_input.value, locals={'pi': pi, 'e': E}))
                    y0 = float(sympify(self.y0_input.value, locals={'pi': pi, 'e': E}))
                    yn = float(sympify(self.yn_input.value, locals={'pi': pi, 'e': E}))
                    h = float(sympify(self.h_double_input.value, locals={'pi': pi, 'e': E}))
                    k = float(sympify(self.k_input.value, locals={'pi': pi, 'e': E}))
                except ValueError:
                    await self.main_window.error_dialog("Error", "Invalid parameter values")
                    return
                
                result_text = f"Double Integration - {self.integration_method.replace('_', ' ').title()}\n"
                result_text += f"Function: f(x,y) = {function_str}\n"
                result_text += f"X limits: x₀ = {x0}, xₙ = {xn}, h = {h}\n"
                result_text += f"Y limits: y₀ = {y0}, yₙ = {yn}, k = {k}\n"
                result_text += f"Grid size: {int((xn-x0)/h)} × {int((yn-y0)/k)}\n\n"
            
            result_text += f"Method: {self.integration_method.replace('_', ' ').title()}\n"
            result_text += "Integration setup complete!\n\n"
            result_text += "Note: Actual numerical calculation requires custom modules.\n"
            result_text += "This is a mobile interface demo.\n"
            
            self.integration_results.value = result_text
            
            await self.main_window.info_dialog("Success", "Integration setup complete")
            
        except Exception as e:
            await self.main_window.error_dialog("Error", f"Integration failed: {str(e)}")


def main():
    return numerical(
        'Numerical Methods',
        'org.example.numerical'
    )


if __name__ == '__main__':
    app = main()
    app.main_loop()