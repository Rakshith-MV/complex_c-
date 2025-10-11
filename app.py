from sympy import var, symbols, diff, sympify, E, sin, cos, tan, log, sqrt, exp, lambdify
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from numpy import pi

from interpolation import lagrange, hermitian, cubic
from nintegration import dintegrate, simpsons382d_integrate, sintegrate, trapezoidal1d_integrate, trapezoidal2d_integrate, simpsons1d_integrate , simpsons2d_integrate,  simpsons381d_integrate, simpsons382d_integrate, gaussian, romberg_integration
from node import runge_kutta, euler_first, adams_bashforth, milne, runge_kutta2
from support import string_to_function


# some starting information... 
solution_text_interpolation = "Cubic spline is yet to be implemented properly"
solution_text_nintegration = "Romberg method is under progress. \n Gaussian only for single integral"


singlefunctions = {
    'trapezoidal':trapezoidal1d_integrate,
    'simpsons':simpsons1d_integrate,
    'simpsons38':simpsons381d_integrate,
    'gaussian':gaussian,
    'romberg':romberg_integration,
    'all':sintegrate
}
doublefunctions = {
    'trapezoidal':trapezoidal2d_integrate,
    'simpsons':simpsons2d_integrate,
    'simpsons38':simpsons382d_integrate,
    'all':dintegrate
}
odefunctions1 = {
    'rk':runge_kutta,
    'adams_bashforth':adams_bashforth,
    'milne':milne
}
odefunctions2 = {
    'rk':runge_kutta2
}


