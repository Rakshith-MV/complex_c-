import requests
import numpy as np
import json
import webbrowser
import tempfile
import os

class MatrixPlotter:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def plot_matrix(self, matrix, open_browser=True):
        """
        Send matrix to Flask app and optionally open result in browser
        
        Args:
            matrix: 2D array-like object (list of lists, numpy array, etc.)
            open_browser: Whether to automatically open the plot in browser
        
        Returns:
            Response object from the Flask app
        """
        # Convert matrix to list format for JSON serialization
        if hasattr(matrix, 'tolist'):
            matrix_list = matrix.tolist()
        else:
            matrix_list = matrix
        
        # Prepare data
        data = {'matrix': matrix_list}
        
        try:
            # Send POST request
            response = requests.post(
                f"{self.base_url}/plot",
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                print("Matrix plot created successfully!")
                
                if open_browser:
                    # Save the HTML response to a temporary file and open it
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                        f.write(response.text)
                        temp_file = f.name
                    
                    # Open in default browser
                    webbrowser.open(f'file://{temp_file}')
                    print(f"Plot opened in browser: {temp_file}")
                
                return response
            else:
                print(f"Error: {response.status_code}")
                print(response.json())
                return response
                
        except requests.exceptions.RequestException as e:
            print(f"Connection error: {e}")
            print("Make sure the Flask app is running on localhost:5000")
            return None
    
    def get_plot_json(self, matrix):
        """
        Get plot data as JSON (for programmatic use)
        
        Args:
            matrix: 2D array-like object
            
        Returns:
            Dictionary containing plot data and matrix info
        """
        if hasattr(matrix, 'tolist'):
            matrix_list = matrix.tolist()
        else:
            matrix_list = matrix
        
        data = {'matrix': matrix_list}
        
        try:
            response = requests.post(
                f"{self.base_url}/plot_json",
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.status_code}")
                print(response.json())
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Connection error: {e}")
            return None

# Example usage and demonstrations
def main():
    # Initialize the plotter
    plotter = MatrixPlotter()
    
    print("Matrix Plotting Client")
    print("=" * 50)
    
    # Example 1: Simple matrix
    print("\n1. Simple 3x3 matrix:")
    simple_matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]
    plotter.plot_matrix(simple_matrix)
    
    # Example 2: Random matrix using numpy
    print("\n2. Random 10x10 matrix:")
    random_matrix = np.random.rand(10, 10)
    plotter.plot_matrix(random_matrix)
    
    # Example 3: Correlation matrix
    print("\n3. Correlation matrix:")
    # Generate some correlated data
    np.random.seed(42)
    data = np.random.randn(100, 5)
    data[:, 1] = data[:, 0] + 0.5 * np.random.randn(100)  # Correlated with column 0
    data[:, 2] = -data[:, 0] + 0.3 * np.random.randn(100)  # Anti-correlated with column 0
    
    correlation_matrix = np.corrcoef(data.T)
    plotter.plot_matrix(correlation_matrix)
    
    # Example 4: Mathematical function
    print("\n4. Mathematical function (sin(x) * cos(y)):")
    x = np.linspace(0, 2*np.pi, 20)
    y = np.linspace(0, 2*np.pi, 20)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) * np.cos(Y)
    plotter.plot_matrix(Z)
    
    # Example 5: Get JSON data (for programmatic use)
    print("\n5. Getting plot data as JSON:")
    json_data = plotter.get_plot_json(simple_matrix)
    if json_data:
        print(f"Matrix shape: {json_data['matrix_info']['shape']}")
        print(f"Value range: {json_data['matrix_info']['min_value']:.2f} to {json_data['matrix_info']['max_value']:.2f}")

def create_custom_matrix():
    """Interactive function to create and plot a custom matrix"""
    print("\nCustom Matrix Creator")
    print("=" * 30)
    
    try:
        rows = int(input("Enter number of rows: "))
        cols = int(input("Enter number of columns: "))
        
        print(f"\nEnter values for {rows}x{cols} matrix:")
        matrix = []
        
        for i in range(rows):
            row = []
            for j in range(cols):
                value = float(input(f"Enter value for position ({i+1},{j+1}): "))
                row.append(value)
            matrix.append(row)
        
        print(f"\nYour matrix:")
        for row in matrix:
            print(row)
        
        plotter = MatrixPlotter()
        plotter.plot_matrix(matrix)
        
    except ValueError:
        print("Invalid input. Please enter numeric values.")
    except KeyboardInterrupt:
        print("\nOperation cancelled.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "custom":
        create_custom_matrix()
    else:
        main()
        
        # Ask if user wants to create a custom matrix
        response = input("\nWould you like to create a custom matrix? (y/n): ")
        if response.lower() in ['y', 'yes']:
            create_custom_matrix()