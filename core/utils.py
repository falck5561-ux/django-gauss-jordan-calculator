import numpy as np

def gauss_jordan_solver(matrix_data, size):
    """
    Realiza la eliminación de Gauss-Jordan y almacena los pasos intermedios.
    """
    rows, cols = size
    steps = []

    try:
        M = np.array(matrix_data, dtype=float).reshape(rows, cols)
    except ValueError:
        return {"error": "El número de elementos no coincide con la dimensión.", "steps": []}
        
    steps.append({
        "description": "Matriz inicial",
        "matrix": M.copy().tolist(), 
        "operation": "Inicio del proceso"
    })

    for i in range(rows):
        pivot_val = M[i, i]
        
        if abs(pivot_val) < 1e-9: 
            return {"error": f"Pivote cero (o muy cercano) en la posición ({i+1}, {i+1}). La matriz es singular o requiere intercambio de filas. No se puede continuar.", "steps": steps}
        
        # Paso de Normalización
        factor = pivot_val
        M[i] = M[i] / factor
        
        steps.append({
            "description": f"Normalizar fila {i+1}",
            "matrix": M.copy().tolist(),
            "operation": f"R{i+1} → R{i+1} / {factor:.4f}"
        })

        # Paso de Eliminación
        for j in range(rows):
            if i != j:
                factor = M[j, i]
                M[j] = M[j] - factor * M[i]
                
                steps.append({
                    "description": f"Eliminar elemento en fila {j+1} y columna {i+1}",
                    "matrix": M.copy().tolist(),
                    "operation": f"R{j+1} → R{j+1} - {factor:.4f} × R{i+1}"
                })
                
    return {"result": M.tolist(), "steps": steps}

def calculate_inverse(matrix_data, n):
    """
    Calcula la inversa de una matriz N x N usando Gauss-Jordan [A | I].
    """
    A = np.array(matrix_data, dtype=float).reshape(n, n)
    I = np.identity(n)
    Augmented = np.hstack([A, I])
    
    result = gauss_jordan_solver(Augmented.flatten().tolist(), (n, 2 * n))
    
    if "result" in result and len(result["result"]) > 0:
        final_matrix = np.array(result["result"])
        
        if np.allclose(final_matrix[:, :n], np.identity(n)):
            result["inverse"] = final_matrix[:, n:].tolist()
        else:
            result["error"] = "La matriz es singular y no tiene inversa."
            
        result["is_inverse"] = True
        result["dimension"] = n

        for step in result["steps"]:
            step["matrix"] = np.array(step["matrix"]).tolist() 

    return result