import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
# ¡IMPORTANTE! Esta línea debe estar activa para definir las funciones de cálculo.
from .utils import gauss_jordan_solver, calculate_inverse 
import numpy as np
import io

# Vista para el formulario y el cálculo
def index(request):
    results = None
    dimension = 3
    is_inverse = False
    
    if request.method == 'POST':
        try:
            dimension = int(request.POST.get('dimension', 3))
            is_inverse = request.POST.get('is_inverse') == 'on'
            
            num_cols_input = dimension if is_inverse else dimension + 1 
            
            matrix_elements = []
            for i in range(dimension):
                for j in range(num_cols_input): 
                    key = f'cell_{i}_{j}'
                    value = request.POST.get(key)
                    if value is not None:
                        matrix_elements.append(float(value))

            # --- Lógica de cálculo (Mejorada para modo Inversa) ---
            
            if is_inverse:
                # 1. Recolectar el vector B (de los nuevos inputs)
                vector_b = []
                for i in range(dimension):
                    key = f'vector_b_{i}'
                    value = request.POST.get(key)
                    if value is not None:
                        vector_b.append(float(value))
                
                # 2. Calcular la inversa y obtener los resultados
                results = calculate_inverse(matrix_elements, dimension)
                
                if 'error' not in results and 'inverse' in results and vector_b:
                    try:
                        # Convertir a numpy arrays
                        A_inv = np.array(results['inverse'])
                        B = np.array(vector_b)
                        
                        # 3. Realizar la multiplicación matricial X = A_inv * B
                        solution_x = np.dot(A_inv, B)
                        
                        # 4. Agregar la solución X a los resultados para mostrar en HTML
                        results['solution_x_from_inverse'] = solution_x.tolist()
                    except Exception as e:
                        results['error'] = f"Error al multiplicar A⁻¹ * B: {e}"
                
            else: # Modo Gauss-Jordan directo (A | B)
                results = gauss_jordan_solver(matrix_elements, (dimension, dimension + 1))
            
            # 5. Pasar el modo y la dimensión al diccionario de resultados para el HTML
            results["is_inverse"] = is_inverse
            results["dimension"] = dimension
                
            if 'error' not in results:
                # Guardar los pasos en la sesión para la exportación
                request.session['calculation_steps'] = results.get('steps', [])
                request.session['is_inverse'] = is_inverse
                request.session['dimension'] = dimension
                
                # Guardar la solución X para exportar si estamos en modo inversa
                if is_inverse and 'solution_x_from_inverse' in results:
                    request.session['final_solution_x'] = results['solution_x_from_inverse']
                else:
                    request.session['final_solution_x'] = []

            else:
                request.session['calculation_steps'] = []
                request.session['final_solution_x'] = []


        except Exception as e:
            results = {"error": f"Error en la entrada o el procesamiento (Revise que sólo haya números): {e}"}
            results["is_inverse"] = is_inverse
            results["dimension"] = dimension


    separation_index = dimension 

    context = {
        'results': results,
        'range_dim': range(1, 6), 
        'separation_index': separation_index
    }
    return render(request, 'core/index.html', context)


# Vista para la exportación a Excel
def export_to_excel(request):
    steps = request.session.get('calculation_steps', [])
    is_inverse = request.session.get('is_inverse', False)
    dimension = request.session.get('dimension', 3)
    final_solution_x = request.session.get('final_solution_x', []) # Obtener la solución X
    
    if not steps:
        return HttpResponse("No hay datos de cálculo para exportar. Por favor, realice un cálculo primero.", status=400)
    
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        
        temp_df = pd.DataFrame()
        temp_df.to_excel(writer, sheet_name='Pasos', index=False, header=False)
        
        current_row = 0
        
        for i, step in enumerate(steps):
            description = step['description']
            matrix_data = step['matrix']
            operation = step['operation']
            
            # --- 1. Escribir Encabezados y Operación ---
            header_data = [
                [f'PASO {i+1}: {description}'],
                [f'Operación: {operation}']
            ]
            header_df = pd.DataFrame(header_data)
            header_df.to_excel(writer, sheet_name='Pasos', startrow=current_row, index=False, header=False)
            current_row += len(header_df)
            
            # --- 2. Escribir Matriz de Pasos ---
            matrix_df = pd.DataFrame(matrix_data)
            
            if is_inverse:
                col_names = [f'A{k+1}' for k in range(dimension)] + [f'I{k+1}' for k in range(dimension)]
            else:
                col_names = [f'X{k+1}' for k in range(dimension)] + ['B']
            
            matrix_df.columns = col_names
            
            matrix_df.to_excel(writer, sheet_name='Pasos', startrow=current_row, index=False, header=True)
            current_row += len(matrix_df) + 1 

            current_row += 1 

        # --- 3. Escribir Solución Final X (solo si se calculó en modo inversa) ---
        if is_inverse and final_solution_x:
            current_row += 1
            sol_header = pd.DataFrame([['SOLUCIÓN FINAL (A⁻¹ * B)']])
            sol_header.to_excel(writer, sheet_name='Pasos', startrow=current_row, index=False, header=False)
            current_row += 1
            
            sol_col_names = [f'X{k+1}' for k in range(dimension)]
            sol_df = pd.DataFrame([final_solution_x], columns=sol_col_names)
            sol_df.to_excel(writer, sheet_name='Pasos', startrow=current_row, index=False, header=True)


    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="Gauss_Jordan_Pasos.xlsx"'
    return response