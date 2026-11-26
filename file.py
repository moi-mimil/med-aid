import customtkinter as ctk  # Pour l'affichage general
from unidecode import unidecode  # Pour enllever les accents en francais
import webbrowser as w # pour ouvrir les pages wiki
from data import (
    give_condition,
    give_symptoms,
)  #Pour avoir la liste de symptomes et de conditions depuis l'autre fichier


liste_symptomes = give_symptoms()
assert type(liste_symptomes) == list, "liste_symptomes est forcément une liste"
assert liste_symptomes, "liste_symptomes est vide"

conditions = give_condition()
assert type(conditions) == dict, "conditions est forcément un dictionnaire"
assert conditions, "conditions est vide"


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

application = ctk.CTk()

application.title("MED AID")
application.geometry("1920x1080")
# application.state("zoomed")


fenetre = ctk.CTkFrame(application)
fenetre.pack(pady=20)

# Fenetre des symptomes non selectionnes
fenetre_off = ctk.CTkFrame(fenetre)
fenetre_off.pack(side="left", padx=10, pady=10)

# Fenetre pour les symptomes selectionnes
fenetre_on = ctk.CTkFrame(fenetre)
fenetre_on.pack(side="right", padx=10, pady=10)


symptomes_actifs = []
assert type(symptomes_actifs) == list, "sympotomes_actifs est forcément une liste"


bouton_actifs = []
assert type(bouton_actifs) == list, "bouton_actifs est forcément une liste"


boutons_conditions = []
assert type(boutons_conditions) == list, "boutons_conditions est forcément une liste"

# Bar de recherche
recherche = ctk.StringVar()

barre_recherche = ctk.CTkEntry(
    application,
    placeholder_text="recherche des symptomes ...",
    textvariable=recherche,
    width=300,
)
barre_recherche.pack(pady=20)


def ouvr_lien(url):
    w.open_new(url)


def activer_symptome(symptome):
    """
    Active ou désactive un symptome.

    Si le symptome est dans les sympotomes_actifs, on l'enleve, sinon on l'ajoute
    """
    assert type(sympotomes_actifs) == list, "sympotomes_actifs est forcément une liste"
    assert type(liste_symptomes) == list, "liste_symptomes est forcément une liste"
    assert type(symptome) == str, "symptome est forcément un str"
    # print(type(sympotomes_actifs))
    # print(type(symptom))

    if symptome in sympotomes_actifs:
        sympotomes_actifs.remove(symptom)
        print(f"symptômes '{symptom}' enlevé.")

    elif symptome in liste_symptomes: #pour n'ajouter que les symptomes valides
        sympotomes_actifs.append(symptom)
        print(f"symptômes '{symptom}' ajouté.")
        print("Selected symptoms:", sympotomes_actifs)

        results_frame.pack_forget()

    search()


def search(*args):
    """
    Filtre la liste de symptomes par la recherche de l'utilisateur
    et sépare les symptomes actifs des non-actifs
    """

    # Enleve les anciens resultat
    for widget in fenetre_off.winfo_children():
        widget.destroy()

    for widget in fenetre_on.winfo_children():
        widget.destroy()

    # Enleve les anciens boutons actifs
    bouton_actifs.clear()

    # mets la recherche en minuscule et enleve les accents
    requete = unidecode(recherche.get()).lower()

    # Garde les bons symptomes
    liste_symptomes_recherche = [
        symptome for symptome in liste_symptomes if requete in unidecode(symptome).lower()
    ]
    assert type(liste_symptomes_recherche) == list, "liste_symptomes_recherche list est forcément une liste"

    # Priorise les symptomes qui commencent par la recherche
    liste_symptomes_recherche.sort(
        key=lambda symptome: not unidecode(symptome).lower().startswith(requete)
    )

    # Separe les symptomes selectionnes des non selectionnes
    off_list = [
        symptome for symptome in liste_symptomes_recherche if symptome not in sympotomes_actifs
    ]

    on_list = [symptome for symptome in liste_symptomes if symptome in sympotomes_actifs]

    assert type(off_list) == list, "off list est forcémment une liste"
    assert type(on_list) == list, "on_list est forcément une liste"

    # Affiche les symptomes selectionnes dans leur propre fenetre
    if not on_list:
        message = ctk.CTkLabel(fenetre_on, text="Aucun symptôme sélectionné.")
        message.pack(pady=5)
    for symptome in on_list:
        button = ctk.CTkButton(
            fenetre_on,
            text=symptome,
            fg_color="green",
            hover_color="darkgreen",
            command=lambda s=symptome: activer_symptome(s),
        )

        button.pack(pady=5)
        bouton_actifs.append(button)

    # Affiche les symptomes non selectionnes dans leur propre fenetre
    if not requete:
        message = ctk.CTkLabel(fenetre_off, text="Cherchez un symptôme...")
        message.pack(pady=5)
    else:
        if len(off_list) > 21:
            l = len(off_list) - 20
            off_list = off_list[:20] #pour ne garder visible que les 20 premiers
            off_list.append(f"et {l} autres résultats...")

        for symptome in off_list:
            button = ctk.CTkButton(
                fenetre_off, text=symptome, command=lambda s=symptome: activer_symptome(s)
            )

            button.pack(pady=5)
            bouton_actifs.append(button)


