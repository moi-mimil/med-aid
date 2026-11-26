import customtkinter as ctk  # for the general GUI
from unidecode import unidecode  # for removing accents from the search bar input
import webbrowser as w # pour ouvrir les pages wiki
from data import (
    give_condition,
    give_symptoms,
)  # for the list of conditions and their associated symptoms


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

# Frame for unselected symptoms
fenetre_off = ctk.CTkFrame(fenetre)
fenetre_off.pack(side="left", padx=10, pady=10)

# Frame for selected symptoms
fenetre_on = ctk.CTkFrame(fenetre)
fenetre_on.pack(side="right", padx=10, pady=10)


symptomes_actifs = []
assert type(symptomes_actifs) == list, "sympotomes_actifs est forcément une liste"


bouton_actifs = []
assert type(bouton_actifs) == list, "bouton_actifs est forcément une liste"


boutons_conditions = []
assert type(boutons_conditions) == list, "boutons_conditions est forcément une liste"

# Search bar
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
    assert type(symptomes_actifs) == list, "sympotomes_actifs est forcément une liste"
    assert type(liste_symptomes) == list, "liste_symptomes est forcément une liste"
    assert type(symptome) == str, "symptome est forcément un str"
    # print(type(sympotomes_actifs))
    # print(type(symptom))

    if symptome in symptomes_actifs:
        symptomes_actifs.remove(symptome)
        print(f"symptômes '{symptome}' enlevé.")

    elif symptome in liste_symptomes: #pour n'ajouter que les symptomes valides
        symptomes_actifs.append(symptome)
        print(f"symptômes '{symptome}' ajouté.")
        print("Selected symptoms:", symptomes_actifs)

    fenetre_resultats.pack_forget()

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

    # Prioritise symptoms that START with the search text.
    liste_symptomes_recherche.sort(
        key=lambda symptome: not unidecode(symptome).lower().startswith(requete)
    )

    # Separate selected and unselected symptoms.
    off_list = [
        symptome for symptome in liste_symptomes_recherche if symptome not in symptomes_actifs
    ]

    on_list = [symptome for symptome in liste_symptomes if symptome in symptomes_actifs]

    assert type(off_list) == list, "off list est forcémment une liste"
    assert type(on_list) == list, "on_list est forcément une liste"

    # Display selected symptoms.
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

    # Display unselected symptoms.
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
    if not symptomes_actifs:
        print("aucun symptôme sélectionné.")
    else:
        print("symptômes sélectionnés:", symptomes_actifs)
        print("recherche des conditions possibles...")

        recherche_fonct()


def recherche_fonct():

    matchs = {}
    assert type(matchs) == dict, "matchs est forcément un dictionnaire"

    selectiones = set(symptomes_actifs)

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

    # Sort by score, highest first
    matchs = dict(
        sorted(matchs.items(), key=lambda item: item[1]["score"], reverse=True)
    )

    # Display results
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

        # Determine whether it's an exact match
        match_parfait = precision == 100 and rappel == 100

        if match_parfait:
            title = f"✓ {condition} - Correspondance parfaite"
            color = "green"
        else:
            title = condition
            color = None

        # Container for each condition
        condition_frame = ctk.CTkFrame(fenetre_resultats)
        condition_frame.pack(fill="x", padx=10, pady=5)

        # Condition name
        label = ctk.CTkLabel(
            condition_frame, text=title, font=("Arial", 16, "bold"), text_color=color
        )
        label.pack(pady=(10, 5))

        # Matching information
        details = (
            f"{commun} symptômes en commun\n"
            f"Précision : {precision:.2f}%\n"
            f"Couverture : {rappel:.2f}%\n"
            f"Score F1 : {score:.2f}%"
        )

        info = ctk.CTkLabel(condition_frame, text=details, font=("Arial", 12))
        info.pack(pady=(0, 10))

        link = ctk.CTkLabel(condition_frame, text="Lien Wikipedia", text_color="blue", cursor="hand2")
        link.pack(pady=(0, 10))
        link.bind("<Button-1>", lambda e, url=wiki: ouvr_lien(url))

validate_button = ctk.CTkButton(
    application, text="Valider les symptômes", command=valider_symtomes
)
validate_button.pack(pady=10)

fenetre_resultats = ctk.CTkScrollableFrame(application)

# Call search whenever the contents of the search bar change.
recherche.trace_add("write", search)

# Display the complete symptom list when the application starts.
search()

application.mainloop()
