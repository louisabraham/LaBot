all: pyodide.js pyodide.asm.js pyodide.asm.data pyodide.asm.data.js pyodide.asm.wasm packages.json

pyodide.js:
	wget https://iodide-project.github.io/pyodide-demo/pyodide.js
	sed -i -e "s/https:\/\/iodide-project.github.io\/pyodide-demo/./g" pyodide.js

pyodide.asm.js:
	wget https://iodide-project.github.io/pyodide-demo/pyodide.asm.js

pyodide.asm.data:
	wget https://iodide-project.github.io/pyodide-demo/pyodide.asm.data

pyodide.asm.data.js:
	wget https://iodide-project.github.io/pyodide-demo/pyodide.asm.data.js

pyodide.asm.wasm:
	wget https://iodide-project.github.io/pyodide-demo/pyodide.asm.wasm

packages.json:
	wget https://iodide-project.github.io/pyodide-demo/packages.json