import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
# Asegúrate que tu archivo 'Blog.py' contiene la clase BlogApp Neo4j adaptada
from Blog import BlogAppNeo4j as BlogApp
app = BlogApp(password="12345678")

#AGREGAR
def add_user():
    name = simpledialog.askstring("Nuevo Usuario", "Nombre del usuario:")
    if (name == ""):
        name = simpledialog.askstring("Nuevo Usuario", "No puede quedar vacio")
    email = simpledialog.askstring("Nuevo Usuario", "Correo electrónico:")
    if (email == ""):
        email = simpledialog.askstring("Nuevo Usuario", "No puede quedar vacio")

    if name and email:
        try:
            app.create_user(name, email)
            messagebox.showinfo("Éxito", "Usuario agregado (o actualizado) correctamente.")
        except Exception as e:
            messagebox.showerror("Error Cypher", f"Fallo al agregar usuario: {e}")

def add_category():
    name = simpledialog.askstring("Nueva Categoría", "Nombre de la categoría:")
    if name:
        try:
            # En Neo4j, usamos una función específica para crear/actualizar categoría por nombre (MERGE)
            app.create_category(name)
            messagebox.showinfo("Éxito", "Categoría agregada correctamente.")
        except Exception as e:
            messagebox.showerror("Error Cypher", f"Fallo al agregar categoría: {e}")

def add_comment():
    articles = app.list_nodes("Article")
    if not articles:
        messagebox.showinfo("Sin artículos", "No hay artículos registrados.")
        return

    win = tk.Toplevel(root)
    win.title("Selección de Artículo")
    win.geometry("400x200")

    tk.Label(win, text="Selecciona un artículo para comentar:").pack(pady=10)
    titles = [a["title"] for a in articles]
    combo = ttk.Combobox(win, values=titles, width=47)
    combo.pack(pady=10)

    def comment_selected():
        article_title = combo.get()
        if not article_title:
            messagebox.showerror("Error", "Selecciona un artículo válido.")
            return
        win.destroy()
        # Llamamos al formulario real para ingresar datos del comentario
        comment_form(article_title) 

    tk.Button(win, text="Comentar", command=comment_selected).pack(pady=10)

# --------------------------------------------------------------------------
# Forma para que se muestre el agregar, editar archivo
# --------------------------------------------------------------------------
def comment_form(article_title):
    win = tk.Toplevel(root)
    win.title(f"Añadir Comentario a '{article_title}'")
    win.geometry("400x350")

    # Autor
    tk.Label(win, text="Tu nombre (Usuario existente):").pack(anchor="w", padx=10, pady=5)
    users = app.list_nodes("User") 
    user_names = [u["name"] for u in users]
    author_combo = ttk.Combobox(win, values=user_names, width=47)
    author_combo.pack(padx=10)

    #Comentario
    tk.Label(win, text="Comentario:").pack(anchor="w", padx=10, pady=5)
    text_entry = tk.Text(win, height=6, width=45)
    text_entry.pack(padx=10)

    def guardar_comentario():
        commenter_name = author_combo.get().strip()
        comment_text = text_entry.get("1.0", "end").strip()
        if not commenter_name or not comment_text:
            messagebox.showerror("Error", "Nombre de usuario y comentario son obligatorios.")
            return
        # verificar autor
        commenter = app.search_nodes("User", "name", commenter_name)
        if not commenter:
            messagebox.showerror("Error", f"Usuario '{commenter_name}' no encontrado. Por favor, créalo primero.")
            return
        try:
            # Relaciones del comentario
            app.create_com(article_title, commenter_name, comment_text)
            messagebox.showinfo("Éxito", f"Comentario añadido al artículo '{article_title}'.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Error Cypher", f"Fallo al agregar comentario: {e}")

    tk.Button(win, text="Publicar Comentario", command=guardar_comentario, width=20).pack(pady=20)


def add_tag():
    name = simpledialog.askstring("Nuevo Tag", "Nombre del tag:")
    if name:
        try:
            app.create_tag(name)
            messagebox.showinfo("Éxito", "Tag agregado correctamente.")
        except Exception as e:
            messagebox.showerror("Error Cypher", f"Fallo al agregar tag: {e}")

