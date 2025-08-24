

def string_to_function(function_str, integration_type="single"):
    """Convert function string to callable Python function"""
    from sympy import symbols, sympify, lambdify, sin, cos, tan, exp, log, sqrt, pi, E
    
    try:
        # Replace ^ with ** for exponentiation
        function_str = function_str.replace('^', '**')
        
        # Create symbolic variables
        if integration_type == "single":
            x = symbols('x')
            variables = x
        else:
            x, y = symbols('x y')
            variables = (x, y)
        
        # Create sympify locals dict
        sympify_locals = {
            'pi': pi, 'e': E,
            'sin': sin, 'cos': cos, 'tan': tan,
            'exp': exp, 'log': log, 'sqrt': sqrt
        }
        
        # Parse the expression
        expr = sympify(function_str, locals=sympify_locals)
        
        # Convert to numerical function
        func = lambdify(variables, expr, 'numpy')
        
        return func
        
    except Exception as e:
        raise ValueError(f"Could not convert function string: {str(e)}")
    