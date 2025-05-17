import papermill as pm
import os
from dotenv import load_dotenv 
    
# Cargar variables de entorno desde .env para que este script las conozca
project_root = os.path.abspath(os.path.dirname(__file__)) 
dotenv_path = os.path.join(project_root, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    print(f"Variables de entorno para el script cargadas desde: {dotenv_path}")
else:
    print(f"Archivo .env no encontrado en {dotenv_path} para el script.")

input_notebook = os.path.join(project_root, 'notebooks', 'azure_sql_connection_test.ipynb')
output_notebook = os.path.join(project_root, 'notebooks', 'azure_sql_connection_test_output.ipynb')

params_to_inject = {
    # Si no estás inyectando parámetros porque el notebook usa dotenv, puedes dejar esto vacío o comentado
}

print(f"Ejecutando notebook: {input_notebook}")
print(f"El output se guardará en: {output_notebook}")
    
try:
    pm.execute_notebook(
       input_path=input_notebook,
       output_path=output_notebook,
       # parameters=params_to_inject, 
       kernel_name='venv_vod_marketing', # <--- ¡CAMBIO IMPORTANTE AQUÍ!
       log_output=True, # Para ver el output del notebook en la consola mientras se ejecuta
       progress_bar=True
    )
    print("¡Notebook ejecutado exitosamente con Papermill!")
except pm.exceptions.PapermillExecutionError as e:
    print(f"Error durante la ejecución del notebook con Papermill: {e}")
except Exception as e:
    print(f"Un error inesperado ocurrió: {e}")
    
    