class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("Numerical methods")
        self.root.geometry("1400x900")

        # Dictionary for info texts
        self.info_texts = {
            "Interpolation": (
                "Interpolation Tab Information:\n\n"
                "1. Lagrange: Standard polynomial interpolation for a set of points.\n"
                "2. Hermitian: An extension of Lagrange that also uses derivative values at each point for higher accuracy.\n"
                "3. Cubic Spline: Creates a series of piecewise cubic polynomials that pass through the points, ensuring smoothness.\n\n"
                "Input Format: Use comma-separated values for points (e.g., 1, 2, 3.5). "
                "Mathematical expressions like 'pi/2', 'e^2', 'sin(1)' are supported.\n"
                "\nFOR SRC CODE : https://github.com/Rakshith-MV/complex_c-/tree/master#"
            ),
            "Numerical Integration": (
                "Numerical Integration Tab Information:\n\n"
                "Methods:\n"
                "- Trapezoidal/Simpson's 1/3 & 3/8: Classic rules for approximating definite integrals.\n"
                "- Gaussian Quadrature: A highly accurate method that uses specific points and weights. 'h' is not required.\n"
                "- Romberg: (Under development) Uses Richardson extrapolation to improve Trapezoidal rule results.\n\n"
                "Types:\n"
                "- Single Integral: ∫f(x)dx\n"
                "- Double Integral: ∫∫f(x,y)dxdy. The plot will show a 3D surface.\n\n"
                "Function Input: Use 'x' for single integrals and 'x', 'y' for double integrals. "
                "Supports standard math functions like 'sin(x)', 'exp(y)', 'sqrt(x*y)'.\n"
                "\nFOR SRC CODE : https://github.com/Rakshith-MV/complex_c-/tree/master#"

            ),
            "Ordinary Differential Equations": (
                "ODE Tab Information:\n\n"
                "This tab solves initial value problems for first and second-order ODEs.\n\n"
                "Methods (First Order y' = f(x,y)):\n"
                "- Runge-Kutta: A popular and robust family of methods (this app uses RK4).\n"
                "- Adams-Bashforth: A multi-step method, often efficient but requires starting values.\n"
                "- Milne: A predictor-corrector multi-step method.\n"
                "- Picard: (Not implemented) An iterative method for finding successive approximations.\n\n"
                "Methods (Second Order y'' = f(x,y,y')):\n"
                "- Only Runge-Kutta is currently implemented.\n\n"
                "Analytical Solution: You can enter the exact solution y(x) to compare it with the numerical results on the plot\n."
                "\nFOR SRC CODE : https://github.com/Rakshith-MV/complex_c-/tree/master#"

            )
        }
        
        # Interpolation Variables
        self.points = []
        self.derivatives = []  # For Hermitian interpolation
        self.interpolation_type = tk.StringVar(value="lagrange")
        self.current_poly = None
        self.current_func = None
        self.current_spline = None
        # Removed analytical_func and analytical_func_expr_str from interpolation

        # Integration variables
        self.integration_type = tk.StringVar(value="single")
        self.integration_method = tk.StringVar(value="trapezoidal") 
        self.integration_results = None

        # ODE variables   Default variables
        self.ode_order = tk.StringVar(value="first")
        self.ode_method = tk.StringVar(value="rk") 
        self.ode_results = None
        self.ode_analytical_func = None # To store the callable analytical function for ODE plotting
        self.ode_analytical_func_expr_str = "" # To store the string for ODE replotting
        self.ode_numerical_results = {} # To store numerical results for replotting

        self.setup_gui()

        # Create and place the button AFTER the main GUI is packed.
        info_button = ttk.Button(self.root, text="ⓘ", command=self.show_info, width=3)
        info_button.place(relx=1.0, rely=0, x=-5, y=5, anchor='ne')
        
        # **FIX**: Force the button to the top of the stacking order to ensure it's visible.
        info_button.lift()
        
    def show_info(self):
        """Displays information about the current tab."""
        try:
            # Get the text/title of the currently selected tab
            selected_tab_title = self.main_notebook.tab(self.main_notebook.select(), "text")
            
            # Retrieve the corresponding info text from the dictionary
            info_message = self.info_texts.get(selected_tab_title, "No information available for this tab.")
            
            # Show the info message box
            messagebox.showinfo(f"Information: {selected_tab_title}", info_message)
        except tk.TclError:
            # This can happen if no tab is selected, though unlikely in a running app.
            messagebox.showwarning("Info", "Could not determine the current tab.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def setup_gui(self):
        # Create main notebook for tabs
        self.main_notebook = ttk.Notebook(self.root)
        self.main_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create interpolation, integration, and ODE tabs
        self.setup_interpolation_tab()
        self.setup_integration_tab()
        self.setup_ode_tab()
        
    def setup_interpolation_tab(self):
        """Setup the interpolation tab (existing functionality)"""
        interpolation_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(interpolation_frame, text="Interpolation")        
        # Main frame
        main_frame = ttk.Frame(interpolation_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        # Left panel for inputs
        input_frame = ttk.LabelFrame(main_frame, text="Input Data", padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        input_frame.rowconfigure(5, weight=1)
        
        # Interpolation type selection
        ttk.Label(input_frame, text="Interpolation Type:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        type_frame = ttk.Frame(input_frame)
        type_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        ttk.Radiobutton(type_frame, text="Lagrange", variable=self.interpolation_type, 
                       value="lagrange", command=self.on_type_change).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(type_frame, text="Hermitian", variable=self.interpolation_type, 
                       value="hermitian", command=self.on_type_change).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(type_frame, text="Cubic Spline", variable=self.interpolation_type, 
                       value="spline", command=self.on_type_change).pack(side=tk.LEFT)
        
        # Point input section
        ttk.Label(input_frame, text="Input Data (comma-separated, supports pi, e, ^, sin, cos, etc.):").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        point_frame = ttk.Frame(input_frame)
        point_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        point_frame.columnconfigure(1, weight=1)
        
        # X values input
        ttk.Label(point_frame, text="X values:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.x_entry = ttk.Entry(point_frame, width=40)
        self.x_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Y values input
        ttk.Label(point_frame, text="Y values:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.y_entry = ttk.Entry(point_frame, width=40)
        self.y_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(5, 0))
        
        # Derivative input (for Hermitian)
        self.deriv_label = ttk.Label(point_frame, text="Y' values:")
        self.deriv_entry = ttk.Entry(point_frame, width=40)
        
        # Button frame
        button_frame_input = ttk.Frame(point_frame)
        button_frame_input.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame_input, text="Add Points", command=self.add_points).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame_input, text="Clear Input", command=self.clear_input).pack(side=tk.LEFT)
        
        # Points list
        ttk.Label(input_frame, text="Current Points:").grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        
        # Frame for listbox and scrollbar
        list_frame = ttk.Frame(input_frame)
        list_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.points_listbox = tk.Listbox(list_frame, height=8)
        self.points_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.points_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.points_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_point).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear All", command=self.clear_points).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Calculate", command=self.calculate_interpolation).pack(side=tk.LEFT, padx=5)
        
        # Evaluation section
        eval_frame = ttk.LabelFrame(input_frame, text="Evaluate Function", padding="10")
        eval_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(eval_frame, text="Evaluate at x =").grid(row=0, column=0, padx=(0, 5))
        self.eval_entry = ttk.Entry(eval_frame, width=15)
        self.eval_entry.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(eval_frame, text="Find Value", command=self.evaluate_function).grid(row=0, column=2)
        
        # Result display
        self.eval_result = ttk.Label(eval_frame, text="Result: ", foreground="blue", font=("TkDefaultFont", 9, "bold"))
        self.eval_result.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # Right panel for plot and results
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        # Notebook for plot and polynomial
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Plot tab
        plot_frame = ttk.Frame(self.notebook)
        self.notebook.add(plot_frame, text="Plot")
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 7), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Polynomial tab
        poly_frame = ttk.Frame(self.notebook)
        self.notebook.add(poly_frame, text="Polynomial/Expression")
        
        self.poly_text = scrolledtext.ScrolledText(poly_frame, wrap=tk.WORD, height=20)
        self.poly_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Initialize display
        self.on_type_change()
        
    def setup_integration_tab(self):
        """Setup the numerical integration tab"""
        integration_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(integration_frame, text="Numerical Integration")
        
        # Main frame
        main_frame = ttk.Frame(integration_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Left panel for integration inputs
        input_frame = ttk.LabelFrame(main_frame, text="Integration Parameters", padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Integration type selection
        ttk.Label(input_frame, text="Integration Type:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        type_frame = ttk.Frame(input_frame)
        type_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        ttk.Radiobutton(type_frame, text="Single Integral", variable=self.integration_type, 
                       value="single", command=self.on_integration_type_change).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(type_frame, text="Double Integral", variable=self.integration_type, 
                       value="double", command=self.on_integration_type_change).pack(side=tk.LEFT)
        
        # Method selection
        ttk.Label(input_frame, text="Integration Method:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        method_frame = ttk.Frame(input_frame)
        method_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        methods_row1 = ttk.Frame(method_frame)
        methods_row1.pack(fill=tk.X, pady=(0, 5))

            

        # Function input section (existing)
        self.function_frame = ttk.LabelFrame(input_frame, text="Function Input")
        self.function_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        # ... (add function_entry and labels inside this frame) ...

        # List of values input section (new)
        self.list_frame = ttk.LabelFrame(input_frame, text="List of Values Input")
        self.list_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        # ... (add x_list_entry, y_list_entry, etc. inside this frame) ...


        ttk.Radiobutton(methods_row1, text="Simpson's 1/3", variable=self.integration_method, 
                       value="simpsons").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(methods_row1, text="trapezoidal", variable=self.integration_method, 
                       value="trapezoidal").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(methods_row1, text="Simpson's 3/8", variable=self.integration_method, 
                       value="simpsons38").pack(side=tk.LEFT)

        methods_row2 = ttk.Frame(method_frame)
        methods_row2.pack(fill=tk.X)
        
        ttk.Radiobutton(methods_row2, text="Gaussian", variable=self.integration_method, 
                       value="gaussian").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(methods_row2, text="Romberg", variable=self.integration_method, 
                       value="romberg").pack(side=tk.LEFT)
        ttk.Radiobutton(methods_row2, text="All", variable=self.integration_method,
                        value="all").pack(side=tk.LEFT, padx=(0, 10))
        
        # Function input
        ttk.Label(input_frame, text="Function f(x) or f(x,y):").grid(row=4, column=0, sticky=tk.W, pady=(15, 5))
        ttk.Label(input_frame, text="(Use x, y, pi, e, sin, cos, exp, log, sqrt, etc.)").grid(row=5, column=0, sticky=tk.W, pady=(0, 5))
        
        self.function_entry = ttk.Entry(input_frame, width=50)
        self.function_entry.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Single integral parameters
        self.single_frame = ttk.LabelFrame(input_frame, text="Single Integral Parameters", padding="5")
        self.single_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        single_grid = ttk.Frame(self.single_frame)
        single_grid.pack(fill=tk.X)
        
        ttk.Label(single_grid, text="x0:").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        self.x0_entry = ttk.Entry(single_grid, width=10)
        self.x0_entry.grid(row=0, column=1, padx=(0, 15))
        
        ttk.Label(single_grid, text="xN:").grid(row=0, column=2, padx=(0, 5), sticky=tk.W)
        self.xn_entry = ttk.Entry(single_grid, width=10)
        self.xn_entry.grid(row=0, column=3, padx=(0, 15))
        
        ttk.Label(single_grid, text="h:").grid(row=0, column=4, padx=(0, 5), sticky=tk.W)
        self.h_single_entry = ttk.Entry(single_grid, width=10)
        self.h_single_entry.grid(row=0, column=5)
        
        # Double integral parameters
        self.double_frame = ttk.LabelFrame(input_frame, text="Double Integral Parameters", padding="5")
        self.double_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        double_grid = ttk.Frame(self.double_frame)
        double_grid.pack(fill=tk.X)
        
        # First row
        ttk.Label(double_grid, text="x0:").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        self.x0_double_entry = ttk.Entry(double_grid, width=8)
        self.x0_double_entry.grid(row=0, column=1, padx=(0, 10))

        ttk.Label(double_grid, text="xn:").grid(row=0, column=2, padx=(0, 5), sticky=tk.W)
        self.xn_double_entry = ttk.Entry(double_grid, width=8)
        self.xn_double_entry.grid(row=0, column=3, padx=(0, 10))
        
        ttk.Label(double_grid, text="h:").grid(row=0, column=4, padx=(0, 5), sticky=tk.W)
        self.h_double_entry = ttk.Entry(double_grid, width=8)
        self.h_double_entry.grid(row=0, column=5, padx=(0, 10))
        
        # Second row
        ttk.Label(double_grid, text="y0:").grid(row=1, column=0, padx=(0, 5), sticky=tk.W, pady=(5, 0))
        self.y0_entry = ttk.Entry(double_grid, width=8)
        self.y0_entry.grid(row=1, column=1, padx=(0, 10), pady=(5, 0))
        
        ttk.Label(double_grid, text="yn:").grid(row=1, column=2, padx=(0, 5), sticky=tk.W, pady=(5, 0))
        self.yn_entry = ttk.Entry(double_grid, width=8)
        self.yn_entry.grid(row=1, column=3, padx=(0, 10), pady=(5, 0))
        
        ttk.Label(double_grid, text="k:").grid(row=1, column=4, padx=(0, 5), sticky=tk.W, pady=(5, 0))
        self.k_entry = ttk.Entry(double_grid, width=8)
        self.k_entry.grid(row=1, column=5, padx=(0, 10), pady=(5, 0))
        
        # Calculate button
        calculate_button = ttk.Button(input_frame, text="Calculate Integration", 
                                    command=self.calculate_integration)
        calculate_button.grid(row=9, column=0, columnspan=2, pady=(15, 0))
        
        # Clear button
        clear_button = ttk.Button(input_frame, text="Clear All", 
                                command=self.clear_integration)
        clear_button.grid(row=10, column=0, columnspan=2, pady=(5, 0))
        
        # Right panel for results
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        # Results notebook
        self.integration_notebook = ttk.Notebook(right_frame)
        self.integration_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Results tab
        results_frame = ttk.Frame(self.integration_notebook)
        self.integration_notebook.add(results_frame, text="Results")
        
        # Results display
        self.integration_results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=25)
        self.integration_results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Array output tab
        array_frame = ttk.Frame(self.integration_notebook)
        self.integration_notebook.add(array_frame, text="Array Output")
        
        self.array_output_text = scrolledtext.ScrolledText(array_frame, wrap=tk.WORD, height=25)
        self.array_output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Plot tab for integration
        integration_plot_frame = ttk.Frame(self.integration_notebook)
        self.integration_notebook.add(integration_plot_frame, text="Plot")
        
        # Create matplotlib figure for integration
        self.integration_fig = Figure(figsize=(10, 7), dpi=100)
        self.integration_ax = self.integration_fig.add_subplot(111)
        
        self.integration_canvas = FigureCanvasTkAgg(self.integration_fig, integration_plot_frame)
        
        self.integration_toolbar = NavigationToolbar2Tk(self.integration_canvas, integration_plot_frame)
        self.integration_toolbar.pack(side=tk.TOP, fill=tk.X)
        
        self.integration_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize integration display
        self.on_integration_type_change()
    
    def setup_ode_tab(self):
        """Setup the ODE tab"""
        ode_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(ode_frame, text="Ordinary Differential Equations")
        
        # Main frame
        main_frame = ttk.Frame(ode_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Left panel for ODE inputs
        input_frame = ttk.LabelFrame(main_frame, text="ODE Parameters", padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
    
        # ODE order selection
        ttk.Label(input_frame, text="ODE Order:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        order_frame = ttk.Frame(input_frame)
        order_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        ttk.Radiobutton(order_frame, text="First Order", variable=self.ode_order, 
                       value="first", command=self.on_ode_order_change).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(order_frame, text="Second Order", variable=self.ode_order, 
                       value="second", command=self.on_ode_order_change).pack(side=tk.LEFT)
        
        # Method selection
        ttk.Label(input_frame, text="Solution Method:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        method_frame = ttk.Frame(input_frame)
        method_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        methods_row1 = ttk.Frame(method_frame)
        methods_row1.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Radiobutton(methods_row1, text="Picard's Method", variable=self.ode_method, 
                       value="picard").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(methods_row1, text="Runge-Kutta", variable=self.ode_method, 
                       value="rk").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(methods_row1, text="Milne's Method", variable=self.ode_method, 
                       value="milne").pack(side=tk.LEFT)

        methods_row2 = ttk.Frame(method_frame)
        methods_row2.pack(fill=tk.X)
        
        ttk.Radiobutton(methods_row2, text="Adams-Bashforth", variable=self.ode_method, 
                       value="adams_bashforth").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(methods_row2, text="All", variable=self.ode_method, 
                       value="all").pack(side=tk.LEFT)
        
        # First Order ODE inputs
        self.first_order_frame = ttk.LabelFrame(input_frame, text="First Order ODE: y' = f(x,y)", padding="5")
        self.first_order_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Function input for first order
        ttk.Label(self.first_order_frame, text="f(x,y) =").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.ode_function_entry = ttk.Entry(self.first_order_frame, width=40)
        self.ode_function_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Initial conditions and parameters
        params_frame = ttk.Frame(self.first_order_frame)
        params_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Label(params_frame, text="x₀:").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        self.ode_x0_entry = ttk.Entry(params_frame, width=10)
        self.ode_x0_entry.grid(row=0, column=1, padx=(0, 15))
        
        ttk.Label(params_frame, text="y₀:").grid(row=0, column=2, padx=(0, 5), sticky=tk.W)
        self.ode_y0_entry = ttk.Entry(params_frame, width=10)
        self.ode_y0_entry.grid(row=0, column=3, padx=(0, 15))
        
        ttk.Label(params_frame, text="h:").grid(row=0, column=4, padx=(0, 5), sticky=tk.W)
        self.ode_h_entry = ttk.Entry(params_frame, width=10)
        self.ode_h_entry.grid(row=0, column=5, padx=(0, 15))
        
        ttk.Label(params_frame, text="xn :").grid(row=1, column=0, padx=(0, 5), sticky=tk.W, pady=(5, 0))
        self.ode_n_entry = ttk.Entry(params_frame, width=10)
        self.ode_n_entry.grid(row=1, column=1, padx=(0, 15), pady=(5, 0))
        
        # Second Order ODE inputs
        self.second_order_frame = ttk.LabelFrame(input_frame, text="Second Order ODE: y'' = f(x,y,y')", padding="5")
        self.second_order_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Function input for second order
        ttk.Label(self.second_order_frame, text="f(x,y,y') =").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.ode2_function_entry = ttk.Entry(self.second_order_frame, width=40)
        self.ode2_function_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Initial conditions for second order
        params2_frame = ttk.Frame(self.second_order_frame)
        params2_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Label(params2_frame, text="x₀:").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        self.ode2_x0_entry = ttk.Entry(params2_frame, width=8)
        self.ode2_x0_entry.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(params2_frame, text="y₀:").grid(row=0, column=2, padx=(0, 5), sticky=tk.W)
        self.ode2_y0_entry = ttk.Entry(params2_frame, width=8)
        self.ode2_y0_entry.grid(row=0, column=3, padx=(0, 10))
        
        ttk.Label(params2_frame, text="y'₀:").grid(row=0, column=4, padx=(0, 5), sticky=tk.W)
        self.ode2_dy0_entry = ttk.Entry(params2_frame, width=8)
        self.ode2_dy0_entry.grid(row=0, column=5, padx=(0, 10))
        
        ttk.Label(params2_frame, text="h:").grid(row=1, column=0, padx=(0, 5), sticky=tk.W, pady=(5, 0))
        self.ode2_h_entry = ttk.Entry(params2_frame, width=8)
        self.ode2_h_entry.grid(row=1, column=1, padx=(0, 10), pady=(5, 0))
        
        ttk.Label(params2_frame, text="Xn").grid(row=1, column=2, padx=(0, 5), sticky=tk.W, pady=(5, 0))
        self.ode2_xn_entry = ttk.Entry(params2_frame, width=8)
        self.ode2_xn_entry.grid(row=1, column=3, padx=(0, 10), pady=(5, 0))
        
        # Special parameters for shooting method
        self.shooting_frame = ttk.LabelFrame(input_frame, text="Shooting Method Parameters", padding="5")
        self.shooting_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        shooting_params = ttk.Frame(self.shooting_frame)
        shooting_params.pack(fill=tk.X)
        
        ttk.Label(shooting_params, text="Target y(xₙ):").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        self.shooting_target_entry = ttk.Entry(shooting_params, width=12)
        self.shooting_target_entry.grid(row=0, column=1, padx=(0, 15))
        
        ttk.Label(shooting_params, text="Initial guess y'₀:").grid(row=0, column=2, padx=(0, 5), sticky=tk.W)
        self.shooting_guess_entry = ttk.Entry(shooting_params, width=12)
        self.shooting_guess_entry.grid(row=0, column=3)
        
        # Calculate and Clear buttons
        button_frame_ode = ttk.Frame(input_frame)
        button_frame_ode.grid(row=7, column=0, columnspan=2, pady=(15, 0))
        
        ttk.Button(button_frame_ode, text="Solve ODE", 
                  command=self.solve_ode).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame_ode, text="Clear All", 
                  command=self.clear_ode).pack(side=tk.LEFT)
        
        # --- Analytical Solution Section (New for ODE) ---
        self.analytical_ode_frame = ttk.LabelFrame(input_frame, text="Analytical Solution y(x)", padding="10")
        self.analytical_ode_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Label(self.analytical_ode_frame, text="y(x) =").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        self.ode_analytical_func_entry = ttk.Entry(self.analytical_ode_frame, width=30)
        self.ode_analytical_func_entry.grid(row=0, column=1, padx=(0, 10), sticky=(tk.W, tk.E))

        ttk.Button(self.analytical_ode_frame, text="Plot Analytical Solution", command=self.plot_ode_analytical_solution).grid(row=0, column=2)
        
        self.ode_analytical_plot_status = ttk.Label(self.analytical_ode_frame, text="", foreground="green", font=("TkDefaultFont", 9, "bold"))
        self.ode_analytical_plot_status.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        # --- End Analytical Solution Section ---

        # Right panel for ODE results
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        # ODE Results notebook
        self.ode_notebook = ttk.Notebook(right_frame)
        self.ode_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Solution tab
        solution_frame = ttk.Frame(self.ode_notebook)
        self.ode_notebook.add(solution_frame, text="Solution")
        
        self.ode_solution_text = scrolledtext.ScrolledText(solution_frame, wrap=tk.WORD, height=25)
        self.ode_solution_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Table tab
        table_frame = ttk.Frame(self.ode_notebook)
        self.ode_notebook.add(table_frame, text="Solution Table")
        
        self.ode_table_text = scrolledtext.ScrolledText(table_frame, wrap=tk.NONE, height=25, font=("Courier", 10))
        self.ode_table_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Plot tab for ODE
        ode_plot_frame = ttk.Frame(self.ode_notebook)
        self.ode_notebook.add(ode_plot_frame, text="Solution Plot")
        
        # Create matplotlib figure for ODE
        self.ode_fig = Figure(figsize=(10, 7), dpi=100)
        self.ode_ax = self.ode_fig.add_subplot(111)
        
        self.ode_canvas = FigureCanvasTkAgg(self.ode_fig, ode_plot_frame)
        
        self.ode_toolbar = NavigationToolbar2Tk(self.ode_canvas, ode_plot_frame)
        self.ode_toolbar.pack(side=tk.TOP, fill=tk.X)
        
        self.ode_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize ODE display
        self.on_ode_order_change()
    
    def on_ode_order_change(self):
        """Handle ODE order change"""
        if self.ode_order.get() == "first":
            self.first_order_frame.grid()
            self.second_order_frame.grid_remove()
            # Show/hide shooting method parameters based on method
            if self.ode_method.get() == "shooting":
                self.shooting_frame.grid()
            else:
                self.shooting_frame.grid_remove()
        else:
            self.first_order_frame.grid_remove()
            self.second_order_frame.grid()
            # Show shooting method parameters for second order if selected
            if self.ode_method.get() == "shooting":
                self.shooting_frame.grid()
            else:
                self.shooting_frame.grid_remove()
    
    def clear_ode(self):
        """Clear all ODE inputs and results"""
        # Clear first order inputs
        self.ode_function_entry.delete(0, tk.END)
        self.ode_x0_entry.delete(0, tk.END)
        self.ode_y0_entry.delete(0, tk.END)
        self.ode_h_entry.delete(0, tk.END)
        self.ode_n_entry.delete(0, tk.END)
        
        # Clear second order inputs
        self.ode2_function_entry.delete(0, tk.END)
        self.ode2_x0_entry.delete(0, tk.END)
        self.ode2_y0_entry.delete(0, tk.END)
        self.ode2_dy0_entry.delete(0, tk.END)
        self.ode2_h_entry.delete(0, tk.END)
        self.ode2_xn_entry.delete(0, tk.END)
        
        # Clear shooting method inputs
        self.shooting_target_entry.delete(0, tk.END)
        self.shooting_guess_entry.delete(0, tk.END)

        # Clear analytical function input and status
        self.ode_analytical_func_entry.delete(0, tk.END)
        self.ode_analytical_plot_status.config(text="")
        self.ode_analytical_func = None
        self.ode_analytical_func_expr_str = ""
        
        # Clear results
        self.ode_solution_text.delete(1.0, tk.END)
        self.ode_table_text.delete(1.0, tk.END)
        
        # Clear plot and stored numerical results
        self.ode_numerical_results = {}
        self._update_ode_plot() # Use helper to clear and redraw plot (which will be empty now)
        
        self.ode_results = None
    
    def _update_ode_plot(self):
        """Helper method to update the ODE solution plot with all available data."""
        self.ode_ax.clear()

        # Plot numerical solutions
        if self.ode_numerical_results:
            x_values = self.ode_numerical_results.get('x', [])
            if self.ode_method.get() == 'all':
                for method_name in odefunctions1.keys():
                    if method_name in self.ode_numerical_results:
                        self.ode_ax.plot(x_values, self.ode_numerical_results[method_name], 
                                         label=f'{method_name.replace("_", "-").title()} Solution')
            else:
                method_name = self.ode_method.get()
                if method_name in self.ode_numerical_results:
                    y_values = self.ode_numerical_results[method_name]
                    self.ode_ax.plot(x_values, y_values, 'b-', linewidth=2, label=f'{method_name.replace("_", "-").title()} Solution')
                    if x_values and y_values:
                        self.ode_ax.plot(x_values[0], y_values[0], 'ro', markersize=8, label='Initial Condition')
                        self.ode_ax.plot(x_values[-1], y_values[-1], 'go', markersize=8, label='Final Value')
        
        # Plot analytical solution if available
        if self.ode_analytical_func and self.ode_numerical_results.get('x'): # Only plot if numerical results define x range
            x_plot = np.linspace(min(self.ode_numerical_results['x']), max(self.ode_numerical_results['x']), 400)
            try:
                y_plot = np.array([self.ode_analytical_func(val) for val in x_plot])
                self.ode_ax.plot(x_plot, y_plot, 'k--', linewidth=1.5, label=f'Analytical: {self.ode_analytical_func_expr_str}')
            except Exception as e:
                # Handle cases where analytical function might fail for some x values in the range
                self.ode_analytical_plot_status.config(text=f"Analytical function plotting issue: {e}", foreground="red")




        self.ode_ax.grid(True, alpha=0.3)
        self.ode_ax.legend()
        self.ode_ax.set_xlabel('x')
        self.ode_ax.set_ylabel('y')
        self.ode_ax.set_title(f'First Order ODE Solutions - {self.ode_method.get().replace("_", "-").title()}')
        self.ode_canvas.draw()

    def ode_table(self):
        table_text = "Solution Table:\n"
        if self.ode_order.get()== 'first':
            if self.ode_method.get() == 'all':
                table_text += f"{'i':>3} {'x':>10} {'Runge-Kutta':>14}{'Adams-Bashforth':>18}{'Milne':>10}\n" # Removed error column
                table_text+= '-'*70 + '\n'
                for i, x_val in enumerate(self.ode_numerical_results['x']):
                    rk_val = self.ode_numerical_results.get('rk', [])[i] if i < len(self.ode_numerical_results.get('rk', [])) else float('nan')
                    ab_val = self.ode_numerical_results.get('adams_bashforth', [])[i] if i < len(self.ode_numerical_results.get('adams_bashforth', [])) else float('nan')
                    milne_val = self.ode_numerical_results.get('milne', [])[i] if i < len(self.ode_numerical_results.get('milne', [])) else float('nan')
                    table_text += f"{i:>3} {x_val:>10.4f} {rk_val:>14.6f} {ab_val:>18.6f}{milne_val:>10.6f}\n"
            else:   #if analytical expression is given
                if self.ode_analytical_func_expr_str == "":
                    table_text += f"{'i':>3} {'x':>10} {'y':>12} {'Error':>12}\n"
                    table_text += "-" * 40 + "\n"
                    x_values = self.ode_numerical_results.get('x', [])
                    y_values = self.ode_numerical_results.get(self.ode_method.get(), [])
                    for i, (x_val, y_val) in enumerate(zip(x_values, y_values)):
                        error = 0.001 * i  # Placeholder error
                        table_text += f"{i:>3} {x_val:>10.4f} {y_val:>12.6f} {error:>12.6f}\n"
                else: #if it is not given!!!
                    table_text += f"{'i':>3} {'x':>10} {'y':>12} {'Error':>12}\n"
                    table_text += "-" * 40 + "\n"
                    x_values = self.ode_numerical_results.get('x', [])
                    y_values = self.ode_numerical_results.get(self.ode_method.get(), [])
                    for i, (x_val, y_val) in enumerate(zip(x_values, y_values)):
                        error = abs(y_val - self.ode_analytical_func(x_val)) if self.ode_analytical_func else '-'  # Use actual error if analytical func exists
                        table_text += f"{i:>3} {x_val:>10.4f} {y_val:>12.6f} {error:>12.6f}\n"
        else:
            #For now only Runge kutta is implemented.
            x_values = self.ode_numerical_results.get('x', [])
            y_values = self.ode_numerical_results.get(self.ode_method.get(), [])
            y1_values = self.ode_numerical_results.get(self.ode_method.get()+'1',[])

            if self.ode_analytical_func_expr_str == "":
                table_text += f"{'i':>3} {'x':>10} {'y':>12} {"y'":>12}\n"
                table_text += "-" * 40 + "\n"
                for i, (x_val, y_val, y1_val) in enumerate(zip(x_values, y_values, y1_values)):
                    table_text += f"{i:>3} {x_val:>10.4f} {y_val:>12.6f} {y1_val:>12.6f}\n"
            else:
                table_text += f"{'i':>3} {'x':>10} {'y':>12} {"y1'":>12}{'Error':>12}\n"
                table_text += "-" * 40 + "\n"
                for i,(x_val, y_val, y1_val) in enumerate(zip(x_values, y_values, y1_values)):
                    error = abs(y_val - self.ode_analytical_func(x_val))
                    table_text += f"{i:>3} {x_val:>10.4f} {y_val:>12.6f} {y1_val:>12.6f} {error:>12.6f}\n"
            table_text += "-" * 40 + "\n"
        return table_text
    
    def solve_ode(self):
        """Solve ODE using selected method - placeholder implementation"""
        try:
            if self.ode_order.get() == "first":
                function_str = self.ode_function_entry.get().strip()
                if not function_str:
                    messagebox.showerror("Error", "Please enter the ODE function f(x,y)")
                    return
                
                # Get parameters
                x0 = float(sympify(self.ode_x0_entry.get(), locals={'pi': pi, 'e': E}))
                y0 = float(sympify(self.ode_y0_entry.get(), locals={'pi': pi, 'e': E}))
                h = float(sympify(self.ode_h_entry.get(), locals={'pi': pi, 'e': E}))
                xn = float(sympify(self.ode_n_entry.get(), locals={'pi': pi, 'e': E}))
                f = string_to_function(function_str, "double")


                self.ode_numerical_results = {} # Clear previous numerical results
                
                if self.ode_method.get() in ['rk','milne','adams_bashforth']:
                    sol = odefunctions1[self.ode_method.get()](f, x0, xn, y0, h)
                    x_values, y_values = sol
                    self.ode_numerical_results['x'] = x_values
                    self.ode_numerical_results[self.ode_method.get()] = y_values

                    # Create solution text
                    solution_text = f"First Order ODE Solution\n"
                    solution_text += f"Method: {self.ode_method.get().replace('_', '-').title()}\n"
                    solution_text += f"ODE: y' = {function_str}\n"
                    solution_text += f"Initial conditions: x₀ = {x0}, y₀ = {y0}\n"
                    solution_text += f"Step size: h = {h}, At point : xn = {xn}\n\n"
                    
                    solution_text += f"Solution computed using {self.ode_method.get().replace('_', '-').title()} method\n"
                    solution_text += f"Final value: y({x_values[-1]:.4f}) = {y_values[-1]:.6f}\n"
                
                
                elif self.ode_method.get() == 'all':
                    solution_text = f"First Order ODE Solution\n"
                    solution_text += f"ODE: y' = {function_str}\n"
                    solution_text += f"Initial conditions: x₀ = {x0}, y₀ = {y0}\n"
                    solution_text += f"Step size: h = {h}, At point : xn = {xn}\n\n"
                    
                    for i,j in zip(odefunctions1.keys(), odefunctions1.values()):
                        solution_text += f"Solution computed using {i.replace('_', '-').title()} method\n"
                        sol = j(f, x0, xn, y0, h)
                        x_values, y_values = sol
                        self.ode_numerical_results[i] = y_values # Store results
                        solution_text += f"Final value: y({x_values[-1]:.4f}) = {y_values[-1]:.6f}\n"
                    self.ode_numerical_results['x'] = x_values # Store x-values once
                else: 
                    messagebox.showinfo("info", f"{self.ode_method.get().replace('_', '-').title()} method not implemented yet. Using placeholder values.")
                    return

                
            else:  # Second order
                if self.ode_method.get() in ['picard', 'milne','adams_bashforth','all']:
                    messagebox.showinfo("Info", f"{self.ode_method.get().replace('_', '-').title()} method not implemented yet for second order ODEs. Using Runge-Kutta instead.")
                    self.ode_method.set('rk')  # Default to Runge-Kutta

                # To store values
                self.ode_numerical_results = {}

                function_str = self.ode2_function_entry.get().strip()
                if not function_str:
                    messagebox.showerror("Error", "Please enter the ODE function f(x,y,y')")
                    return
                

                # Get parameters
                x0 = float(sympify(self.ode2_x0_entry.get(), locals={'pi': pi, 'e': E}))
                y0 = float(sympify(self.ode2_y0_entry.get(), locals={'pi': pi, 'e': E}))
                dy0 = float(sympify(self.ode2_dy0_entry.get(), locals={'pi': pi, 'e': E}))
                h = float(sympify(self.ode2_h_entry.get(), locals={'pi': pi, 'e': E}))
                xn = float(sympify(self.ode2_xn_entry.get(), locals={'pi': pi, 'e': E})) 
                g = string_to_function(function_str, "triple") #depends on x, y, y'==z

                solution_text = f"Second Order ODE Solution\n"
                solution_text += f"Method: {self.ode_method.get().replace('_', '-').title()}\n"
                solution_text += f"ODE: y'' = {function_str}\n"
                solution_text += f"Initial conditions: x₀ = {x0}, y₀ = {y0}, y'₀ = {dy0}\n"
                solution_text += f"Step size: h = {h}, Number of steps: n = {int((xn-x0)/h)}\n\n" 

                # if self.ode_method.get() == "shooting":
                #     target = float(sympify(self.shooting_target_entry.get(), locals={'pi': pi, 'e': E}))
                #     guess = float(sympify(self.shooting_guess_entry.get(), locals={'pi': pi, 'e': E}))
                #     solution_text += f"Shooting method with target y({x_values[-1]:.4f}) = {target}\n"
                #     solution_text += f"Initial guess for y'₀: {guess}\n"
                # else:
                #     solution_text += f"Solution computed using {self.ode_method.get().replace('_', '-').title()} method\n"
                #     sol = odefunctions2[self.ode_method.get()](f,g, x0, xn, y0, dy0, h, n_steps)
                if self.ode_method.get() == "rk":
                    sol = odefunctions2[self.ode_method.get()](g, x0, xn, y0, dy0, h)
                    x_values, y_values, y1_values = sol
                    solution_text += f"Final value: y({x_values[-1]:.4f}) = {y_values[-1]:.6f};, y'({x_values[-1]:.4f}) = {y1_values[-1]:.6f}\n" 
                    self.ode_numerical_results['x'] = x_values
                    self.ode_numerical_results[self.ode_method.get()] = y_values
                    self.ode_numerical_results[self.ode_method.get()+'1'] = y1_values

                else:
                    messagebox.showinfo("Info", "Not implemented yet")

            # Display solution text
            self.ode_solution_text.delete(1.0, tk.END)
            self.ode_solution_text.insert(1.0, solution_text)

            # Create and display solution table
            table_text = self.ode_table()
            
            self.ode_table_text.delete(1.0, tk.END)
            self.ode_table_text.insert(1.0, table_text)
            
            # Plot solutions using the helper method
            self._update_ode_plot()
            
            messagebox.showinfo("Success", f"ODE solved using {self.ode_method.get().replace('_', '-').title()} method")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Please enter valid numeric values for all parameters: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"ODE solution failed: {str(e)}")
    
    # --- New plot_ode_analytical_solution method ---
    def plot_ode_analytical_solution(self):
        """Plots the analytical function entered by the user on the ODE plot."""
        func_str = self.ode_analytical_func_entry.get().strip()
        if not func_str:
            messagebox.showwarning("Warning", "Please enter an analytical function to plot.")
            self.ode_analytical_plot_status.config(text="")
            return

        try:
            x_sym = symbols('x') # Define 'x' as a symbolic variable
            # Use locals for common functions and constants
            expr = sympify(func_str, locals={'pi': pi, 'e': E, 'sin':sin, 'cos':cos, 'tan':tan, 'log':log, 'exp':exp, 'sqrt':sqrt})
            self.ode_analytical_func = lambdify(x_sym, expr, 'numpy')
            self.ode_analytical_func_expr_str = func_str # Store the string for replotting

            # Determine x-range for plotting based on numerical solution's x-values if available
            x_values_for_range = self.ode_numerical_results.get('x')
            if x_values_for_range:
                x_plot = np.array(x_values_for_range)
            else: # Fallback to user input range if no numerical solution calculated yet
                try:
                    x0 = float(sympify(self.ode_x0_entry.get(), locals={'pi': pi, 'e': E}))
                    xn = float(sympify(self.ode_n_entry.get(), locals={'pi': pi, 'e': E})) # Assuming n_entry is x_final
                    x_plot = np.linspace(x0, xn, 500)
                except:
                    # Default range if even input parameters are not valid/set
                    x_plot = np.linspace(-5, 5, 500)
            
            # Attempt to evaluate the analytical function over this range to catch issues early
            _ = self.ode_analytical_func(x_plot) # Just try to run it

            self._update_ode_plot() # Update plot with new analytical function
            
            self.ode_analytical_plot_status.config(text="Analytical function plotted successfully.", foreground="green")

        except (SyntaxError, TypeError, NameError) as e:
            messagebox.showerror("Error", f"Invalid analytical function string: {e}\nEnsure correct syntax and variable 'x'.")
            self.ode_analytical_plot_status.config(text="Error plotting analytical function.", foreground="red")
            self.ode_analytical_func = None # Clear the stored function on error
            self.ode_analytical_func_expr_str = ""
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while plotting analytical function: {e}")
            self.ode_analytical_plot_status.config(text="Error plotting analytical function.", foreground="red")
            self.ode_analytical_func = None
            self.ode_analytical_func_expr_str = ""
    # --- End new method ---
    
    def on_input_method_change(self):
        if self.input_method.get() == "function":
            self.function_frame.grid()
            self.list_frame.grid_remove()
        else:
            self.function_frame.grid_remove()
            self.list_frame.grid()

    def on_integration_type_change(self):
        """Handle integration type change"""
        if self.integration_type.get() == "single":
            self.single_frame.grid()
            self.double_frame.grid_remove()
        else:
            self.single_frame.grid_remove()
            self.double_frame.grid()
    
    def integration_plot(self,
                         f,
                         X,
                         Y=None):
        """
        plot the intermediate trianlges
        x and y are lists of values, 
        we shall build meshes and implement the barplot
        
        """
        messagebox.showinfo("1")
        if self.integration_type.get() == 'single':
            if self.integration_method.get() == 'trapezoidal':
                h = X[1] - X[0]
                for j,i in enumerate(np.arange(X[0], X[-1],h)):
                    points = np.linspace(i, i+h, 25)
                    self.integration_ax.fill_between(points, 0, f[j], color='lightblue', alpha=0.5)
            if self.integration_method.get() == 'simpsons':
                h = X[1] - X[0]
                for j,i in enumerate(np.arange(X[0], X[-1],2*h)):
                    points = np.linspace(i,i+2*h,25)
                    self.integration_ax.fill_between(points,0,f[j], color='lightblue',alpha=0.5)
            if self.integration_method.get() == 'simpsons38':
                h = X[1] - X[0]
                for j,i in enumerate(np.arange(X[0],X[-1],3*h)):
                    if i+3*h <= X[-1]:
                        points = np.linspace(i,i+3*h, 25)
                        self.integration_ax.fill_between(points,0,f[j],color='lightblue',alpha=0.5)
        else:
            if self.integration_method.get() == 'trapezoidal':
                messagebox.showinfo("2")     
                h = X[1]-X[0]   #probably not required to create another mesh
                k = Y[1]-Y[0]
                x_vals = X[:-1]
                y_vals = Y[:-1]
                x, y = np.meshgrid(x_vals, y_vals)
                x_vals = x.ravel()
                y_vals = y.ravel()
                base = np.zeros_like(f)
                # with open("debug.txt",'w+') as ff:
                #     ff.write(f"x_vals: {x_vals} : {len(x_vals)}\n")
                #     ff.write(f"y_vals: {y_vals} : {len(y_vals)}\n")
                #     ff.write(f"f: {f}, : {len(f)}\n")
                #     # f.write(f"base: {base} : {len(base)}\n ")
                #     # f.write(f"h: {h}\n")
                self.integration_ax.bar3d(x_vals, y_vals, base, h, k, f, shade=True, alpha=0.5)
            if self.integration_method.get() == 'simpsons':
                h = X[1]-X[0]
                k = Y[1]-Y[0]
                x_vals = X[:-2:2]
                y_vals = Y[:-2:2]
                x, y = np.meshgrid(x_vals, y_vals)
                x_vals = x.ravel()
                y_vals = y.ravel()
                base = np.zeros_like(f)
                self.integration_ax.bar3d(x_vals, y_vals, base, 2*h, 2*k, f, shade=True, alpha=0.5)

            if self.integration_method.get() == 'simpsons38':
                messagebox.showinfo("3")
                h = X[1]-X[0]
                k = Y[1]-Y[0]
                
                # Fix: Create grid points at intervals of 3*h and 3*k
                x_vals = [X[0] + 3*i*h for i in range(int(len(X)/3))]
                y_vals = [Y[0] + 3*j*k for j in range(int(len(Y)/3))]
                
                # Don't use meshgrid and ravel - create the positions directly
                x_pos = []
                y_pos = []
                for y in y_vals:
                    for x in x_vals:
                        x_pos.append(x)
                        y_pos.append(y)
                
                x_pos = np.array(x_pos)
                y_pos = np.array(y_pos)
                base = np.zeros_like(f)
                
                with open("debug.txt",'w+') as ff:
                    ff.write(f"x_pos: {x_pos} : {len(x_pos)}\n")
                    ff.write(f"y_pos: {y_pos} : {len(y_pos)}\n")
                    ff.write(f"f: {f}, : {len(f)}\n")
                    ff.write(f"base: {base} : {len(base)}\n")
                
                self.integration_ax.bar3d(x_pos, y_pos, base, 3*h, 3*k, f, shade=True, alpha=0.5)
                
                # messagebox.showinfo("3")
                # h = X[1]-X[0]
                # k = Y[1]-Y[0]
                # x_vals = [X[0] + 3*i*h for i in range(int(len(X)/3))]
                # y_vals = [Y[0] + 3*i*k for i in range(int(len(Y)/3))]
                # x, y = np.meshgrid(x_vals, y_vals)
                # x_vals = x.ravel()
                # y_vals = y.ravel()
                # base = np.zeros_like(f)
                # with open("debug.txt",'w+') as ff:
                #     ff.write(f"x_vals: {x_vals} : {len(x_vals)}\n")
                #     ff.write(f"y_vals: {y_vals} : {len(y_vals)}\n")
                #     ff.write(f"f: {f}, : {len(f)}\n")
                #     ff.write(f"base: {base} : {len(base)}\n ")
                # self.integration_ax.bar3d(x_vals, y_vals, base, 3*h, 3*k, f, shade=True, alpha=0.5) 

    def clear_integration(self):
        """Clear all integration inputs and results"""
        # Clear input fields
        self.function_entry.delete(0, tk.END)
        self.x0_entry.delete(0, tk.END)
        self.xn_entry.delete(0, tk.END)
        self.h_single_entry.delete(0, tk.END)
        self.x0_double_entry.delete(0, tk.END)
        self.xn_double_entry.delete(0, tk.END)
        self.h_double_entry.delete(0, tk.END)
        self.y0_entry.delete(0, tk.END)
        self.yn_entry.delete(0, tk.END)
        self.k_entry.delete(0, tk.END)
        
        # Clear results
        self.integration_results_text.delete(1.0, tk.END)
        self.array_output_text.delete(1.0, tk.END)
        
        # Clear plot
        self.integration_ax.clear()
        self.integration_canvas.draw()
        
        self.integration_results = None
    
    def calculate_integration(self):
        """Calculate numerical integration - placeholder for now"""
        try:
            function_str = self.function_entry.get().strip()
            if not function_str:
                messagebox.showerror("Error", "Please enter a function")
                return
            
            # Get parameters based on integration type
            if self.integration_type.get() == "single":
                try:
                    f = string_to_function(function_str, integration_type="single")
                    x0 = float(sympify(self.x0_entry.get(), locals={'pi': pi, 'e': E}))
                    xn = float(sympify(self.xn_entry.get(), locals={'pi': pi, 'e': E}))
                    
                    if self.integration_method.get() != 'gaussian' and not self.h_single_entry.get():
                        messagebox.showerror("Error", "Please fill all single integral parameters (including h)")
                        return
                    if self.integration_method.get() == 'gaussian' and (not self.x0_entry.get() or not self.xn_entry.get()):
                        messagebox.showerror("Error", "Please fill x0 and xn for Gaussian method")
                        return

                    h = float(sympify(self.h_single_entry.get(), locals={'pi': pi, 'e': E})) if self.h_single_entry.get() else None
                    n = int((xn-x0)/h)
                    results_text = f"Single Integration - {self.integration_method.get().replace('_', ' ').title()}\n"
                    results_text += f"Function: f(x) = {function_str}\n"
                    results_text += f"Limits: x₀ = {x0}, xN = {xn}\n"    
                    
                    integral_data = {}
                    if self.integration_method.get() == 'romberg':
                        messagebox.showinfo("Info", "Romberg method isn't active yet for single integral")
                        return  
                    elif self.integration_method.get() == 'gaussian':
                        val = singlefunctions[self.integration_method.get()](f,x0,xn)
                        results_text += f"The integral under 2 points : {val['two']:.6f}, 3 points : {val['three']:.6f}\n"
                        integral_data['integral_value'] = f"2 points: {val['two']:.6f}, 3 points: {val['three']:.6f}" # Storing string for gaussian
                        integral_data['data'] = []  # Gaussian doesn't provide a continuous array of points for visualising like trapezoidal
                        integral_data['graph'] = []
                    elif self.integration_method.get() == 'all':
                        all_results_string = ""
                        x_vals_for_plot = None
                        y_vals_for_plot = None
                        for method_name, method_func in singlefunctions.items():
                            if method_name in ['romberg', 'gaussian', 'all']: # Skip romberg and special handling for gaussian
                                continue
                            if h is None: # Should have been caught earlier, but defensive check
                                continue 
                            current_result = method_func(x0, xn, h, f)
                            all_results_string += f"Integral by {method_name.replace('_', ' ').title()} method: {current_result['integral_value']:.6f}\n"
                            if x_vals_for_plot is None: # Use one method's x-values for plot if available
                                x_vals_for_plot = current_result.get('x_values', [])
                            if y_vals_for_plot is None: # Use one method's y-values for plot if available
                                y_vals_for_plot = current_result.get('y_values', [])
                        
                        gauss_val = singlefunctions['gaussian'](f, x0, xn)
                        all_results_string += f"Integral by Gaussian method (2 points): {gauss_val['two']:.6f}\n"
                        all_results_string += f"Integral by Gaussian method (3 points): {gauss_val['three']:.6f}\n"

                        results_text += "\n" + all_results_string
                        integral_data['integral_value'] = all_results_string # Store concatenated string
                        # For plotting 'all', might need a representative plot, e.g., trapezoidal or Simpson's
                        # Here, we'll just plot the function itself and the points, if any single method provides them.
                        integral_data['data'] = y_vals_for_plot # Store some y-values for array output if applicable

                    else: # trapezoidal, simpsons, simpsons38
                        if h is None: # Should not happen if previous check is good
                            messagebox.showerror("Error", "Step size 'h' is required for this method.")
                            return
                        results_text += f"Step size: h = {h}\n\n"
                        current_result = singlefunctions[self.integration_method.get()](x0,xn,h,f)
                        results_text += f"The integral is {current_result['integral_value']:.6f}\n"
                        integral_data = current_result
                    
                    self.integration_results_text.delete(1.0, tk.END)
                    self.integration_results_text.insert(1.0, results_text)

                    # Array output for single integral (if available)
                    array_text = "Function values (y-values at integration points):\n"
                    if 'data' in integral_data and integral_data['data']:
                        temp = x0
                        array_text += f"{'i':>3} {'x':>6} {'y':>12}\n"
                        array_text += "-" * 25 + "\n"
                        for i, val in enumerate(integral_data['data']):
                            array_text += f"{i:3} {temp+i*h:7.4f} {val:12.6f}\n"
                    else:
                        array_text += "No detailed array output for this method or configuration.\n"

                    self.array_output_text.delete(1.0, tk.END)
                    self.array_output_text.insert(1.0, array_text)

                    # Plotting for single integral
                    self.integration_ax.clear()
                    if integral_data['data']:
                        x_vals = [x0+i*h for i in range(n+1)]
                        x_plot = np.linspace(x0,xn,100)
                        self.integration_ax.plot(x_plot,f(x_plot),'b-',label="Function")
                        self.integration_plot(integral_data['graph'], x_vals)
                    else:
                        # If a method like Gaussian doesn't provide explicit x/y values, just try to plot the function
                        x_plot = np.linspace(x0, xn, 100)
                        y_plot = [f(val) for val in x_plot]
                        self.integration_ax.plot(x_plot, y_plot, 'b-', label='Function f(x)')
                        self.integration_ax.fill_between(x_plot, y_plot, color='lightblue', alpha=0.5, label='Area under curve')
                    self.integration_ax.set_xlabel('x')
                    self.integration_ax.set_ylabel('f(x)')
                    self.integration_ax.set_title(f'Single Integral: {self.integration_method.get().replace("_", " ").title()} Method')
                    self.integration_ax.legend()
                    self.integration_ax.grid(True, alpha=0.3)
                    self.integration_canvas.draw()
                except Exception as e:
                    messagebox.showerror("Error", f"Error in single integral calculation: {str(e)}")
                    return
            else:  # Double integral
                try:
                    f = string_to_function(function_str, integration_type="double")
                    x0 = float(sympify(self.x0_double_entry.get(), locals={'pi': pi, 'e': E}))
                    xn = float(sympify(self.xn_double_entry.get(), locals={'pi': pi, 'e': E}))
                    y0 = float(sympify(self.y0_entry.get(), locals={'pi': pi, 'e': E}))
                    yn = float(sympify(self.yn_entry.get(), locals={'pi': pi, 'e': E}))
                    h = float(sympify(self.h_double_entry.get(), locals={'pi': pi, 'e': E}))
                    k = float(sympify(self.k_entry.get(), locals={'pi': pi, 'e': E}))

                    if(self.integration_method.get() in ['romberg', 'gaussian']):
                        messagebox.showinfo("Info", f"{self.integration_method.get().replace('_', ' ').title()} method isn't active yet for double integral")
                        return
                    
                    if not all([self.x0_double_entry.get(), self.xn_double_entry.get(),
                        self.y0_entry.get(), self.yn_entry.get(),
                        self.h_double_entry.get(), self.k_entry.get()]):
                        messagebox.showerror("Error", "Please fill all double integral parameters")
                        return

                    if self.integration_method.get() != 'all':
                        integral_result = doublefunctions[self.integration_method.get()](x0, xn, y0, yn, h, k, f)    
                        results_text = f"Double Integration - {self.integration_method.get().replace('_', ' ').title()}\n"
                        results_text += f"Function: f(x,y) = {function_str}\n"
                        results_text += f"X limits: x₀ = {x0}, xN = {xn}, h = {h}\n"
                        results_text += f"Y limits: y₀ = {y0}, yN = {yn}, k = {k}\n\n"
                        results_text += f"The integral is {integral_result['integral_value']:.6f}\n"
                    else:
                        results_text = f"Double Integration - All Methods\n"
                        results_text += f"Function: f(x,y) = {function_str}\n"
                        results_text += f"X limits: x₀ = {x0}, xN = {xn}, h = {h}\n"
                        results_text += f"Y limits: y₀ = {y0}, yN = {yn}, k = {k}\n\n"
                        integral_result = dintegrate(x0, xn, y0, yn, h, k, f)
                        for method_name, res in integral_result.items():
                            results_text += f"The integral by {method_name.replace('_', ' ').title()} method is {res['integral_value']:.6f}\n"

                    # Display results
                    self.integration_results_text.delete(1.0, tk.END)
                    self.integration_results_text.insert(1.0, results_text)
                    
                    # Array output
                    array_text = "Function values (matrix form):\n"
                    # For 'all' method, we might just show one representative array or need more complex logic
                    if 'data' in integral_result and integral_result['data']:
                        xlen = int((xn-x0) / h) + 1
                        ylen = int((yn-y0) / k) + 1 # Use k for y-steps
                        data_array = np.array(integral_result['data']).reshape((ylen, xlen)) # Reshape to matrix

                        for row in data_array:
                            array_text += " ".join([f"{val:.4f}" for val in row]) + "\n"
                    else:
                        array_text += "No detailed array output for this method.\n"

                    self.array_output_text.delete(1.0, tk.END)
                    self.array_output_text.insert(1.0, array_text)
                    
                    messagebox.showinfo("Success", f"Integration setup complete for {self.integration_method.get().replace('_', ' ').title()} method")
                    
                    # Plot for double integral (3D plot)
                    x_vals_plot = np.arange(x0, xn + h/2, h)
                    y_vals_plot = np.arange(y0, yn + k/2, k)
                    X, Y = np.meshgrid(x_vals_plot, y_vals_plot)
                    Z = np.array([[f(x, y) for x in x_vals_plot] for y in y_vals_plot])

                    self.integration_ax.clear()
                    self.integration_fig.clear() # Clear entire figure for 3D plot
                    self.integration_ax = self.integration_fig.add_subplot(111, projection='3d') # Add 3D subplot
                    
                    if self.integration_method.get() not in ['all', 'gaussian','romberg']:
                        fn = integral_result['graph']
                        messagebox.showinfo("Debug", f"Plotting with fn: {type(fn)}")
                        self.integration_plot(fn, x_vals_plot, y_vals_plot)

                    self.integration_ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
                    self.integration_ax.set_xlabel('x')
                    self.integration_ax.set_ylabel('y')
                    self.integration_ax.set_zlabel('f(x,y)')
                    self.integration_ax.set_title(f'Double Integral: {self.integration_method.get().replace("_", " ").title()} Method')
                    self.integration_canvas.draw()


                except ValueError as e:
                    messagebox.showerror("Error", f"Please enter valid numeric values for double integral parameters: {str(e)}")
                    return
                except Exception as e:
                    messagebox.showerror("Error", f"Double integration failed: {str(e)}")
                    return
            
        except Exception as e:
            messagebox.showerror("Error", f"Integration setup failed: {str(e)}")
    
    # Helper method to consolidate plotting logic for interpolation tab
    def _update_interpolation_plot(self):
        self.ax.clear()

        # Plot interpolated function if available
        if self.current_func or self.current_spline:
            x_vals_interp = [p[0] for p in self.points]
            y_vals_interp = [p[1] for p in self.points]
            
            # Use a slightly wider range for interpolation curve for visual clarity
            x_min_interp, x_max_interp = min(x_vals_interp), max(x_vals_interp)
            x_range_interp = x_max_interp - x_min_interp
            if x_range_interp > 0:
                x_plot_interp = np.linspace(x_min_interp, x_max_interp, 500)
            else: # Case of a single point or all points at the same x-value
                x_plot_interp = np.linspace(x_min_interp , x_max_interp , 500)

            if self.interpolation_type.get() in ["lagrange", "hermitian"]:
                y_plot_interp = [self.current_func(i) for i in x_plot_interp]
            else:  # Cubic Spline
                y_plot_interp = [self.current_spline(i) for i in x_plot_interp]
            
            self.ax.plot(x_plot_interp, y_plot_interp, 'b-', linewidth=2, label=f'{self.interpolation_type.get().title()} Interpolation')
            self.ax.plot(x_vals_interp, y_vals_interp, 'ro', markersize=8, label='Data Points')
            
            for i, (x_p, y_p) in enumerate(zip(x_vals_interp, y_vals_interp)):
                self.ax.annotate(f'({x_p:.2f}, {y_p:.2f})', (x_p, y_p), xytext=(5, 5), 
                               textcoords='offset points', fontsize=8)
        
        self.ax.grid(True, alpha=0.3)
        # self.ax.legend()
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.set_title('Interpolation Plot') # Changed title slightly
        self.canvas.draw()


    def on_type_change(self):
        """Handle interpolation type change"""
        if self.interpolation_type.get() == 'spline':
            messagebox.showinfo("Info", "Under progress")
            return
        if self.interpolation_type.get() == "hermitian":
            # Show derivative input
            self.deriv_label.grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
            self.deriv_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(5, 0))
        else:
            # Hide derivative input
            self.deriv_label.grid_remove()
            self.deriv_entry.grid_remove()
        
        # Clear evaluation result
        self.eval_result.config(text="Result: ")
        self.update_points_display()
        self._update_interpolation_plot() # Update plot to reflect type change
    
    def add_points(self):
        """Add points from comma-separated input"""
        try:
            # Parse X values
            x_input = self.x_entry.get().strip()
            y_input = self.y_entry.get().strip()
            
            if not x_input or not y_input:
                messagebox.showerror("Error", "Please enter both X and Y values")
                return
            
            # Split and convert to float using sympify
            x_values = [float(sympify(x.strip(), locals={'pi': pi, 'e': E})) for x in x_input.split(',') if x.strip()]
            y_values = [float(sympify(y.strip(), locals={'pi': pi, 'e': E})) for y in y_input.split(',') if y.strip()]
            
            if len(x_values) != len(y_values):
                messagebox.showerror("Error", "Number of X and Y values must be equal")
                return
            
            # Handle derivatives for Hermitian
            if self.interpolation_type.get() == "hermitian":
                deriv_input = self.deriv_entry.get().strip()
                if not deriv_input:
                    messagebox.showerror("Error", "Please enter derivative values for Hermitian interpolation")
                    return
                
                deriv_values = [float(sympify(d.strip(), locals={'pi': pi, 'e': E})) for d in deriv_input.split(',') if d.strip()]
                if len(deriv_values) != len(x_values):
                    messagebox.showerror("Error", "Number of derivative values must equal number of points")
                    return
                
                # Clear existing derivatives and add new ones
                self.derivatives.clear()
                self.derivatives.extend(deriv_values)
            
            # Clear existing points and add new ones
            self.points.clear()
            for x_val, y_val in zip(x_values, y_values):
                self.points.append((x_val, y_val))
            
            self.update_points_display()
            self._update_interpolation_plot()
            
            # Show success message
            messagebox.showinfo("Success", f"Added {len(x_values)} points successfully")
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numeric values or expressions (e.g., 2*pi, e^2, sin(pi/2)) separated by commas")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add points: {str(e)}")
    
    def clear_input(self):
        """Clear input fields"""
        self.x_entry.delete(0, tk.END)
        self.y_entry.delete(0, tk.END)
        if hasattr(self, 'deriv_entry'):
            self.deriv_entry.delete(0, tk.END)
    
    def add_point(self):
        """Legacy method - kept for compatibility"""
        self.add_points()
    
    def remove_point(self):
        """Remove selected point"""
        selection = self.points_listbox.curselection()
        if selection:
            index = selection[0]
            self.points.pop(index)
            if self.interpolation_type.get() == "hermitian" and index < len(self.derivatives):
                self.derivatives.pop(index)
            self.update_points_display()
            self._update_interpolation_plot() # Update plot after point removal
    
    def clear_points(self):
        """Clear all points"""
        self.points.clear()
        self.derivatives.clear()
        self.current_poly = None
        self.current_func = None
        self.current_spline = None
        self.eval_result.config(text="Result: ")
        self.update_points_display()
        self.ax.clear()
        self.canvas.draw()
        self.poly_text.delete(1.0, tk.END)
    
    def update_points_display(self):
        """Update the points listbox"""
        self.points_listbox.delete(0, tk.END)
        for i, (x_val, y_val) in enumerate(self.points):
            if self.interpolation_type.get() == "hermitian" and i < len(self.derivatives):
                text = f"({x_val}, {y_val}, y'={self.derivatives[i]})"
            else:
                text = f"({x_val}, {y_val})"
            self.points_listbox.insert(tk.END, text)
    
    def format_polynomial_clean(self, coeffs):
        temp = ''
        n = len(coeffs)
        for i in range(n):
            coeff_val = float(coeffs[i]) # Ensure coeff is float for cleaner formatting
            if(abs(coeff_val) > 1e-9): # Ignore very small coefficients
                sign = " + " if coeff_val >= 0 and i > 0 else " - " if coeff_val < 0 else ""
                abs_coeff = abs(coeff_val)
                term = f"{abs_coeff:.6g}" # Format coefficient cleanly
                
                if n-i-1 == 0: # Constant term
                    temp += f"{sign}{term}"
                elif n-i-1 == 1: # x term
                    temp += f"{sign}{term}*x"
                else: # x^power term
                    temp += f"{sign}{term}*x^{n-i-1}"
        
        if not temp.strip(): # If all coefficients were zero or very small
            return "0"
        
        # Clean up leading '+' if present
        if temp.strip().startswith('+'):
            # Check if it's " + 0" or similar, if so return "0"
            if temp.strip()[3:].strip() == "0":
                return "0"
            return temp.strip()[3:] # Remove ' + '
        elif temp.strip().startswith('-'):
            return temp.strip()[1:] # Keep '-' but remove leading space
        return temp.strip() # Should already be good


    def calculate_interpolation(self):
        """Calculate and display interpolation"""
        if len(self.points) < 2:
            messagebox.showerror("Error", "Please enter at least 2 points")
            return
        
        if self.interpolation_type.get() == "hermitian" and len(self.derivatives) != len(self.points):
            messagebox.showerror("Error", "Please provide derivatives for all points in Hermitian interpolation")
            return
        
        try:
            # Extract x and y values
            x_vals = [p[0] for p in self.points]
            y_vals = [p[1] for p in self.points]
            
            # Check for duplicate x values
            if len(set(x_vals)) != len(x_vals):
                messagebox.showerror("Error", "Duplicate x values are not allowed")
                return
            
            # Sort points by x value
            if self.interpolation_type.get() == "hermitian":
                combined_data = sorted(zip(x_vals, y_vals, self.derivatives))
                x_vals = [d[0] for d in combined_data]
                y_vals = [d[1] for d in combined_data]
                self.derivatives = [d[2] for d in combined_data]
            else:
                combined_data = sorted(zip(x_vals, y_vals))
                x_vals = [d[0] for d in combined_data]
                y_vals = [d[1] for d in combined_data]
            
            poly_text = ""

            # Calculate interpolation
            if self.interpolation_type.get() == "lagrange":
                x = var('x')
                self.current_poly, self.current_func, _ = lagrange(x_vals, y_vals)
                # Get coefficients for display
                max_degree = len(x_vals) - 1
                coeffs = [self.current_poly.coeff(x, i) for i in range(max_degree + 1)]
                coeffs.reverse()  # Highest degree first
                
                polynomial_str = self.format_polynomial_clean(coeffs)
                poly_text = f"Lagrange Polynomial:\nP(x) = {polynomial_str}\n\n"
                
            elif self.interpolation_type.get() == "hermitian":
                x = var('x')
                self.current_poly, self.current_func, _ = hermitian(x_vals, y_vals, self.derivatives)
                
                # Get coefficients for display
                max_degree = 2 * len(x_vals) - 1
                coeffs = [self.current_poly.coeff(x, i) for i in range(max_degree + 1)]
                coeffs.reverse()  # Highest degree first
                
                polynomial_str = self.format_polynomial_clean(coeffs)
                poly_text = f"Hermitian Polynomial:\nP(x) = {polynomial_str}\n\n"
                
            else:  # Cubic Spline 
                x = var('x')
                self.current_poly, self.current_spline, self.Mvalues = cubic(x_vals, y_vals)           #removed d spline (differential )
                # For splines, show piecewise polynomials
                poly_text = "Cubic Spline Interpolation:\n The M-values are : "
                for i in range(len(self.Mvalues)):
                    poly_text += f"  M_{i} = {self.Mvalues[i]:.3f}, "
                poly_text += f"\nPiecewise cubic polynomials between {len(x_vals)} points\n\n"
                
                # Show the cubic polynomial pieces
                for i in range(len(x_vals) - 1):
                    poly_text += f"Interval [{x_vals[i]:.3f}, {x_vals[i+1]:.3f}]:\n"
                    # Get coefficients for this piece
                    coeffs = [self.current_poly[i].coeff(x, j) for j in range(4)]
                    poly_text += f"  S_{i}(x) = {self.format_polynomial_clean(coeffs)}\n"
            
            # Plot
            self._update_interpolation_plot() # Use the helper to replot interpolation
            
            # Display polynomial and data points
            poly_text += "Data Points:\n"
            for i, (x_p, y_p) in enumerate(zip(x_vals, y_vals)):
                if self.interpolation_type.get() == "hermitian":
                    poly_text += f"  ({x_p}, {y_p}), y'({x_p}) = {self.derivatives[i]}\n"
                else:
                    poly_text += f"  ({x_p}, {y_p})\n"
            
            self.poly_text.delete(1.0, tk.END)
            self.poly_text.insert(1.0, poly_text)
            
            # Clear previous evaluation result
            self.eval_result.config(text="Result: ")
            
        except Exception as e:
            messagebox.showerror("Error", f"Calculation failed: {str(e)}")
    
    def evaluate_function(self):
        """Evaluate the interpolating function at a given point"""
        if not self.current_func and not self.current_spline:
            messagebox.showerror("Error", "Please calculate interpolation first")
            return
        
        try:
            x_val = float(sympify(self.eval_entry.get(), locals={'pi': pi, 'e': E}))
            
            if self.interpolation_type.get() in ["lagrange", "hermitian"]:
                result = self.current_func(x_val)
            else:  # Cubic Spline
                result = float(self.current_spline(x_val))

            self.eval_result.config(text=f"Result: f({x_val}) = {result:.6f}")
            
            # Add evaluation point to plot
            self.ax.plot(x_val, result, 'ko', markersize=10, label=f'Evaluated f({x_val}) = {result:.3f}') 
            self.ax.legend()
            self.canvas.draw()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric value or expression (e.g., 2*pi, e^2, sin(pi/2))")
        except Exception as e:
            messagebox.showerror("Error", f"Evaluation failed: {str(e)}")
       
if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    root.mainloop()