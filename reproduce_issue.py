from flask import Flask
import os
from jinja2 import Environment, FileSystemLoader

# Read the actual template file
template_path = os.path.join(os.getcwd(), 'app', 'templates', 'workout_form.html')
with open(template_path, 'r') as f:
    template_content = f.read()

# Mock data
ejercicios = {
    "Pecho": [
        {"id": 1, "nombre": "Press Banca"},
        {"id": 2, "nombre": "Aperturas"}
    ]
}

datos = {
    'exercise_id': 1,
    'exercise_name': 'Press Banca',
    'series_details': [{'numero': 1, 'reps': 10, 'peso': 50, 'comentario': 'Easy'}]
}

# Setup Jinja2 environment
env = Environment(loader=FileSystemLoader(os.path.join(os.getcwd(), 'app', 'templates')))

# Mock globals
env.globals['url_for'] = lambda endpoint, **values: f"/{endpoint}"
env.globals['get_flashed_messages'] = lambda with_categories=False: []
env.globals['session'] = {} 

template = env.get_template('workout_form.html')

try:
    rendered = template.render(ejercicios=ejercicios, datos=datos, titulo="Test")
    
    # Check for any invalid Jinja2 syntax in the rendered output
    if '{ {' in rendered or '} }' in rendered:
        print("FAIL: Found invalid syntax '{ {' or '} }' in rendered output.")
        # Print context around the error
        idx = rendered.find('{ {')
        if idx == -1: idx = rendered.find('} }')
        print("Context:", rendered[max(0, idx-50):min(len(rendered), idx+50)])
    else:
        print("SUCCESS: No invalid Jinja2 syntax found.")
        
    # Check specific values
    if 'const selectedExerciseId = 1;' in rendered:
        print("SUCCESS: selectedExerciseId rendered correctly.")
    else:
        print("FAIL: selectedExerciseId not rendered correctly.")
        
    if 'const selectedExerciseName = "Press Banca";' in rendered:
        print("SUCCESS: selectedExerciseName rendered correctly.")
    else:
        print("FAIL: selectedExerciseName not rendered correctly.")

    if 'const seriesDetails = [{"comentario": "Easy", "numero": 1, "peso": 50, "reps": 10}];' in rendered or 'const seriesDetails = [{"comentario": "Easy", "numero": 1, "peso": 50, "reps": 10}]' in rendered:
         print("SUCCESS: seriesDetails rendered correctly.")
    else:
         print("FAIL: seriesDetails not rendered correctly.")
         # Print what was rendered
         start = rendered.find('const seriesDetails =')
         end = rendered.find('function generateSeriesInputs')
         print("Rendered seriesDetails:", rendered[start:end].strip())

except Exception as e:
    print(f"FAIL: Rendering error: {e}")
