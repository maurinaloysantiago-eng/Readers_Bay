import flet as ft
import json
import datetime

# --- 1. Carga y Guardado de datos ---
def cargar_datos(archivo):
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def guardar_datos(archivo, datos):
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

# Variables Globales
libros = cargar_datos('data/libros.json')
reseñas = cargar_datos('data/reseñas.json')
usuarios = cargar_datos('data/usuarios.json')
compartidos = cargar_datos('data/compartidos.json')

USUARIO_ACTUAL = None 

# --- 2. Interfaz Gráfica ---
def main(page: ft.Page):
    page.title = "Readers Bay"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # ==========================================
    #  LOGICA DE REGISTRO
    # ==========================================
    def abrir_dialogo_registro(e):
        reg_usuario = ft.TextField(label="Nuevo Usuario", width=250, autofocus=True)
        reg_pass = ft.TextField(label="Nueva Contraseña", password=True, width=250)
        reg_error = ft.Text("", color="red", size=12)

        def crear_usuario(e):
            nombre = reg_usuario.value.strip()
            password = reg_pass.value.strip()

            if not nombre or not password:
                reg_error.value = "Campos vacíos."
                reg_error.update()
                return

            for u in usuarios:
                if u['nombre'].lower() == nombre.lower():
                    reg_error.value = "¡Ese usuario ya existe!"
                    reg_error.update()
                    return

            nuevo_id = usuarios[-1]['id'] + 1 if usuarios else 1
            nuevo_usuario = {
                "id": nuevo_id,
                "nombre": nombre,
                "password": password
            }
            
            usuarios.append(nuevo_usuario)
            guardar_datos('data/usuarios.json', usuarios)
            
            page.close(dlg_registro)
            page.snack_bar = ft.SnackBar(ft.Text("¡Cuenta creada! Ahora puedes ingresar."))
            page.snack_bar.open = True
            page.update()

        dlg_registro = ft.AlertDialog(
            title=ft.Text("Crear Cuenta"),
            content=ft.Column([
                ft.Text("Únete al Readers Bay"),
                reg_usuario,
                reg_pass,
                reg_error
            ], tight=True, height=200),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: page.close(dlg_registro)),
                ft.ElevatedButton("Registrarme", on_click=crear_usuario),
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        page.open(dlg_registro)

    # ==========================================
    #  PANTALLA DE LOGIN
    # ==========================================
    
    txt_usuario = ft.TextField(label="Nombre de usuario", width=300, prefix_icon="person")
    txt_password = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, width=300, prefix_icon="lock")
    txt_error = ft.Text("", color="red")

    def intentar_login(e):
        global USUARIO_ACTUAL
        nombre_ingresado = txt_usuario.value.strip()
        pass_ingresada = txt_password.value.strip()

        if not nombre_ingresado or not pass_ingresada:
            txt_error.value = "Por favor llena ambos campos."
            page.update()
            return

        usuario_encontrado = None
        for u in usuarios:
            if u['nombre'].lower() == nombre_ingresado.lower():
                usuario_encontrado = u
                break
        
        if usuario_encontrado and usuario_encontrado.get('password') == pass_ingresada:
            USUARIO_ACTUAL = usuario_encontrado
            iniciar_aplicacion_principal()
        else:
            txt_error.value = "Usuario o contraseña incorrectos."
            page.update()

    btn_entrar = ft.ElevatedButton("Ingresar", on_click=intentar_login, width=300)
    btn_registro = ft.TextButton("¿No tienes cuenta? Regístrate aquí", on_click=abrir_dialogo_registro)

    tarjeta_login = ft.Container(
        content=ft.Column(
            [
                ft.Icon(name="menu_book", size=60, color="blue"),
                ft.Text("Bienvenido a Readers Bay", size=24, weight="bold"),
                txt_usuario,
                txt_password,
                txt_error,
                btn_entrar,
                ft.Divider(),
                btn_registro
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15
        ),
        padding=40,
        bgcolor="white",
        border_radius=10,
        shadow=ft.BoxShadow(blur_radius=15, color="grey")
    )

    page.add(tarjeta_login)


    # ==========================================
    #  APLICACIÓN PRINCIPAL (Biblioteca)
    # ==========================================
    def iniciar_aplicacion_principal():
        page.clean()
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.horizontal_alignment = ft.CrossAxisAlignment.START
        page.title = f"Readers Bay - Hola {USUARIO_ACTUAL['nombre']}"

        # --- LOGICA BANDEJA DE ENTRADA (NUEVO) ---
        def mostrar_mis_recomendaciones(e):
            # 1. Buscar recomendaciones dirigidas a MI (a_usuario_id == MI ID)
            mis_recos = [c for c in compartidos if c['a_usuario_id'] == USUARIO_ACTUAL['id']]
            
            # Contenedor de la lista
            lista_recos = ft.Column(spacing=10, scroll="auto", height=300)
            
            if not mis_recos:
                lista_recos.controls.append(
                    ft.Container(
                        content=ft.Text("No tienes recomendaciones nuevas 😢", italic=True),
                        padding=20, alignment=ft.alignment.center
                    )
                )
            else:
                for reco in mis_recos:
                    # Encontrar nombre del libro y del amigo
                    nombre_libro = next((l['titulo'] for l in libros if l['id'] == reco['libro_id']), "Libro desconocido")
                    nombre_amigo = next((u['nombre'] for u in usuarios if u['id'] == reco['de_usuario_id']), "Alguien")
                    
                    tarjeta_reco = ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon("mark_email_unread", color="blue"),
                                ft.Text(f"{nombre_amigo} te recomienda:", weight="bold")
                            ]),
                            ft.Text(f"📖 {nombre_libro}", size=16, weight="bold", color="blue900"),
                            ft.Text(f"Nota: \"{reco['nota']}\"", italic=True),
                            ft.Text(f"Fecha: {reco['fecha']}", size=12, color="grey")
                        ]),
                        bgcolor="blue50",
                        padding=15,
                        border_radius=10,
                        border=ft.border.all(1, "blue200")
                    )
                    lista_recos.controls.append(tarjeta_reco)

            dlg_recos = ft.AlertDialog(
                title=ft.Text("📬 Mis Recomendaciones"),
                content=ft.Container(content=lista_recos, width=400),
                actions=[ft.TextButton("Cerrar", on_click=lambda e: page.close(dlg_recos))]
            )
            page.open(dlg_recos)


        # --- HEADER / BARRA SUPERIOR ---
        def cerrar_sesion(e):
            page.clean()
            page.vertical_alignment = ft.MainAxisAlignment.CENTER
            page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
            txt_usuario.value = ""
            txt_password.value = ""
            txt_error.value = ""
            page.add(tarjeta_login)
            page.update()

        fila_titulo = ft.Row(
            [
                ft.Column([
                    ft.Text(f"Hola, {USUARIO_ACTUAL['nombre']} 👋", size=20, weight="bold"),
                    ft.Text("Biblioteca de Readers Bay", size=14, color="grey")
                ], expand=True),
                
                # BOTÓN NUEVO: NOTIFICACIONES
                ft.IconButton(
                    icon="mail", 
                    icon_color="blue", 
                    tooltip="Ver mis recomendaciones",
                    on_click=mostrar_mis_recomendaciones
                ),
                
                ft.ElevatedButton("Salir", icon="logout", on_click=cerrar_sesion, color="red")
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        # --- Funciones de Detalle ---
        def cerrar_dialogo(e):
            page.close(e.control.data)

        def mostrar_detalle(libro):
            
            # PESTAÑA 1: RESEÑAS
            reseñas_libro = [r for r in reseñas if r['libro_id'] == libro['id']]
            columna_reseñas = ft.Column(spacing=10, scroll="auto", height=200)

            def pintar_reseñas():
                columna_reseñas.controls.clear()
                if not reseñas_libro:
                    columna_reseñas.controls.append(ft.Text("No hay reseñas aún.", italic=True))
                else:
                    for r in reseñas_libro:
                        nombre_user = "Anónimo"
                        for u in usuarios:
                            if u['id'] == r['usuario_id']:
                                nombre_user = u['nombre']
                                break
                        columna_reseñas.controls.append(
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(f"{nombre_user} - {r['rating']}⭐", weight="bold"),
                                    ft.Text(r['texto'], size=13)
                                ]),
                                bgcolor="blue50", padding=10, border_radius=5
                            )
                        )
                if columna_reseñas.page: columna_reseñas.update()

            pintar_reseñas()

            campo_rating = ft.TextField(label="1-5", width=60)
            campo_texto_resena = ft.TextField(label="Escribe tu reseña...", expand=True)

            def guardar_resena(e):
                try:
                    rating = int(campo_rating.value)
                    if not (1 <= rating <= 5): raise ValueError
                except:
                    campo_rating.error_text = "Err"
                    campo_rating.update()
                    return

                nueva = {
                    "id": reseñas[-1]['id'] + 1 if reseñas else 1,
                    "libro_id": libro['id'],
                    "usuario_id": USUARIO_ACTUAL['id'],
                    "rating": rating,
                    "texto": campo_texto_resena.value,
                    "fecha": datetime.date.today().isoformat()
                }
                reseñas.append(nueva)
                reseñas_libro.append(nueva) 
                guardar_datos('data/reseñas.json', reseñas)
                campo_rating.value = ""
                campo_texto_resena.value = ""
                pintar_reseñas()
                page.snack_bar = ft.SnackBar(ft.Text("¡Reseña publicada!"))
                page.snack_bar.open = True
                page.update()

            contenido_tab_reseñas = ft.Column([
                columna_reseñas,
                ft.Divider(),
                ft.Row([campo_rating, campo_texto_resena, ft.IconButton(icon="send", on_click=guardar_resena)])
            ])

            # PESTAÑA 2: COMPARTIR
            opciones_usuarios = []
            for u in usuarios:
                if u['id'] != USUARIO_ACTUAL['id']:
                    opciones_usuarios.append(ft.dropdown.Option(key=str(u['id']), text=u['nombre']))

            combo_usuarios = ft.Dropdown(label="Seleccionar amigo", options=opciones_usuarios, width=200)
            campo_nota = ft.TextField(label="Nota opcional")

            def enviar_recomendacion(e):
                if not combo_usuarios.value:
                    combo_usuarios.error_text = "Elige a alguien"
                    combo_usuarios.update()
                    return

                nuevo_compartido = {
                    "id": compartidos[-1]['id'] + 1 if compartidos else 1,
                    "de_usuario_id": USUARIO_ACTUAL['id'],
                    "a_usuario_id": int(combo_usuarios.value),
                    "libro_id": libro['id'],
                    "fecha": datetime.date.today().isoformat(),
                    "nota": campo_nota.value
                }
                compartidos.append(nuevo_compartido)
                guardar_datos('data/compartidos.json', compartidos)
                page.snack_bar = ft.SnackBar(ft.Text(f"¡Recomendación enviada!"))
                page.snack_bar.open = True
                page.close(dlg_modal)
                page.update()

            contenido_tab_compartir = ft.Column([
                ft.Text("Recomendar este libro a:", weight="bold"),
                combo_usuarios,
                campo_nota,
                ft.ElevatedButton("Enviar Recomendación", icon="share", on_click=enviar_recomendacion)
            ], spacing=20, alignment=ft.MainAxisAlignment.CENTER)

            tabs = ft.Tabs(
                selected_index=0,
                animation_duration=300,
                tabs=[
                    ft.Tab(text="Reseñas", icon="reviews", content=contenido_tab_reseñas),
                    ft.Tab(text="Compartir", icon="share", content=contenido_tab_compartir),
                ],
                expand=1,
            )

            dlg_modal = ft.AlertDialog(
                title=ft.Text(libro['titulo']),
                content=ft.Container(content=tabs, width=500, height=400), 
                actions=[ft.TextButton("Cerrar", on_click=cerrar_dialogo)]
            )
            dlg_modal.actions[0].data = dlg_modal
            page.open(dlg_modal)

        # TABLA
        campo_busqueda = ft.TextField(label="Buscar libro...", icon="search", autofocus=True)
        tabla_libros = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Título")),
                ft.DataColumn(ft.Text("Autor")),
                ft.DataColumn(ft.Text("Ver")),
            ],
            rows=[]
        )

        def actualizar_tabla(texto_busqueda=""):
            tabla_libros.rows.clear()
            texto_busqueda = texto_busqueda.lower()
            for libro in libros:
                if texto_busqueda in str(libro['titulo']).lower() or texto_busqueda in str(libro['autor']).lower():
                    boton_ver = ft.IconButton(
                        icon="visibility", icon_color="blue",
                        on_click=lambda e, l=libro: mostrar_detalle(l)
                    )
                    tabla_libros.rows.append(ft.DataRow(cells=[
                        ft.DataCell(ft.Text(libro['titulo'])),
                        ft.DataCell(ft.Text(libro['autor'])),
                        ft.DataCell(boton_ver),
                    ]))
            page.update()

        campo_busqueda.on_change = lambda e: actualizar_tabla(e.control.value)
        actualizar_tabla() 
        
        page.add(fila_titulo, campo_busqueda, tabla_libros)
        page.update()

ft.app(target=main)