def article_form(existing_title=None):
    win = tk.Toplevel(root)
    win.title("Editar Artículo" if existing_title else "Agregar Artículo")
    win.geometry("400x500")
    win.resizable(False, False)

    # Si estamos editando, cargamos los datos por TÍTULO (referencia principal en Neo4j)
    existing_article_details = app.get_article_with_details(existing_title) if existing_title else None

    tk.Label(win, text="Título:").pack(anchor="w", padx=10, pady=5)
    title_entry = tk.Entry(win, width=50)
    title_entry.pack(padx=10)
    if existing_article_details:
        title_entry.insert(0, existing_article_details["title"])
        # No se debe cambiar el título de un artículo existente (es la clave)
        title_entry.config(state='readonly')

    tk.Label(win, text="Contenido:").pack(anchor="w", padx=10, pady=5)
    text_entry = tk.Text(win, height=6, width=45)
    text_entry.pack(padx=10)
    if existing_article_details:
        text_entry.insert("1.0", existing_article_details["text"])

    # --- Autor (referencia por Nombre) ---
    tk.Label(win, text="Autor existente:").pack(anchor="w", padx=10, pady=5)
    # Reemplazamos app.search("users", {}) por app.list_nodes("User")
    users = app.list_nodes("User") 
    user_names = [u["name"] for u in users]
    author_combo = ttk.Combobox(win, values=user_names, width=47)
    author_combo.pack(padx=10)
    if existing_article_details:
        author_combo.set(existing_article_details["author"]) # Autor viene como nombre

    #Categoria
    tk.Label(win, text="Categoría:").pack(anchor="w", padx=10, pady=5)
    categories = app.list_nodes("Category")
    category_names = [c["name"] for c in categories]
    category_combo = ttk.Combobox(win, values=category_names, width=47)
    category_combo.pack(padx=10)
    if existing_article_details and existing_article_details["categories"]:
        category_combo.set(existing_article_details["categories"][0])
    # Tag
    tk.Label(win, text="Tags (separados por coma):").pack(anchor="w", padx=10, pady=5) # Cambiar etiqueta
    # Reemplazar el Combobox por una Entrada de Texto:
    tag_entry = tk.Entry(win, width=50) # Usamos Entry en lugar de Combobox
    tag_entry.pack(padx=10)
    if existing_article_details and existing_article_details["tags"]:
        # Unir la lista de tags con comas para mostrarla
        tag_entry.insert(0, ", ".join(existing_article_details["tags"]))

    def guardar():
        title = title_entry.get().strip() if not existing_title else existing_title # Usar título original si existe
        text = text_entry.get("1.0", "end").strip()
        author_name = author_combo.get().strip()
        category_name = category_combo.get().strip()
        
        # ------------------------------------------------------------------
        # 1. PROCESAR LA ENTRADA DE MÚLTIPLES TAGS
        # ------------------------------------------------------------------
        tag_names_input = tag_entry.get().strip()
        # Dividir la cadena por comas, limpiar espacios y filtrar elementos vacíos
        tag_names = [t.strip() for t in tag_names_input.split(',') if t.strip()]

        if not title or not text or not author_name:
            messagebox.showerror("Error", "Título, contenido y autor son obligatorios.")
            return

        # 2. Verificar si el Autor existe (la función search_nodes devuelve una lista)
        author = app.search_nodes("User", "name", author_name) 
        if not author:
            messagebox.showerror("Error", f"Autor '{author_name}' no encontrado. Por favor, créalo primero.")
            return
        
        try:
            # 3. Asegurar que la Categoría y los Tags existen (MERGE en la capa de la aplicación)
            app.create_category(category_name)
            
            # Crear cada Tag que el usuario haya introducido
            for tag_name in tag_names:
                app.create_tag(tag_name)

            # 4. Guardar o Actualizar
            if existing_title:
                # 4a. Actualizar las propiedades del nodo Article (usando la corrección de update_article)
                app.update_article(title, {"text": text, "date": "FechaActualizada"})
                
                # 4b. Actualizar las relaciones (incluyendo la lista de tags)
                app.update_article_relationships(title, author_name, category_name, tag_names)
                
                messagebox.showinfo("Éxito", "Artículo actualizado correctamente.")
            else:
                # 4c. Crear nuevo artículo y todas sus relaciones (incluyendo la lista de tags)
                app.create_article(title, text, author_name, category_name, tag_names)
                messagebox.showinfo("Éxito", "Artículo agregado correctamente.")

            win.destroy()
        except Exception as e:
            messagebox.showerror("Error Cypher", f"Error al guardar/actualizar artículo: {e}")

    tk.Button(win, text="Guardar", command=guardar, width=20).pack(pady=20)


# -------- EDITAR ARTÍCULO --------
def edit_article():
    articles = app.list_nodes("Article")
    if not articles:
        messagebox.showinfo("Sin artículos", "No hay artículos registrados.")
        return

    win = tk.Toplevel(root)
    win.title("Editar Artículo")
    win.geometry("400x200")

    tk.Label(win, text="Selecciona el artículo a editar:").pack(pady=10)
    titles = [a["title"] for a in articles]
    combo = ttk.Combobox(win, values=titles, width=47)
    combo.pack(pady=10)

    def editar():
        title = combo.get()
        if not title:
            messagebox.showerror("Error", "Selecciona un artículo válido.")
            return
        win.destroy()
        # Pasamos el TÍTULO, que es la clave de referencia en Neo4j
        article_form(existing_title=title) 

    tk.Button(win, text="Editar", command=editar).pack(pady=10)

