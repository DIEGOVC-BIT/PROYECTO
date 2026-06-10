from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'clave_tyr'

# ── Crear carpeta datos si no existe ────────────────────────────────────────
import os
os.makedirs("datos", exist_ok=True)

# ── Rutas de los archivos .txt ──────────────────────────────────────────────
ARCHIVO_PRODUCTOS = "datos/productos.txt"
ARCHIVO_SERVICIOS = "datos/servicios.txt"
ARCHIVO_CLIENTES  = "datos/clientes.txt"
ARCHIVO_USUARIOS  = "datos/usuarios.txt"

# ── Crear archivos con datos iniciales si no existen ────────────────────────
if not os.path.exists(ARCHIVO_USUARIOS):
    with open(ARCHIVO_USUARIOS, "w", encoding="utf-8") as f:
        f.write("1,admin,1234\n")

if not os.path.exists(ARCHIVO_PRODUCTOS):
    with open(ARCHIVO_PRODUCTOS, "w", encoding="utf-8") as f:
        f.write("1,Retroexcavadora,S/. 500/dia,3\n")
        f.write("2,Minicargador,S/. 350/dia,2\n")
        f.write("3,Volquete,S/. 400/dia,5\n")
        f.write("4,Excavadora,S/. 600/dia,2\n")

if not os.path.exists(ARCHIVO_SERVICIOS):
    with open(ARCHIVO_SERVICIOS, "w", encoding="utf-8") as f:
        f.write("1,Alquiler de maquinaria,Alquiler por dia semana o mes\n")
        f.write("2,Movimiento de tierras,Excavacion y nivelacion de terrenos\n")
        f.write("3,Transporte de carga,Transporte de materiales y agregados\n")

if not os.path.exists(ARCHIVO_CLIENTES):
    with open(ARCHIVO_CLIENTES, "w", encoding="utf-8") as f:
        f.write("1,Carlos Perez,987654321,carlos@gmail.com\n")
        f.write("2,Maria Lopez,912345678,maria@gmail.com\n")

# ══════════════════════════════════════════════════════════════════════════════
#  FUNCIONES GENÉRICAS DE LECTURA / ESCRITURA
# ══════════════════════════════════════════════════════════════════════════════

def leer_lineas(archivo):
    """Lee el .txt y devuelve lista de listas (cada línea separada por comas)."""
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            lineas = []
            for linea in f:
                linea = linea.strip()
                if linea:
                    lineas.append(linea.split(","))
            return lineas
    except FileNotFoundError:
        return []

def siguiente_id(archivo):
    """Calcula el siguiente ID leyendo la última línea."""
    lineas = leer_lineas(archivo)
    if not lineas:
        return 1
    return int(lineas[-1][0]) + 1

# ══════════════════════════════════════════════════════════════════════════════
#  INICIO
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    return render_template('index.html')

# ══════════════════════════════════════════════════════════════════════════════
#  LOGIN / REGISTRO DE USUARIO
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/login', methods=['GET', 'POST'])
def login():
    mensaje = ""
    if request.method == 'POST':
        usuario  = request.form['usuario']
        password = request.form['password']

        # Buscar usuario en usuarios.txt  (formato: id,usuario,password)
        encontrado = False
        for linea in leer_lineas(ARCHIVO_USUARIOS):
            if linea[1] == usuario and linea[2] == password:
                encontrado = True
                break

        if encontrado:
            session['usuario'] = usuario
            flash('Bienvenido, ' + usuario + '!', 'success')
            return redirect(url_for('dashboard'))
        else:
            mensaje = "Usuario o contraseña incorrectos."

    return render_template('login.html', mensaje=mensaje)


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    mensaje = ""
    if request.method == 'POST':
        usuario  = request.form['usuario']
        password = request.form['password']

        # Verificar que no exista ya ese usuario
        for linea in leer_lineas(ARCHIVO_USUARIOS):
            if linea[1] == usuario:
                mensaje = "Ese usuario ya existe, elige otro."
                return render_template('registro.html', mensaje=mensaje)

        nuevo_id = siguiente_id(ARCHIVO_USUARIOS)
        with open(ARCHIVO_USUARIOS, "a", encoding="utf-8") as f:
            f.write(f"{nuevo_id},{usuario},{password}\n")

        mensaje = "Usuario registrado correctamente. Ya puedes iniciar sesión."

    return render_template('registro.html', mensaje=mensaje)


