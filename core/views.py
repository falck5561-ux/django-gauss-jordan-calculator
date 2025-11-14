import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse
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

            if is_inverse:
                results = calculate_inverse(matrix_elements, dimension)
            else:
                results = gauss_jordan_solver(matrix_elements, (dimension, dimension + 1))
            
            # 1. Pasar el modo y la dimensión al diccionario de resultados para el HTML
            results["is_inverse"] = is_inverse
            results["dimension"] = dimension
                
            if 'error' not in results:
                # 2. Guardar los pasos en la sesión para la exportación
                request.session['calculation_steps'] = results.get('steps', [])
                request.session['is_inverse'] = is_inverse
                request.session['dimension'] = dimension
            else:
                request.session['calculation_steps'] = []


        except Exception as e:
            results = {"error": f"Error en la entrada o el procesamiento (Revise que sólo haya números): {e}"}
            results["is_inverse"] = is_inverse
            results["dimension"] = dimension


    # 3. Calcular el índice de separación para el HTML
    separation_index = dimension # La línea de separación está siempre después de la matriz A (columna N, índice N)

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
            
            # --- 2. Escribir Matriz ---
            matrix_df = pd.DataFrame(matrix_data)
            
            if is_inverse:
                col_names = [f'A{k+1}' for k in range(dimension)] + [f'I{k+1}' for k in range(dimension)]
            else:
                col_names = [f'X{k+1}' for k in range(dimension)] + ['B']
            
            matrix_df.columns = col_names
            
            matrix_df.to_excel(writer, sheet_name='Pasos', startrow=current_row, index=False, header=True)
            current_row += len(matrix_df) + 1 

            current_row += 1 

    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="Gauss_Jordan_Pasos.xlsx"'
    return response