def delete_article():
    # Reemplazamos app.search("articles", {}) por app.list_nodes("Article")
    articles = app.list_nodes("Article")
    if not articles:
        messagebox.showinfo("Sin artículos", "No hay artículos registrados.")
        return

    win = tk.Toplevel(root)
    win.title("Eliminar Artículo")
    win.geometry("400x200")

    tk.Label(win, text="Selecciona el artículo a eliminar:").pack(pady=10)
    titles = [a["title"] for a in articles]
    combo = ttk.Combobox(win, values=titles, width=47)
    combo.pack(pady=10)

    def eliminar():
        title = combo.get()
        if not title:
            messagebox.showerror("Error", "Selecciona un artículo válido.")
            return

        confirm = messagebox.askyesno("Confirmar eliminación", f"¿Eliminar '{title}'?")
        if confirm:
            try:
                # Usamos la función de Neo4j para eliminar por Título (DETACH DELETE)
                app.delete_node("Article", "title", title)
                messagebox.showinfo("Éxito", "Artículo eliminado correctamente.")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error Cypher", f"Fallo al eliminar: {e}")

    tk.Button(win, text="Eliminar", command=eliminar).pack(pady=10)

def view_articles():
    # Reemplazamos app.search("articles", {}) por app.list_nodes("Article")
    articles_list = app.list_nodes("Article")
    if not articles_list:
        messagebox.showinfo("Sin artículos", "No hay artículos registrados.")
        return

    ventana = tk.Toplevel()
    ventana.title("Lista de Artículos")
    ventana.geometry("700x600")

    container = tk.Frame(ventana)
    container.pack(fill="both", expand=True)

    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    ventana.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

    for art_info in articles_list:
        # Usamos el TÍTULO para obtener los detalles del grafo (conexiones)
        article = app.get_article_with_details(art_info["title"]) 
        if not article: continue # Si la consulta falla o no encuentra el artículo, saltar

        frame = tk.LabelFrame(scrollable_frame, text=article["title"], padx=10, pady=5)
        frame.pack(fill="x", padx=10, pady=8)

        tk.Label(frame, text=f"URL: {article['url']}").pack(anchor="w")
        tk.Label(frame, text=f"Autor: {article['author']}").pack(anchor="w")
        tk.Label(frame, text=f"Contenido: {article['text']}", wraplength=650, justify="left").pack(anchor="w")
        tk.Label(frame, text=f"Categorías: {', '.join(article['categories'])}").pack(anchor="w")
        tk.Label(frame, text=f"Tags: {', '.join(article['tags'])}").pack(anchor="w")

        if article["comments"]:
            tk.Label(frame, text="Comentarios:").pack(anchor="w")
            for c in article["comments"]:
                tk.Label(frame, text=f"- {c['name']}: {c.get('text', '')}", wraplength=600, justify="left").pack(anchor="w")

def view_categories():
    categories = app.list_nodes("Category")
    if not categories:
        messagebox.showinfo("Sin categorías", "No hay categorías registradas.")
        return

    ventana = tk.Toplevel()
    ventana.title("Categorías y sus Artículos")
    ventana.geometry("700x600")

    canvas = tk.Canvas(ventana)
    scrollbar = ttk.Scrollbar(ventana, orient="vertical", command=canvas.yview)
    frame = tk.Frame(canvas)
    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for cat in categories:
        lf = tk.LabelFrame(frame, text=f"{cat['name']} ({cat['url']})", padx=10, pady=5)
        lf.pack(fill="x", padx=10, pady=8)
        # Usamos la función adaptada que usa la relación del grafo por nombre
        articles = app.get_articles_by_category(cat["name"]) 
        if articles:
            for a in articles:
                tk.Label(lf, text=f"• {a['title']} ({a['url']})", anchor="w").pack(fill="x")
        else:
            tk.Label(lf, text="(Sin artículos)", fg="gray").pack(anchor="w")