@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash('Sesión cerrada', 'info')
    return redirect(url_for('index'))

# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# ══════════════════════════════════════════════════════════════════════════════
#  PRODUCTOS   (formato línea: id,nombre,precio,stock)
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/productos')
def productos_lista():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    filas = leer_lineas(ARCHIVO_PRODUCTOS)
    productos = [{'id': f[0], 'nombre': f[1], 'precio': f[2], 'stock': f[3]} for f in filas]
    return render_template('productos.html', productos=productos)


@app.route('/productos/agregar', methods=['GET', 'POST'])
def producto_agregar():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    mensaje = ""
    if request.method == 'POST':
        nuevo_id = siguiente_id(ARCHIVO_PRODUCTOS)
        nombre   = request.form['nombre']
        precio   = request.form['precio']
        stock    = request.form['stock']
        with open(ARCHIVO_PRODUCTOS, "a", encoding="utf-8") as f:
            f.write(f"{nuevo_id},{nombre},{precio},{stock}\n")
        mensaje = "Producto guardado correctamente."
    return render_template('producto_form.html', producto=None, accion='Agregar', mensaje=mensaje)


@app.route('/productos/editar/<int:pid>', methods=['GET', 'POST'])
def producto_editar(pid):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    filas = leer_lineas(ARCHIVO_PRODUCTOS)
    mensaje = ""
    if request.method == 'POST':
        nuevas = []
        for f in filas:
            if int(f[0]) == pid:
                nuevas.append(f"{f[0]},{request.form['nombre']},{request.form['precio']},{request.form['stock']}\n")
            else:
                nuevas.append(",".join(f) + "\n")
        with open(ARCHIVO_PRODUCTOS, "w", encoding="utf-8") as arch:
            arch.writelines(nuevas)
        flash('Producto actualizado', 'success')
        return redirect(url_for('productos_lista'))

    prod = next((f for f in filas if int(f[0]) == pid), None)
    if not prod:
        flash('Producto no encontrado', 'danger')
        return redirect(url_for('productos_lista'))
    producto = {'id': prod[0], 'nombre': prod[1], 'precio': prod[2], 'stock': prod[3]}
    return render_template('producto_form.html', producto=producto, accion='Editar', mensaje=mensaje)


@app.route('/productos/eliminar/<int:pid>')
def producto_eliminar(pid):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    filas = leer_lineas(ARCHIVO_PRODUCTOS)
    with open(ARCHIVO_PRODUCTOS, "w", encoding="utf-8") as f:
        for linea in filas:
            if int(linea[0]) != pid:
                f.write(",".join(linea) + "\n")
    flash('Producto eliminado', 'warning')
    return redirect(url_for('productos_lista'))

# ══════════════════════════════════════════════════════════════════════════════
#  SERVICIOS   (formato línea: id,nombre,descripcion)
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/servicios')
def servicios_lista():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    filas = leer_lineas(ARCHIVO_SERVICIOS)
    servicios = [{'id': f[0], 'nombre': f[1], 'descripcion': f[2]} for f in filas]
    return render_template('servicios.html', servicios=servicios)


@app.route('/servicios/agregar', methods=['GET', 'POST'])
def servicio_agregar():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    mensaje = ""
    if request.method == 'POST':
        nuevo_id    = siguiente_id(ARCHIVO_SERVICIOS)
        nombre      = request.form['nombre']
        descripcion = request.form['descripcion']
        with open(ARCHIVO_SERVICIOS, "a", encoding="utf-8") as f:
            f.write(f"{nuevo_id},{nombre},{descripcion}\n")
        mensaje = "Servicio guardado correctamente."
    return render_template('servicio_form.html', servicio=None, accion='Agregar', mensaje=mensaje)


