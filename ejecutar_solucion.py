from pathlib import Path
import os
import sys

BASE = Path(__file__).resolve().parent
DEPS = BASE.parent / '.taller3_deps'
sys.path.insert(0, str(DEPS))
os.environ['PYTHONPATH'] = str(DEPS)
os.environ['MPLBACKEND'] = 'module://matplotlib_inline.backend_inline'
os.environ['IPYTHONDIR'] = str(BASE / '.ipython')
os.environ['JUPYTER_RUNTIME_DIR'] = str(BASE / '.jupyter_runtime')
os.environ['MPLCONFIGDIR'] = str(BASE / '.matplotlib')

import nbformat
from IPython.terminal.interactiveshell import TerminalInteractiveShell
from IPython.utils.capture import capture_output

path = BASE / 'Solucion_Completa_Taller3_Unidad3.ipynb'
nb = nbformat.read(path, as_version=4)
os.chdir(BASE)
shell = TerminalInteractiveShell.instance()
shell.run_line_magic('matplotlib', 'inline')
shell.display_formatter.active_types = ['text/plain', 'text/html', 'image/png']
count = 0
try:
    for cell in nb.cells:
        if cell.cell_type != 'code':
            continue
        count += 1
        print('Executing cell', count, flush=True)
        with capture_output() as captured:
            result = shell.run_cell(cell.source, store_history=True)
        cell.execution_count = count
        cell.outputs = []
        if captured.stdout:
            cell.outputs.append(nbformat.v4.new_output('stream', name='stdout', text=captured.stdout))
        if captured.stderr:
            cell.outputs.append(nbformat.v4.new_output('stream', name='stderr', text=captured.stderr))
        for output in captured.outputs:
            cell.outputs.append(nbformat.v4.new_output('display_data', data=output.data, metadata=output.metadata))
        if result.error_before_exec or result.error_in_exec:
            raise RuntimeError(captured.stdout + captured.stderr)
finally:
    nbformat.write(nb, path)
nbformat.validate(nb)
code_cells = [c for c in nb.cells if c.cell_type == 'code']
errors = [o for c in code_cells for o in c.outputs if o.output_type == 'error']
images = sum('image/png' in o.get('data', {}) for c in code_cells for o in c.outputs)
print('Executed:', len(code_cells), 'Errors:', len(errors), 'Charts:', images)
for cell in code_cells:
    if 'cantidad_item_9 =' in cell.source or 'Filas originales:' in cell.source:
        for output in cell.outputs:
            if output.output_type == 'stream':
                print(output.text)
