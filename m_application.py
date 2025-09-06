# toga_app.py
# Converted from your tkinter implementation into a Toga desktop app.
# Save as toga_app.py and run: python toga_app.py
# Requirements: pip install toga sympy numpy matplotlib

import os
import tempfile
from sympy import var, sympify, E
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import numpy as np
import matplotlib.pyplot as plt

# Import your modules (keep these files next to this script)
from interpolation import lagrange, hermitian, cubic
from nintegration import (
    dintegrate,
    sintegrate,
    trapezoidal1d_integrate,
    trapezoidal2d_integrate,
    simpsons1d_integrate,
    simpsons2d_integrate,
    simpsons381d_integrate,
    simpsons382d_integrate,
    gaussian,
    romberg_integration,
)
from support import string_to_function
from numpy import pi

# Mapping like your original script
singlefunctions = {
    "trapezoidal": trapezoidal1d_integrate,
    "simpsons": simpsons1d_integrate,
    "simpsons38": simpsons381d_integrate,
    "gaussian": gaussian,
    "romberg": romberg_integration,
    "all": sintegrate,
}
doublefunctions = {
    "trapezoidal": trapezoidal2d_integrate,
    "simpsons": simpsons2d_integrate,
    "simpsons38": simpsons382d_integrate,
    "all": dintegrate,
}