def view_tags():
    tags = app.list_nodes("Tag")
    if not tags:
        messagebox.showinfo("Sin tags", "No hay tags registrados.")
        return

    ventana = tk.Toplevel()
    ventana.title("Tags y sus Artículos")
    ventana.geometry("700x600")

    canvas = tk.Canvas(ventana)
    scrollbar = ttk.Scrollbar(ventana, orient="vertical", command=canvas.yview)
    frame = tk.Frame(canvas)
    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    for tag in tags:
        lf = tk.LabelFrame(frame, text=f"{tag['name']} ({tag['url']})", padx=10, pady=5)
        lf.pack(fill="x", padx=10, pady=8)
        # Usamos la función adaptada que usa la relación del grafo por nombre
        articles = app.get_articles_by_tag(tag["name"]) 
        if articles:
            for a in articles:
                tk.Label(lf, text=f"• {a['title']} ({a['url']})", anchor="w").pack(fill="x")
        else:
            tk.Label(lf, text="(Sin artículos)", fg="gray").pack(anchor="w")

def view_one_article():
    articles = app.list_nodes("Article")
    if not articles:
        messagebox.showinfo("Sin artículos", "No hay artículos registrados.")
        return

    win = tk.Toplevel(root)
    win.title("Ver un Artículo")
    win.geometry("400x200")

    tk.Label(win, text="Selecciona un artículo:").pack(pady=10)
    article_titles = [a["title"] for a in articles]
    combo = ttk.Combobox(win, values=article_titles, width=47)
    combo.pack(pady=10)

    def ver():
        title = combo.get()
        if not title:
            messagebox.showerror("Error", "Selecciona un artículo válido.")
            return
        win.destroy()

        # Usamos el TÍTULO como referencia para la consulta de detalles
        art = app.get_article_with_details(title)

        if not art:
            messagebox.showerror("Error", "No se encontraron detalles del artículo.")
            return

        ventana = tk.Toplevel()
        ventana.title(art["title"])
        ventana.geometry("700x500")

        container = tk.Frame(ventana)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        frame = tk.Frame(canvas)
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(frame, text=f"Título: {art['title']}", font=("Arial", 14, "bold")).pack(anchor="w", pady=5)
        tk.Label(frame, text=f"URL: {art['url']}").pack(anchor="w")
        tk.Label(frame, text=f"Autor: {art['author']}").pack(anchor="w")
        tk.Label(frame, text=f"Contenido:\n{art['text']}", wraplength=650, justify="left").pack(anchor="w")
        tk.Label(frame, text=f"Categorías: {', '.join(art['categories'])}").pack(anchor="w")
        tk.Label(frame, text=f"Tags: {', '.join(art['tags'])}").pack(anchor="w")

        if art["comments"]:
            tk.Label(frame, text="Comentarios:", font=("Arial", 10, "bold")).pack(anchor="w", pady=5)
            for c in art["comments"]:
                tk.Label(frame, text=f"- {c['name']}: {c.get('text', '')}", wraplength=600, justify="left").pack(anchor="w")

    tk.Button(win, text="Ver", command=ver).pack(pady=20)

def submenu_users():
    win = tk.Toplevel(root)
    win.title("Usuarios")
    win.geometry("300x200")
    tk.Button(win, text="Agregar usuario", width=25, command=add_user).pack(pady=10)
    tk.Button(win, text="Agregar comentario", width=25, command=add_comment).pack(pady=10)


def submenu_articles():
    win = tk.Toplevel(root)
    win.title("Artículos")
    win.geometry("300x400")
    tk.Button(win, text="Agregar artículo", width=25, command=article_form).pack(pady=5)
    tk.Button(win, text="Editar artículo", width=25, command=edit_article).pack(pady=5)
    tk.Button(win, text="Eliminar artículo", width=25, command=delete_article).pack(pady=5)
    tk.Button(win, text="Ver todos", width=25, command=view_articles).pack(pady=5)
    tk.Button(win, text="Ver uno", width=25, command=view_one_article).pack(pady=5)

def submenu_categories():
    win = tk.Toplevel(root)
    win.title("Categorías")
    win.geometry("300x300")
    tk.Button(win, text="Agregar categoría", width=25, command=add_category).pack(pady=5)
    tk.Button(win, text="Ver categorías", width=25, command=view_categories).pack(pady=5)

def submenu_tags():
    win = tk.Toplevel(root)
    win.title("Tags")
    win.geometry("300x300")
    tk.Button(win, text="Agregar tag", width=25, command=add_tag).pack(pady=5)
    tk.Button(win, text="Ver tags", width=25, command=view_tags).pack(pady=5)
#
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
root = tk.Tk()
root.title("Sistema de Blog - Neo4j (Cypher)") # Título actualizado
root.geometry("400x500")

tk.Label(root, text="MENÚ PRINCIPAL", font=("Arial", 16, "bold")).pack(pady=20)

def boton(texto, comando):
    tk.Button(root, text=texto, width=30, height=2, command=comando).pack(pady=10)

boton("Usuarios", submenu_users)
boton("Artículos", submenu_articles)
boton("Categorías", submenu_categories)
boton("Tags", submenu_tags)
boton("Salir", root.destroy)

root.mainloop()
