from pathlib import Path
import os
import sys
import ast
from itertools import chain

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
code_cells = list(filter(lambda cell: cell.cell_type == 'code', nb.cells))
prohibidos = (ast.If, ast.IfExp, ast.For, ast.AsyncFor, ast.While,
              ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)


def verificar_sintaxis(fuente):
    hallazgos = tuple(filter(lambda nodo: isinstance(nodo, prohibidos), ast.walk(ast.parse(fuente))))
    assert not hallazgos, 'Se encontraron ciclos, condicionales o comprensiones.'
    return True


assert all(map(lambda cell: verificar_sintaxis(cell.source), code_cells))


def ejecutar_celda(numero, cell):
    print('Executing cell', numero, flush=True)
    with capture_output() as captured:
        result = shell.run_cell(cell.source, store_history=True)
    cell.execution_count = numero
    streams = filter(lambda par: bool(par[1]),
                     (('stdout', captured.stdout), ('stderr', captured.stderr)))
    cell.outputs = list(map(
        lambda par: nbformat.v4.new_output('stream', name=par[0], text=par[1]), streams,
    )) + list(map(
        lambda output: nbformat.v4.new_output('display_data', data=output.data, metadata=output.metadata),
        captured.outputs,
    ))
    assert result.success, captured.stdout + captured.stderr
    return cell


try:
    tuple(map(lambda par: ejecutar_celda(*par), enumerate(code_cells, start=1)))
finally:
    nbformat.write(nb, path)
nbformat.validate(nb)
outputs = tuple(chain.from_iterable(map(lambda cell: cell.outputs, code_cells)))
errors = tuple(filter(lambda output: output.output_type == 'error', outputs))
images = sum(map(lambda output: 'image/png' in output.get('data', {}), outputs))
print('Executed:', len(code_cells), 'Errors:', len(errors), 'Charts:', images)
metric_cells = filter(lambda cell: 'cantidad_item_9 =' in cell.source or 'Filas originales:' in cell.source, code_cells)
metric_outputs = chain.from_iterable(map(lambda cell: cell.outputs, metric_cells))
print(''.join(map(lambda output: output.text,
                  filter(lambda output: output.output_type == 'stream', metric_outputs))))
print('AST: sin if/else, for/while ni comprensiones en las celdas de codigo.')