class InterpolationApp(toga.App):
    def startup(self):
        # Main window
        self.main_window = toga.MainWindow(title='NA')

        # State
        self.points = []
        self.derivatives = []
        self.current_poly = None
        self.current_func = None
        self.current_spline = None
        self.Mvalues = {}

        # Top-level container
        outer = toga.Box(style=Pack(direction=COLUMN, padding=10))

        # Tabs (OptionContainer works like Notebook)
        self.tabs = toga.OptionContainer()
        outer.add(self.tabs)

        # ---- Interpolation Tab ----
        interp_box = toga.Box(style=Pack(direction=ROW, padding=10))

        # Left column (inputs)
        left = toga.Box(style=Pack(direction=COLUMN, width=350, padding_right=10))

        left.add(toga.Label("Interpolation Type", style=Pack(padding_bottom=5)))
        self.interp_select = toga.Selection(
            items=["lagrange", "hermitian", "spline"],
            on_select=self.on_type_change,
            style=Pack(padding_bottom=10),
        )
        self.interp_select.value = "lagrange"
        left.add(self.interp_select)

        left.add(toga.Label("Input Data (comma-separated, supports pi, e, sin, cos, etc.)", style=Pack(padding_bottom=5)))
        left.add(toga.Label("X values:", style=Pack(padding_top=5)))
        self.x_input = toga.TextInput(placeholder="e.g. 0, 1, 2", style=Pack(width=300))
        left.add(self.x_input)

        left.add(toga.Label("Y values:", style=Pack(padding_top=5)))
        self.y_input = toga.TextInput(placeholder="e.g. 1, 2, 3", style=Pack(width=300))
        left.add(self.y_input)

        left.add(toga.Label("Y' values (for Hermitian):", style=Pack(padding_top=5)))
        self.deriv_input = toga.TextInput(placeholder="e.g. 0.0, 0.0, 0.0", style=Pack(width=300))
        left.add(self.deriv_input)

        # Buttons
        btns = toga.Box(style=Pack(direction=ROW, padding_top=10))
        btns.add(toga.Button("Add Points", on_press=self.add_points))
        btns.add(toga.Button("Clear Input", on_press=self.clear_input, style=Pack(padding_left=6)))
        left.add(btns)

        left.add(toga.Label("Current Points:", style=Pack(padding_top=10)))
        self.points_display = toga.MultilineTextInput(readonly=True, style=Pack(height=140, width=330))
        left.add(self.points_display)

        left.add(toga.Box(style=Pack(height=6)))  # spacer

        action_row = toga.Box(style=Pack(direction=ROW, padding_top=8))
        action_row.add(toga.Button("Remove Last", on_press=self.remove_last_point))
        action_row.add(toga.Button("Clear All", on_press=self.clear_points, style=Pack(padding_left=6)))
        action_row.add(toga.Button("Calculate", on_press=self.calculate_interpolation, style=Pack(padding_left=6)))
        left.add(action_row)

        # Evaluate
        left.add(toga.Label("Evaluate at x:", style=Pack(padding_top=10)))
        eval_row = toga.Box(style=Pack(direction=ROW))
        self.eval_input = toga.TextInput(placeholder="e.g. pi/2")
        eval_row.add(self.eval_input)
        eval_row.add(toga.Button("Find Value", on_press=self.evaluate_function, style=Pack(padding_left=6)))
        left.add(eval_row)
        self.eval_result_label = toga.Label("Result: ", style=Pack(padding_top=6))
        left.add(self.eval_result_label)

        interp_box.add(left)

        # Right column (plot + polynomial output)
        right = toga.Box(style=Pack(direction=COLUMN, flex=1))

        # Plot display (as image)
        right.add(toga.Label("Plot:", style=Pack(padding_bottom=6)))
        self.plot_image = toga.ImageView(image=None, style=Pack(height=360))
        right.add(self.plot_image)

        # Polynomial / expression text area
        right.add(toga.Label("Polynomial / Expression:", style=Pack(padding_top=10)))
        self.poly_text = toga.MultilineTextInput(readonly=True, style=Pack(flex=1))
        right.add(self.poly_text)

        interp_box.add(right)

        self.tabs.add("Interpolation", interp_box)

        # ---- Integration Tab ----
        integ_box = toga.Box(style=Pack(direction=ROW, padding=10))

        left_i = toga.Box(style=Pack(direction=COLUMN, width=350, padding_right=10))
        left_i.add(toga.Label("Integration Type:", style=Pack(padding_bottom=5)))
        self.integration_select = toga.Selection(
            items=["single", "double"],
            on_select=self.on_integration_type_change,
        )
        self.integration_select.value = "single"
        left_i.add(self.integration_select)

        left_i.add(toga.Label("Integration Method:", style=Pack(padding_top=8)))
        self.method_select = toga.Selection(
            items=["simpsons", "trapezoidal", "simpsons38", "gaussian", "romberg", "all"],
        )
        self.method_select.value = "simpsons"
        left_i.add(self.method_select)

        left_i.add(toga.Label("Function f(x) or f(x,y):", style=Pack(padding_top=8)))
        self.func_input = toga.TextInput(placeholder="e.g. sin(x) or x*y + sin(x)")
        left_i.add(self.func_input)

        # Single parameters
        left_i.add(toga.Label("Single integral params:", style=Pack(padding_top=8)))
        params1 = toga.Box(style=Pack(direction=ROW))
        self.x0_input = toga.TextInput(placeholder="x0", style=Pack(width=80))
        self.xn_input = toga.TextInput(placeholder="xn", style=Pack(width=80))
        self.h_input = toga.TextInput(placeholder="h", style=Pack(width=80))
        params1.add(self.x0_input)
        params1.add(self.xn_input)
        params1.add(self.h_input)
        left_i.add(params1)

        # Double params
        left_i.add(toga.Label("Double integral params (x0, xn, y0, yn, h, k):", style=Pack(padding_top=8)))
        params2 = toga.Box(style=Pack(direction=ROW))
        self.x0_d = toga.TextInput(placeholder="x0", style=Pack(width=60))
        self.xn_d = toga.TextInput(placeholder="xn", style=Pack(width=60))
        self.y0_d = toga.TextInput(placeholder="y0", style=Pack(width=60))
        self.yn_d = toga.TextInput(placeholder="yn", style=Pack(width=60))
        self.h_d = toga.TextInput(placeholder="h", style=Pack(width=60))
        self.k_d = toga.TextInput(placeholder="k", style=Pack(width=60))
        params2.add(self.x0_d)
        params2.add(self.xn_d)
        params2.add(self.y0_d)
        params2.add(self.yn_d)
        params2.add(self.h_d)
        params2.add(self.k_d)
        left_i.add(params2)

        left_i.add(toga.Button("Calculate Integration", on_press=self.calculate_integration, style=Pack(padding_top=8)))
        left_i.add(toga.Button("Clear Integration", on_press=self.clear_integration, style=Pack(padding_top=6)))

        integ_box.add(left_i)

        right_i = toga.Box(style=Pack(direction=COLUMN, flex=1))
        right_i.add(toga.Label("Results:", style=Pack(padding_bottom=6)))
        self.integration_results = toga.MultilineTextInput(readonly=True, style=Pack(flex=1))
        right_i.add(self.integration_results)

        right_i.add(toga.Label("Array output:", style=Pack(padding_top=6)))
        self.array_output = toga.MultilineTextInput(readonly=True, style=Pack(height=120))
        right_i.add(self.array_output)

        integ_box.add(right_i)
        self.tabs.add("Integration", integ_box)

        # Finalize window
        self.main_window.content = outer
        self.main_window.show()

        # Set initial GUI state
        self.on_type_change(None)
        self.on_integration_type_change(None)

    # ---------- Interpolation methods ----------
    def on_type_change(self, widget):
        mode = self.interp_select.value
        # show/hide derivative input
        if mode == "hermitian":
            self.deriv_input.enabled = True
        else:
            self.deriv_input.value = ""
            self.deriv_input.enabled = False
        self.update_points_display()

    def add_points(self, widget):
        x_input = (self.x_input.value or "").strip()
        y_input = (self.y_input.value or "").strip()
        if not x_input or not y_input:
            self.info("Error", "Please enter both X and Y values")
            return
        try:
            x_values = [float(sympify(x.strip(), locals={"pi": pi, "e": E})) for x in x_input.split(",") if x.strip()]
            y_values = [float(sympify(y.strip(), locals={"pi": pi, "e": E})) for y in y_input.split(",") if y.strip()]
            if len(x_values) != len(y_values):
                self.info("Error", "Number of X and Y values must be equal")
                return

            if self.interp_select.value == "hermitian":
                deriv_input = (self.deriv_input.value or "").strip()
                if not deriv_input:
                    self.info("Error", "Please enter derivative values for Hermitian interpolation")
                    return
                deriv_values = [float(sympify(d.strip(), locals={"pi": pi, "e": E})) for d in deriv_input.split(",") if d.strip()]
                if len(deriv_values) != len(x_values):
                    self.info("Error", "Number of derivative values must equal number of points")
                    return
                self.derivatives = deriv_values

            # replace points with new ones (like original)
            self.points = [(x, y) for x, y in zip(x_values, y_values)]
            self.update_points_display()
            self.info("Success", f"Added {len(x_values)} points")
        except Exception as e:
            self.info("Error", f"Failed to add points: {e}")

    def clear_input(self, widget):
        self.x_input.value = ""
        self.y_input.value = ""
        self.deriv_input.value = ""

    def remove_last_point(self, widget):
        if self.points:
            self.points.pop()
            if self.derivatives and len(self.derivatives) >= len(self.points):
                self.derivatives = self.derivatives[: len(self.points)]
            self.update_points_display()

    def clear_points(self, widget):
        self.points = []
        self.derivatives = []
        self.current_poly = None
        self.current_func = None
        self.current_spline = None
        self.poly_text.value = ""
        self.plot_image.image = None
        self.eval_result_label.text = "Result: "
        self.update_points_display()

    def update_points_display(self):
        lines = []
        for i, (x, y) in enumerate(self.points):
            if self.interp_select.value == "hermitian" and i < len(self.derivatives):
                lines.append(f"({x}, {y}, y'={self.derivatives[i]})")
            else:
                lines.append(f"({x}, {y})")
        self.points_display.value = "\n".join(lines)

    def format_polynomial_clean(self, coeffs):
        temp = ""
        n = len(coeffs)
        for i in range(n):
            if coeffs[i] != 0:
                temp += f" + {coeffs[i]}*x^{n-i-1}"
        return temp[3:-3] if len(temp) > 6 else temp

    def calculate_interpolation(self, widget):
        if len(self.points) < 2:
            self.info("Error", "Please enter at least 2 points")
            return
        if self.interp_select.value == "hermitian" and len(self.derivatives) != len(self.points):
            self.info("Error", "Please provide derivatives for all points in Hermitian interpolation")
            return
        try:
            x_vals = [p[0] for p in self.points]
            y_vals = [p[1] for p in self.points]

            # check duplicate x
            if len(set(x_vals)) != len(x_vals):
                self.info("Error", "Duplicate x values are not allowed")
                return

            sorted_data = sorted(
                zip(x_vals, y_vals, (self.derivatives if self.interp_select.value == "hermitian" else [0] * len(x_vals)))
            )
            x_vals = [d[0] for d in sorted_data]
            y_vals = [d[1] for d in sorted_data]
            if self.interp_select.value == "hermitian":
                self.derivatives = [d[2] for d in sorted_data]

            x_min, x_max = min(x_vals), max(x_vals)
            x_range = x_max - x_min
            x_plot = np.linspace(x_min - 0.2 * x_range, x_max + 0.2 * x_range, 500)

            if self.interp_select.value == "lagrange":
                x = var("x")
                self.current_poly, self.current_func, _ = lagrange(x_vals, y_vals)
                y_plot = [self.current_func(i) for i in x_plot]
                max_degree = len(x_vals) - 1
                coeffs = [self.current_poly.coeff(x, i) for i in range(max_degree + 1)]
                coeffs.reverse()
                polynomial_str = self.format_polynomial_clean(coeffs)
                poly_text = f"Lagrange Polynomial:\nP(x) = {polynomial_str}\n\n"
            elif self.interp_select.value == "hermitian":
                x = var("x")
                self.current_poly, self.current_func, _ = hermitian(x_vals, y_vals, self.derivatives)
                y_plot = [self.current_func(i) for i in x_plot]
                max_degree = 2 * len(x_vals) - 1
                coeffs = [self.current_poly.coeff(x, i) for i in range(max_degree + 1)]
                coeffs.reverse()
                polynomial_str = self.format_polynomial_clean(coeffs)
                poly_text = f"Hermitian Polynomial:\nP(x) = {polynomial_str}\n\n"
            else:  # spline
                x = var("x")
                self.current_poly, self.current_spline, self.current_dspline, self.Mvalues = cubic(x_vals, y_vals)
                y_plot = [self.current_spline(i) for i in x_plot]
                poly_text = "Cubic Spline Interpolation:\n M-values:\n"
                for k, v in self.Mvalues.items():
                    poly_text += f"  M_{k} = {v:.3f}\n"
                poly_text += "\nPiecewise polynomials:\n"
                for i in range(len(x_vals) - 1):
                    coeffs = [self.current_poly[i].coeff(x, j) for j in range(4)]
                    poly_text += f"Interval [{x_vals[i]:.3f}, {x_vals[i+1]:.3f}]: S_{i}(x) = {self.format_polynomial_clean(coeffs)}\n"

            # Plot to temporary PNG and show in ImageView
            plt.figure(figsize=(6, 4), dpi=100)
            plt.plot(x_plot, y_plot, "-", linewidth=2, label=f"{self.interp_select.value.title()} Interpolation")
            plt.plot(x_vals, y_vals, "ro", markersize=6, label="Data Points")
            for i, (xx, yy) in enumerate(zip(x_vals, y_vals)):
                plt.annotate(f"({xx:.2f}, {yy:.2f})", (xx, yy), xytext=(5, 5), textcoords="offset points", fontsize=8)
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.xlabel("x")
            plt.ylabel("y")
            plt.title(f"{self.interp_select.value.title()} Interpolation")

            tmpfile = os.path.join(tempfile.gettempdir(), "toga_plot.png")
            plt.tight_layout()
            plt.savefig(tmpfile)
            plt.close()

            # Toga ImageView expects a toga.Image instance
            try:
                self.plot_image.image = toga.Image(tmpfile)
            except Exception:
                # Fallback: just clear image if unsupported
                self.plot_image.image = None

            # Update poly text
            poly_text += "\nData Points:\n"
            for i, (xx, yy) in enumerate(zip(x_vals, y_vals)):
                if self.interp_select.value == "hermitian":
                    poly_text += f"  ({xx}, {yy}), y'({xx}) = {self.derivatives[i]}\n"
                else:
                    poly_text += f"  ({xx}, {yy})\n"
            self.poly_text.value = poly_text
            self.eval_result_label.text = "Result: "
        except Exception as e:
            self.info("Error", f"Calculation failed: {e}")

    def evaluate_function(self, widget):
        if not self.current_func and not self.current_spline:
            self.info("Error", "Please calculate interpolation first")
            return
        try:
            x_val = float(sympify(self.eval_input.value, locals={"pi": pi, "e": np.exp(1)}))
            if self.interp_select.value in ["lagrange", "hermitian"]:
                result = self.current_func(x_val)
            else:
                result = float(self.current_spline(x_val))
            self.eval_result_label.text = f"Result: f({x_val}) = {result:.6f}"
            # append a marker point on plot — regenerate plot quickly
            # (for simplicity just call calculate_interpolation again)
            self.calculate_interpolation(None)
        except Exception as e:
            self.info("Error", f"Evaluation failed: {e}")

    # ---------- Integration methods ----------
    def on_integration_type_change(self, widget):
        # nothing visual to toggle in this simplified layout; left for extension
        pass

    def clear_integration(self, widget):
        self.func_input.value = ""
        self.x0_input.value = ""
        self.xn_input.value = ""
        self.h_input.value = ""
        self.x0_d.value = ""
        self.xn_d.value = ""
        self.y0_d.value = ""
        self.yn_d.value = ""
        self.h_d.value = ""
        self.k_d.value = ""
        self.integration_results.value = ""
        self.array_output.value = ""

    def calculate_integration(self, widget):
        fstr = (self.func_input.value or "").strip()
        if not fstr:
            self.info("Error", "Please enter a function")
            return
        mode = self.integration_select.value
        method = self.method_select.value
        try:
            if mode == "single":
                # parse numbers
                x0 = float(sympify(self.x0_input.value or "0", locals={"pi": pi, "e": E}))
                xn = float(sympify(self.xn_input.value or "0", locals={"pi": pi, "e": E}))
                h = float(sympify(self.h_input.value or "0", locals={"pi": pi, "e": E}))
                results_text = f"Single Integration - {method}\nFunction: f(x) = {fstr}\nLimits: x0 = {x0}, xn = {xn}\n"
                if method != "gaussian" and method != "romberg":
                    if not all([self.x0_input.value, self.xn_input.value, self.h_input.value]):
                        self.info("Error", "Please fill all single integral parameters")
                        return
                    # NOTE: your original code used singlefunctions[method](x0,xn,h,f) but there was a mix: sometimes f is function, sometimes str.
                    # We'll call the same API but in many of your integration functions 'f' is expected to be a callable.
                    # Here, try to build a callable using support.string_to_function
                    try:
                        f_callable = string_to_function(fstr, integration_type="single")
                        res = singlefunctions[method](x0, xn, h, f_callable)
                        results_text += f"Step size: h = {h}\n\nThe integral is {res['integral_value']}\n"
                        data = res.get("data", [])
                    except Exception:
                        # fallback: if singlefunctions expect (x0,xn,h,f) where f is string, call as original (some functions in your repo might differ)
                        res = singlefunctions[method](x0, xn, h, fstr)
                        results_text += f"The integral is {res.get('integral_value', res)}\n"
                        data = res.get("data", [])
                else:
                    # gaussian or romberg case: call with slightly different signatures
                    if method == "gaussian":
                        res = singlefunctions[method](fstr, x0, xn)
                        results_text += f"The integral under 2 points {res.get('two')} , 3 points {res.get('three')}\n"
                        data = res.get("data", [])
                    else:  # romberg
                        res = singlefunctions[method](fstr, x0, xn)
                        results_text += f"Romberg result: {res}\n"
                        data = res.get("data", [])
                self.integration_results.value = results_text
                self.array_output.value = " ".join([str(round(v, 4)) for v in data[:100]])  # abbreviated
                self.info("Success", "Integration computed (see results pane)")
            else:
                # double integral path
                f_callable = string_to_function(fstr, integration_type="double")
                x0 = float(sympify(self.x0_d.value or "0", locals={"pi": pi, "e": E}))
                xn = float(sympify(self.xn_d.value or "0", locals={"pi": pi, "e": E}))
                y0 = float(sympify(self.y0_d.value or "0", locals={"pi": pi, "e": E}))
                yn = float(sympify(self.yn_d.value or "0", locals={"pi": pi, "e": E}))
                h = float(sympify(self.h_d.value or "0", locals={"pi": pi, "e": E}))
                k = float(sympify(self.k_d.value or "0", locals={"pi": pi, "e": E}))
                integral = doublefunctions[method](x0, xn, y0, yn, h, k, f_callable)
                results_text = f"Double Integration - {method}\nFunction: f(x,y) = {fstr}\nX limits: {x0} to {xn}\nY limits: {y0} to {yn}\nResult: {integral['integral_value']}\n"
                self.integration_results.value = results_text
                self.array_output.value = " ".join([str(round(v, 4)) for v in integral.get("data", [])[:200]])
                self.info("Success", "Double integration computed")
        except Exception as e:
            self.info("Error", f"Integration setup failed: {e}")

    # ---------- Helper ----------
    def info(self, title, message):
        # Simple cross-platform message: Toga dialogs vary by platform; using a simple label update here.
        # On desktop you can also use toga.MessageDialog; but to keep cross-platform simple, set a small dialog
        try:
            # try using a modal dialog if available
            dlg = toga.MessageDialog(title=title, message=message)
            dlg.show()
        except Exception:
            # fallback to print + window label
            print(f"{title}: {message}")

def main():
    return InterpolationApp("Interpolation App", "org.example.interpolation")

if __name__ == "__main__":
    app = main()
    app.main_loop()