@app.route('/servicios/editar/<int:sid>', methods=['GET', 'POST'])
def servicio_editar(sid):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    filas = leer_lineas(ARCHIVO_SERVICIOS)
    if request.method == 'POST':
        nuevas = []
        for f in filas:
            if int(f[0]) == sid:
                nuevas.append(f"{f[0]},{request.form['nombre']},{request.form['descripcion']}\n")
            else:
                nuevas.append(",".join(f) + "\n")
        with open(ARCHIVO_SERVICIOS, "w", encoding="utf-8") as arch:
            arch.writelines(nuevas)
        flash('Servicio actualizado', 'success')
        return redirect(url_for('servicios_lista'))

    serv = next((f for f in filas if int(f[0]) == sid), None)
    if not serv:
        flash('Servicio no encontrado', 'danger')
        return redirect(url_for('servicios_lista'))
    servicio = {'id': serv[0], 'nombre': serv[1], 'descripcion': serv[2]}
    return render_template('servicio_form.html', servicio=servicio, accion='Editar', mensaje="")


@app.route('/servicios/eliminar/<int:sid>')
def servicio_eliminar(sid):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    filas = leer_lineas(ARCHIVO_SERVICIOS)
    with open(ARCHIVO_SERVICIOS, "w", encoding="utf-8") as f:
        for linea in filas:
            if int(linea[0]) != sid:
                f.write(",".join(linea) + "\n")
    flash('Servicio eliminado', 'warning')
    return redirect(url_for('servicios_lista'))

# ══════════════════════════════════════════════════════════════════════════════
#  CLIENTES   (formato línea: id,nombre,telefono,email)
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/clientes')
def clientes_lista():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    filas = leer_lineas(ARCHIVO_CLIENTES)
    clientes = [{'id': f[0], 'nombre': f[1], 'telefono': f[2], 'email': f[3]} for f in filas]
    return render_template('clientes.html', clientes=clientes)


@app.route('/clientes/agregar', methods=['GET', 'POST'])
def cliente_agregar():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    mensaje = ""
    if request.method == 'POST':
        nuevo_id = siguiente_id(ARCHIVO_CLIENTES)
        nombre   = request.form['nombre']
        telefono = request.form['telefono']
        email    = request.form['email']
        with open(ARCHIVO_CLIENTES, "a", encoding="utf-8") as f:
            f.write(f"{nuevo_id},{nombre},{telefono},{email}\n")
        mensaje = "Cliente guardado correctamente."
    return render_template('cliente_form.html', cliente=None, accion='Agregar', mensaje=mensaje)


@app.route('/clientes/editar/<int:cid>', methods=['GET', 'POST'])
def cliente_editar(cid):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    filas = leer_lineas(ARCHIVO_CLIENTES)
    if request.method == 'POST':
        nuevas = []
        for f in filas:
            if int(f[0]) == cid:
                nuevas.append(f"{f[0]},{request.form['nombre']},{request.form['telefono']},{request.form['email']}\n")
            else:
                nuevas.append(",".join(f) + "\n")
        with open(ARCHIVO_CLIENTES, "w", encoding="utf-8") as arch:
            arch.writelines(nuevas)
        flash('Cliente actualizado', 'success')
        return redirect(url_for('clientes_lista'))

    cli = next((f for f in filas if int(f[0]) == cid), None)
    if not cli:
        flash('Cliente no encontrado', 'danger')
        return redirect(url_for('clientes_lista'))
    cliente = {'id': cli[0], 'nombre': cli[1], 'telefono': cli[2], 'email': cli[3]}
    return render_template('cliente_form.html', cliente=cliente, accion='Editar', mensaje="")


@app.route('/clientes/eliminar/<int:cid>')
def cliente_eliminar(cid):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    filas = leer_lineas(ARCHIVO_CLIENTES)
    with open(ARCHIVO_CLIENTES, "w", encoding="utf-8") as f:
        for linea in filas:
            if int(linea[0]) != cid:
                f.write(",".join(linea) + "\n")
    flash('Cliente eliminado', 'warning')
    return redirect(url_for('clientes_lista'))

# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    app.run(debug=True)
