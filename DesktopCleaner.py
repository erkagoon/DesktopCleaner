import os
import shutil
from collections import Counter
import tkinter as tk
from tkinter import ttk, messagebox

# Spécifiez le chemin vers votre bureau
desktop_path = os.path.expanduser("~/Desktop")

def count_files_and_folders(path):
    # Liste tous les fichiers et dossiers du bureau
    items = os.listdir(path)

    # Sépare les fichiers et les dossiers
    files = [item for item in items if os.path.isfile(os.path.join(path, item))]
    folders = [item for item in items if os.path.isdir(os.path.join(path, item))]

    # Crée un dictionnaire avec les extensions de fichiers comme clés et leur fréquence comme valeurs
    ext_counts = Counter([os.path.splitext(file)[-1].lower() if os.path.splitext(file)[-1].lower() != '' else 'sans extension' for file in files])

    return len(files), len(folders), ext_counts

def arrange_files(ext):
    # Crée le nom du dossier en supprimant le point de l'extension
    folder_name = ext.replace(".", "") if ext != 'sans extension' else 'sans extension'
    folder_path = os.path.join(desktop_path, folder_name)

    # Crée le dossier s'il n'existe pas déjà
    os.makedirs(folder_path, exist_ok=True)

    # Récupère la liste de fichiers
    files = [item for item in os.listdir(desktop_path) if os.path.isfile(os.path.join(desktop_path, item))]

    # Déplace tous les fichiers avec l'extension spécifiée dans le dossier
    for file in files:
        if (os.path.splitext(file)[-1].lower() == ext) or (ext == 'sans extension' and os.path.splitext(file)[-1] == ''):
            shutil.move(os.path.join(desktop_path, file), folder_path)
    
        # Rafraîchit les données
        refresh_data()

def on_arrange():
    # Demande confirmation à l'utilisateur
    if messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir ranger tous les fichiers {ext_var.get()} dans un dossier ?"):
        arrange_files(ext_var.get())

def arrange_all_files():
    # Demande confirmation à l'utilisateur
    if messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir ranger tous les fichiers dans leurs dossiers respectifs?"):
        # Pour chaque extension, range les fichiers
        for ext in ext_counts.keys():
            arrange_files(ext)
    
        # Rafraîchit les données
        refresh_data()

def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(reverse=reverse, key=lambda x: int(x[0]) if col == "Nombre" else x[0])
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)
    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))

def refresh_data():
    # Récupère le nombre de fichiers, de dossiers et le comptage des extensions
    file_count, folder_count, ext_counts = count_files_and_folders(desktop_path)

    # Met à jour le nombre de fichiers et de dossiers
    file_count_label.config(text=f"Nombre de fichiers sur le bureau: {file_count}")
    folder_count_label.config(text=f"Nombre de dossiers sur le bureau: {folder_count}")

    # Met à jour la table
    for row in tree.get_children():
        tree.delete(row)
    for ext, count in ext_counts.items():
        tree.insert('', 'end', values=(ext, count))

    # Met à jour la liste déroulante
    ext_dropdown['values'] = list(ext_counts.keys())
    if ext_counts:
        ext_dropdown.set(next(iter(ext_counts)))
    else:
        ext_dropdown.set("")

def arrange_folders():
    # Crée le nom du dossier
    folder_name = "Bureau"
    folder_path = os.path.join(desktop_path, folder_name)

    # Crée le dossier s'il n'existe pas déjà
    os.makedirs(folder_path, exist_ok=True)

    # Récupère la liste des dossiers
    folders = [item for item in os.listdir(desktop_path) if os.path.isdir(os.path.join(desktop_path, item))]

    # Déplace tous les dossiers dans le nouveau dossier "Bureau"
    for folder in folders:
        if folder != folder_name:  # Évite de déplacer le dossier "Bureau" dans lui-même
            new_folder_path = os.path.join(folder_path, folder)
            # Si le dossier existe déjà, ajoute un suffixe numérique
            if os.path.exists(new_folder_path):
                i = 1
                while os.path.exists(new_folder_path + "_" + str(i)):
                    i += 1
                new_folder_path = new_folder_path + "_" + str(i)
            shutil.move(os.path.join(desktop_path, folder), new_folder_path)
    
    # Rafraîchit les données
    refresh_data()

def on_arrange_folders():
    # Demande confirmation à l'utilisateur
    if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir ranger tous les dossiers dans un dossier 'Bureau' ?"):
        arrange_folders()

# Crée la fenêtre principale
root = tk.Tk()
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(2, weight=1)

# Récupère la liste de fichiers, le nombre de dossiers et le comptage des extensions
file_count, folder_count, ext_counts = count_files_and_folders(desktop_path)

# Crée un label pour afficher le nombre de fichiers
file_count_label = tk.Label(root, text=f"Nombre de fichiers sur le bureau: {file_count}")
file_count_label.grid(row=0, column=0, sticky='w')

# Crée un label pour afficher le nombre de dossiers
folder_count_label = tk.Label(root, text=f"Nombre de dossiers sur le bureau: {folder_count}")
folder_count_label.grid(row=1, column=0, sticky='w')

# Crée une table pour afficher le nombre d'extensions
tree = ttk.Treeview(root, columns=('Extension', 'Nombre'), show='headings')
tree.heading('Extension', text='Extension', command=lambda: treeview_sort_column(tree, 'Extension', False))
tree.heading('Nombre', text='Nombre', command=lambda: treeview_sort_column(tree, 'Nombre', False))
tree.grid(row=2, column=0, sticky='nsew')

# Remplit la table avec les données d'extension
for ext, count in ext_counts.items():
    tree.insert('', 'end', values=(ext, count))

# Crée la liste déroulante des extensions et le bouton
ext_var = tk.StringVar(root)
if ext_counts:  # Ajoute cette condition
    ext_var.set(next(iter(ext_counts)))  # Fixe la valeur par défaut de la liste déroulante
else:
    ext_var.set("")
ext_dropdown = ttk.Combobox(root, textvariable=ext_var, values=list(ext_counts.keys()))
ext_dropdown.grid(row=3, column=0, sticky='w')
arrange_button = tk.Button(root, text="Ranger", command=on_arrange)
arrange_button.grid(row=3, column=0, sticky='e')

# Crée le bouton "Tout ranger"
arrange_all_button = tk.Button(root, text="Tout ranger", command=arrange_all_files)
arrange_all_button.grid(row=3, column=1, sticky='w')

# Désactive les boutons si aucun fichier n'existe sur le bureau
if file_count == 0:
    arrange_button.config(state='disabled')
    arrange_all_button.config(state='disabled')

# Crée le bouton "Ranger tout les dossiers"
arrange_folder_button = tk.Button(root, text="Ranger tous les dossiers", command=on_arrange_folders)
arrange_folder_button.grid(row=4, column=0, sticky='w')

# Désactive le bouton si aucun dossier n'existe sur le bureau
if folder_count == 0:
    arrange_folder_button.config(state='disabled')


# Exécute la boucle principale de tkinter
root.mainloop()