def valider_symtomes():
    """
    Affiche la liste des symptomes dans la console uniquement puis appelle la fontion suivante pour l'affichage
    Cette fonction s'active avec le bouton "valider les symptomes
    """
    if not sympotomes_actifs:
        print("aucun symptôme sélectionné.")
    else:
        print("symptômes sélectionnés:", sympotomes_actifs)
        print("recherche des conditions possibles...")

        recherche_fonct()


def recherche_fonct():

    matchs = {}
    assert type(matchs) == dict, "matchs est forcément un dictionnaire"

    selectiones = set(sympotomes_actifs)

    if not selectiones:
        return

    for condition, aide in conditions.items():

        symptomes_condition = set(aide["symptoms"])
        wiki = aide["wikipedia"]

        if not symptomes_condition:
            continue

        commun = len(selectiones & symptomes_condition)

        if commun == 0:
            continue

        precision = commun / len(selectiones)
        rappel = commun / len(symptomes_condition)

        f1 = 2 * (precision * rappel) / (precision + rappel)

        matchs[condition] = {
            "wikipedia": wiki,
            "commun": commun,
            "precision": precision * 100,
            "rappel": rappel * 100,
            "score": f1 * 100,
        }

    matchs = dict(
        sorted(matchs.items(), key=lambda item: item[1]["score"], reverse=True)
    )

    afficher_resultats(matchs)


def afficher_resultats(matchs):
    """
    Afficher les resultats de recherche dans l'application
    """

    # Verifie que les resultats ne s'affichent qu'apres le bouton cliqué.
    fenetre_resultats.pack(fill="both", expand=True, padx=20, pady=10)

    # Vide les résutats precedents
    for widget in fenetre_resultats.winfo_children():
        widget.destroy()

    # Trie par score, ordre decroissant (du plus)
    matchs = dict(
        sorted(matchs.items(), key=lambda item: item[1]["score"], reverse=True)
    )

    # Affiche les resultats
    if not matchs:
        message = ctk.CTkLabel(
            fenetre_resultats, text="Aucun résultat trouvé.", font=("Arial", 16)
        )
        message.pack(pady=20)
        return

    for condition, data in matchs.items():

        wiki = data["wikipedia"]
        #print(type(wiki))
        assert type(wiki) == str, "wiki doit être un str"


        commun = data["commun"]
        #print(type(commun))
        assert type(commun) == int, " commun doit être un int"


        precision = data["precision"]
        #print(type(precision))
        assert type(precision) == float, "precision doit être un float"


        rappel = data["rappel"]
        #print(type(rappel))
        assert type(rappel) == float, "rappel doit être un float"


        score = data["score"]
        #print(type(score))
        assert type(score) == float, "score doit être un float"

        # Determine les matchs parfaits
        match_parfait = precision == 100 and rappel == 100

        if match_parfait:
            title = f"✓ {condition} - Correspondance parfaite"
            color = "green"
        else:
            title = condition
            color = None

        # Conteneurs pour chaque condition
        condition_frame = ctk.CTkFrame(results_frame)
        condition_frame.pack(fill="x", padx=10, pady=5)

        # Nom des condition
        label = ctk.CTkLabel(
            condition_frame, text=title, font=("Arial", 16, "bold"), text_color=color
        )
        label.pack(pady=(10, 5))

        # Information correspondantes
        details = (
            f"{common} symptômes en commun\n"
            f"Précision : {precision:.2f}%\n"
            f"Couverture : {recall:.2f}%\n"
            f"Score F1 : {score:.2f}%"
        )

        info = ctk.CTkLabel(condition_frame, text=details, font=("Arial", 12))
        info.pack(pady=(0, 10))

        link = ctk.CTkLabel(condition_frame, text="Lien Wikipedia", text_color="blue", cursor="hand2")
        link.pack(pady=(0, 10))
        link.bind("<Button-1>", lambda e, url=wiki: ouvr_lien(url))

validate_button = ctk.CTkButton(
    application, text="Valider les symptômes", command=activer_symptome
)
validate_button.pack(pady=10)

results_frame = ctk.CTkScrollableFrame(application)

# Appelle la fonction de recherche a chaque fois que la barre de recherche change de valeur
recherche.trace_add("write", search)

# Affiche la liste complete des symptomes
search()

application.mainloop()
