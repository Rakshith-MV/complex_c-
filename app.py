from sympy import var, symbols, diff, sympify, E, sin, cos, tan, log, sqrt, exp
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from interpolation import lagrange, hermitian, cubic
from nintegration import dintegrate, simpsons382d_integrate, sintegrate, trapezoidal1d_integrate, trapezoidal2d_integrate, simpsons1d_integrate , simpsons2d_integrate,  simpsons381d_integrate, simpsons382d_integrate, gaussian, romberg_integration
from numpy import pi
from support import string_to_function

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

class InterpolationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Interpolation & Integration Calculator")
        self.root.geometry("1400x900")
        
        # Variables
        self.points = []
        self.derivatives = []  # For Hermitian interpolation
        self.interpolation_type = tk.StringVar(value="lagrange")
        self.current_poly = None
        self.current_func = None
        self.current_spline = None
        
        # Integration variables
        self.integration_type = tk.StringVar(value="single")
        self.integration_method = tk.StringVar(value="simpsons13")
        self.integration_results = None
        
        self.setup_gui()
        
    def setup_gui(self):
        # Create main notebook for tabs
        self.main_notebook = ttk.Notebook(self.root)
        self.main_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create interpolation and integration tabs
        self.setup_interpolation_tab()
        self.setup_integration_tab()
        
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
                        value="all").pack(side=tk.LEFT, padx=(0,10))
        
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
        
        ttk.Label(single_grid, text="x₀:").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        self.x0_entry = ttk.Entry(single_grid, width=10)
        self.x0_entry.grid(row=0, column=1, padx=(0, 15))
        
        ttk.Label(single_grid, text="xₙ:").grid(row=0, column=2, padx=(0, 5), sticky=tk.W)
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
        ttk.Label(double_grid, text="x₀:").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        self.x0_double_entry = ttk.Entry(double_grid, width=8)
        self.x0_double_entry.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(double_grid, text="xₙ:").grid(row=0, column=2, padx=(0, 5), sticky=tk.W)
        self.xn_double_entry = ttk.Entry(double_grid, width=8)
        self.xn_double_entry.grid(row=0, column=3, padx=(0, 10))
        
        ttk.Label(double_grid, text="h:").grid(row=0, column=4, padx=(0, 5), sticky=tk.W)
        self.h_double_entry = ttk.Entry(double_grid, width=8)
        self.h_double_entry.grid(row=0, column=5, padx=(0, 10))
        
        # Second row
        ttk.Label(double_grid, text="y₀:").grid(row=1, column=0, padx=(0, 5), sticky=tk.W, pady=(5, 0))
        self.y0_entry = ttk.Entry(double_grid, width=8)
        self.y0_entry.grid(row=1, column=1, padx=(0, 10), pady=(5, 0))
        
        ttk.Label(double_grid, text="yₙ:").grid(row=1, column=2, padx=(0, 5), sticky=tk.W, pady=(5, 0))
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
        
    def on_integration_type_change(self):
        """Handle integration type change"""
        if self.integration_type.get() == "single":
            self.single_frame.grid()
            self.double_frame.grid_remove()
        else:
            self.single_frame.grid_remove()
            self.double_frame.grid()
    
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
                    f = string_to_function(function_str)
                    x0 = float(sympify(self.x0_entry.get(), locals={'pi': pi, 'e': E}))
                    xn = float(sympify(self.xn_entry.get(), locals={'pi': pi, 'e': E}))
                    h = float(sympify(self.h_single_entry.get(), locals={'pi': pi, 'e': E}))

                    if(self.integration_method.get() != 'romberg'):
                        results_text = f"Single Integration - {self.integration_method.get().replace('_', ' ').title()}\n"
                        results_text += f"Function: f(x) = {function_str}\n"
                        results_text += f"Limits: x₀ = {x0}, xₙ = {xn}\n"    
                        if(self.integration_method.get() != 'gaussian'):
                            if not all([self.x0_entry.get(), self.xn_entry.get(), self.h_single_entry.get()]):
                                messagebox.showerror("Error", "Please fill all single integral parameters")
                                return
                            results_text += f"Step size: h = {h}\n\n"
                            results_text += f"The integral is {  singlefunctions[self.integration_method.get()](x0,xn,h,f)['integral_value']}\n"
                        else:
                            if not all([self.x0_entry.get(), self.xn_entry.get()]):
                                messagebox.showerror("Error", "Please fill all single integral parameters")
                                return
                            val = singlefunctions[self.integration_method.get()](f,x0,xn)
                            results_text += f"The integral under 2 points {val['two']}, 3 points : {val['three']}\n"
                except:
                    messagebox.showerror("Error", "Please enter valid numeric values for single integral parameters")
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


                    if(self.integration_method.get() not in  ['romberg', 'gaussian','all']):
                        if not all([self.x0_double_entry.get(), self.xn_double_entry.get(),
                            self.y0_entry.get(), self.yn_entry.get(),
                            self.h_double_entry.get(), self.k_entry.get()]):
                            messagebox.showerror("Error", "Please fill all double integral parameters")
                            return

                        xlen = int((xn - x0) / h)+1
                        ylen = int((yn-y0)/h) +1
                        
                        integral = doublefunctions[self.integration_method.get()](x0, xn, y0, yn, h, k, f)    
                    if self.integration_method.get() != 'all':
                        string = f"The integral in {self.integration_method.get()} method is {integral['integral_value']}\n" 
                    else:
                        string = ''
                        for i,j in integral.items():
                            string += f"The integral in {i} method is {j['integral_value']}\n"
                    # Display input parameters
                    results_text = f"Double Integration - {self.integration_method.get().replace('_', ' ').title()}\n"
                    results_text += f"Function: f(x,y) = {function_str}\n"
                    results_text += f"X limits: x₀ = {x0}, xₙ = {xn}, h = {h}\n"
                    results_text += f"Y limits: y₀ = {y0}, yₙ = {yn}, k = {k}\n\n"
                    results_text += f"The integral is {integral['integral_value']}"
                except ValueError:
                    messagebox.showerror("Error", "Please enter valid numeric values for double integral parameters")
                    return
            
            # Display results (placeholder)
            self.integration_results_text.delete(1.0, tk.END)
            self.integration_results_text.insert(1.0, results_text)
            
            array_text = "Function values:\n"
            for i,j in enumerate(integral['data']):
                array_text += str(round(j, 4)) + '  '
                array_text += ((i+1)%ylen == 0)*"\n"
            
            self.array_output_text.delete(1.0, tk.END)
            self.array_output_text.insert(1.0, array_text)
            
            messagebox.showinfo("Success", f"Integration setup complete for {self.integration_method.get().replace('_', ' ').title()} method")
            
            x_val = [x0+i*h for i in range(xlen)]
            y_val = [y0+i*h for i in range(ylen)]
            f_val = [[f(i,j) for i in x_val] for j in y_val]
            
            # self.ax.clear()
            # self.ax.plot_surface(x_val, y_val, f_val, cmap='viridis')
            # self.ax.legend()
            # self.canvas.draw()


        except Exception as e:
            messagebox.showerror("Error", f"Integration setup failed: {str(e)}")
    
    # Keep all existing interpolation methods unchanged
    def on_type_change(self):
        """Handle interpolation type change"""
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
            for x, y in zip(x_values, y_values):
                self.points.append((x, y))
            
            self.update_points_display()
            
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
        for i, (x, y) in enumerate(self.points):
            if self.interpolation_type.get() == "hermitian" and i < len(self.derivatives):
                text = f"({x}, {y}, y'={self.derivatives[i]})"
            else:
                text = f"({x}, {y})"
            self.points_listbox.insert(tk.END, text)
    
    def format_polynomial_clean(self, coeffs):
        temp = ''
        n = len(coeffs)
        # print("start polynomials")
        for i in range(n):
            if(coeffs[i]!=0):
                temp += f" + {coeffs[i]}*x^{n-i-1}"
        # print(temp)
        return temp[3:-3]  # Remove trailing " + "
    
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
            sorted_data = sorted(zip(x_vals, y_vals, self.derivatives if self.interpolation_type.get() == "hermitian" else [0]*len(x_vals)))
            x_vals = [d[0] for d in sorted_data]
            y_vals = [d[1] for d in sorted_data]
            if self.interpolation_type.get() == "hermitian":
                self.derivatives = [d[2] for d in sorted_data]
            
            # Generate x values for plotting
            x_min, x_max = min(x_vals), max(x_vals)
            x_range = x_max - x_min
            x_plot = np.linspace(x_min - 0.2*x_range, x_max + 0.2*x_range, 500)
            
            # Calculate interpolation
            if self.interpolation_type.get() == "lagrange":
                x = var('x')
                print("Started lagrange")
                self.current_poly, self.current_func, _ = lagrange(x_vals, y_vals)
                y_plot = [self.current_func(i) for i in x_plot]
                print("CComputed lagrange")
                # Get coefficients for display
                max_degree = len(x_vals) - 1
                coeffs = [self.current_poly.coeff(x, i) for i in range(max_degree + 1)]
                coeffs.reverse()  # Highest degree first
                
                polynomial_str = self.format_polynomial_clean(coeffs)
                poly_text = f"Lagrange Polynomial:\nP(x) = {polynomial_str}\n\n"
                
            elif self.interpolation_type.get() == "hermitian":
                x = var('x')
                self.current_poly, self.current_func, _ = hermitian(x_vals, y_vals, self.derivatives)
                y_plot = [self.current_func(i) for i in x_plot]
                
                # Get coefficients for display
                max_degree = 2 * len(x_vals) - 1
                coeffs = [self.current_poly.coeff(x, i) for i in range(max_degree + 1)]
                coeffs.reverse()  # Highest degree first
                
                polynomial_str = self.format_polynomial_clean(coeffs)
                poly_text = f"Hermitian Polynomial:\nP(x) = {polynomial_str}\n\n"
                
            else:  # Cubic Spline
                x = var('x')
                self.current_poly, self.current_spline, self.current_dspline, self.Mvalues = cubic(x_vals, y_vals)
                y_plot = [self.current_spline(i) for i in x_plot]
                
                # For splines, show piecewise polynomials
                poly_text = "Cubic Spline Interpolation:\n The M-values are : "
                for i in self.Mvalues:
                    poly_text += f"  M_{i} = {self.Mvalues[i]:.3f}, "
                poly_text += f"\nPiecewise cubic polynomials between {len(x_vals)} points\n\n"
                
                # Show the cubic polynomial pieces
                for i in range(len(x_vals) - 1):
                    poly_text += f"Interval [{x_vals[i]:.3f}, {x_vals[i+1]:.3f}]:\n"
                    # Get coefficients for this piece
                    coeffs = [self.current_poly[i].coeff(x, j) for j in range(4)]
                    poly_text += f"  S_{i}(x) = {self.format_polynomial_clean(coeffs)}\n"
            
            # Plot
            self.ax.clear()
            self.ax.plot(x_plot, y_plot, 'b-', linewidth=2, label=f'{self.interpolation_type.get().title()} Interpolation')
            self.ax.plot(x_vals, y_vals, 'ro', markersize=8, label='Data Points')
            
            # Add point labels
            for i, (x, y) in enumerate(zip(x_vals, y_vals)):
                self.ax.annotate(f'({x:.2f}, {y:.2f})', (x, y), xytext=(5, 5), 
                               textcoords='offset points', fontsize=8)
            
            self.ax.grid(True, alpha=0.3)
            self.ax.legend()
            self.ax.set_xlabel('x')
            self.ax.set_ylabel('y')
            self.ax.set_title(f'{self.interpolation_type.get().title()} Interpolation')
            
            self.canvas.draw()
            
            # Display polynomial and data points
            poly_text += "Data Points:\n"
            for i, (x, y) in enumerate(zip(x_vals, y_vals)):
                if self.interpolation_type.get() == "hermitian":
                    poly_text += f"  ({x}, {y}), y'({x}) = {self.derivatives[i]}\n"
                else:
                    poly_text += f"  ({x}, {y})\n"
            
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
            x_val = float(sympify(self.eval_entry.get(), locals={'pi': pi, 'e': np.exp(1)}))
            
            if self.interpolation_type.get() in ["lagrange", "hermitian"]:
                result = self.current_func(x_val)
            else:  # Cubic Spline
                result = float(self.current_spline(x_val))

            self.eval_result.config(text=f"Result: f({x_val}) = {result:.6f}")
            
            # Add evaluation point to plot
            self.ax.plot(x_val, result, 'go', markersize=10, label=f'f({x_val}) = {result:.3f}')
            self.ax.legend()
            self.canvas.draw()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric value or expression (e.g., 2*pi, e^2, sin(pi/2))")
        except Exception as e:
            messagebox.showerror("Error", f"Evaluation failed: {str(e)}")
       
if __name__ == "__main__":
    root = tk.Tk()
    app = InterpolationGUI(root)
    root.mainloop()