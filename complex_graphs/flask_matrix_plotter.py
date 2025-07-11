from flask import Flask, request, jsonify, render_template_string
import plotly.graph_objects as go
import plotly.utils
import numpy as np
import json

app = Flask(__name__)

# HTML template for displaying the plot
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Matrix Visualization</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .matrix-info {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .plot-container {
            width: 100%;
            height: 600px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Matrix Visualization</h1>
        <div class="matrix-info">
            <p><strong>Matrix Shape:</strong> {{ shape }}</p>
            <p><strong>Data Type:</strong> {{ dtype }}</p>
            <p><strong>Value Range:</strong> {{ min_val }} to {{ max_val }}</p>
        </div>
        <div id="plot" class="plot-container"></div>
    </div>

    <script>
        var plotData = {{ plot_json|safe }};
        Plotly.newPlot('plot', plotData.data, plotData.layout, {responsive: true});
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Home page with API documentation"""
    docs = """
    <h1>Matrix Plotting API</h1>
    <h2>Endpoints:</h2>
    <ul>
        <li><strong>POST /plot</strong> - Submit matrix data for plotting</li>
        <li><strong>GET /plot/{plot_id}</strong> - View a specific plot</li>
    </ul>
    <h2>Usage:</h2>
    <p>Send a POST request to /plot with JSON data containing a 'matrix' field.</p>
    <p>Example: {"matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}</p>
    """
    return docs

@app.route('/plot', methods=['POST'])
def plot_matrix():
    """Accept matrix data and create a heatmap visualization"""
    try:
        data = request.get_json()
        
        if not data or 'matrix' not in data:
            return jsonify({'error': 'Matrix data is required'}), 400
        
        # Convert to numpy array for easier handling
        matrix = np.array(data['matrix'])
        
        # Validate matrix dimensions
        if matrix.ndim != 2:
            return jsonify({'error': 'Matrix must be 2-dimensional'}), 400
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            colorscale='Viridis',
            showscale=True,
            hoverongaps=False,
            colorbar=dict(title="Value")
        ))
        
        # Update layout
        fig.update_layout(
            title=f'Matrix Heatmap ({matrix.shape[0]}x{matrix.shape[1]})',
            xaxis_title='Column Index',
            yaxis_title='Row Index',
            width=800,
            height=600
        )
        
        # Convert to JSON for embedding in HTML
        plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        # Matrix statistics
        matrix_info = {
            'shape': f"{matrix.shape[0]} × {matrix.shape[1]}",
            'dtype': str(matrix.dtype),
            'min_val': float(np.min(matrix)),
            'max_val': float(np.max(matrix))
        }
        
        # Return HTML page with embedded plot
        return render_template_string(
            HTML_TEMPLATE,
            plot_json=plot_json,
            **matrix_info
        )
        
    except Exception as e:
        return jsonify({'error': f'Error processing matrix: {str(e)}'}), 500

@app.route('/plot_json', methods=['POST'])
def plot_matrix_json():
    """Return plot data as JSON (for API consumption)"""
    try:
        data = request.get_json()
        
        if not data or 'matrix' not in data:
            return jsonify({'error': 'Matrix data is required'}), 400
        
        matrix = np.array(data['matrix'])
        
        if matrix.ndim != 2:
            return jsonify({'error': 'Matrix must be 2-dimensional'}), 400
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            colorscale='Viridis',
            showscale=True
        ))
        
        fig.update_layout(
            title=f'Matrix Heatmap ({matrix.shape[0]}x{matrix.shape[1]})',
            xaxis_title='Column Index',
            yaxis_title='Row Index'
        )
        
        # Return JSON data
        return jsonify({
            'plot_data': fig.to_dict(),
            'matrix_info': {
                'shape': matrix.shape,
                'dtype': str(matrix.dtype),
                'min_value': float(np.min(matrix)),
                'max_value': float(np.max(matrix))
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Error processing matrix: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)