import customtkinter as ctk  # for the general GUI
from unidecode import unidecode  # for removing accents from the search bar input
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


sympotomes_actifs = []
assert type(sympotomes_actifs) == list, "sympotomes_actifs est forcément une liste"


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


def toggle_symptom(symptom):
    """
    Selects or deselects a symptom.

    If the symptom is already in selected_symptoms,
    remove it. Otherwise, add it.
    """
    assert type(sympotomes_actifs) == list, "sympotomes_actifs est forcément une liste"
    assert type(liste_symptomes) == list, "liste_symptomes est forcément une liste"
    assert type(symptom) == str, "symtom est forcément un str"
    # print(type(sympotomes_actifs))
    # print(type(symptom))

    if symptom in sympotomes_actifs:
        sympotomes_actifs.remove(symptom)
        print(f"symptômes '{symptom}' enlevé.")

    elif symptom in liste_symptomes:
        sympotomes_actifs.append(symptom)
        print(f"symptômes '{symptom}' ajouté.")
        print("Selected symptoms:", sympotomes_actifs)

    results_frame.pack_forget()  # Hide the results frame when symptoms are toggled.

    # Refresh the buttons so their colors reflect
    # the updated selection state.
    search()


def search(*args):
    """
    Filters the symptom list according to the search bar
    and separates selected and unselected symptoms.
    """

    # Remove all previously displayed buttons.
    for widget in fenetre_off.winfo_children():
        widget.destroy()

    for widget in fenetre_on.winfo_children():
        widget.destroy()

    # Clear the list of old button references.
    bouton_actifs.clear()

    # Get the current search text, remove accents, and convert it to lowercase.
    query = unidecode(recherche.get()).lower()

    # Keep symptoms containing the search text.
    search_symptom_list = [
        symptom for symptom in liste_symptomes if query in unidecode(symptom).lower()
    ]

    # Prioritise symptoms that START with the search text.
    search_symptom_list.sort(
        key=lambda symptom: not unidecode(symptom).lower().startswith(query)
    )

    # Separate selected and unselected symptoms.
    off_list = [
        symptom for symptom in search_symptom_list if symptom not in sympotomes_actifs
    ]

    on_list = [symptom for symptom in liste_symptomes if symptom in sympotomes_actifs]

    # Display selected symptoms.
    if not on_list:
        message = ctk.CTkLabel(fenetre_on, text="Aucun symptôme sélectionné.")
        message.pack(pady=5)
    for symptom in on_list:
        button = ctk.CTkButton(
            fenetre_on,
            text=symptom,
            fg_color="green",
            hover_color="darkgreen",
            command=lambda s=symptom: toggle_symptom(s),
        )

        button.pack(pady=5)
        bouton_actifs.append(button)

    # Display unselected symptoms.
    if not query:
        message = ctk.CTkLabel(fenetre_off, text="Cherchez un symptôme...")
        message.pack(pady=5)
    else:
        if len(off_list) > 21:
            l = len(off_list) - 20
            off_list = off_list[:20]
            off_list.append(f"et {l} autres résultats...")

        for symptom in off_list:
            button = ctk.CTkButton(
                fenetre_off, text=symptom, command=lambda s=symptom: toggle_symptom(s)
            )

            button.pack(pady=5)
            bouton_actifs.append(button)


def validate_symptoms():
    """
    Prints the list of selected symptoms to the console.
    This function is called when the "Validate Symptoms" button is clicked.
    """
    if not sympotomes_actifs:
        print("aucun symptôme sélectionné.")
    else:
        print("symptômes sélectionnés:", sympotomes_actifs)
        print("recherche des conditions possibles...")

        research()


def research():

    matches = {}

    selected = set(sympotomes_actifs)

    if not selected:
        return

    for condition, helper in conditions.items():

        condition_symptoms = set(helper["symptoms"])
        wiki = helper["wikipedia"]

        if not condition_symptoms:
            continue

        common = len(selected & condition_symptoms)

        if common == 0:
            continue

        precision = common / len(selected)
        recall = common / len(condition_symptoms)

        f1 = 2 * (precision * recall) / (precision + recall)

        matches[condition] = {
            "wikipedia": wiki,
            "common": common,
            "precision": precision * 100,
            "recall": recall * 100,
            "score": f1 * 100,
        }

    matches = dict(
        sorted(matches.items(), key=lambda item: item[1]["score"], reverse=True)
    )

    display_results(matches)


def display_results(matches):
    """
    Displays the search results in the application.
    """

    # Ensure the results frame is visible only after the first search.
    results_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Clear previous results
    for widget in results_frame.winfo_children():
        widget.destroy()

    # Sort by score, highest first
    matches = dict(
        sorted(matches.items(), key=lambda item: item[1]["score"], reverse=True)
    )

    # Display results
    if not matches:
        message = ctk.CTkLabel(
            results_frame, text="Aucun résultat trouvé.", font=("Arial", 16)
        )
        message.pack(pady=20)
        return

    for condition, data in matches.items():

        wiki = data["wikipedia"]
        common = data["common"]
        precision = data["precision"]
        recall = data["recall"]
        score = data["score"]

        # Determine whether it's an exact match
        perfect_match = precision == 100 and recall == 100

        if perfect_match:
            title = f"✓ {condition} - Correspondance parfaite"
            color = "green"
        else:
            title = condition
            color = None

        # Container for each condition
        condition_frame = ctk.CTkFrame(results_frame)
        condition_frame.pack(fill="x", padx=10, pady=5)

        # Condition name
        label = ctk.CTkLabel(
            condition_frame, text=title, font=("Arial", 16, "bold"), text_color=color
        )
        label.pack(pady=(10, 5))

        # Matching information
        details = (
            f"{common} symptômes en commun\n"
            f"Précision : {precision:.2f}%\n"
            f"Couverture : {recall:.2f}%\n"
            f"Score F1 : {score:.2f}%"
        )

        info = ctk.CTkLabel(condition_frame, text=details, font=("Arial", 12))
        info.pack(pady=(0, 10))


validate_button = ctk.CTkButton(
    application, text="Valider les symptômes", command=validate_symptoms
)
validate_button.pack(pady=10)

results_frame = ctk.CTkScrollableFrame(application)

# Call search whenever the contents of the search bar change.
recherche.trace_add("write", search)

# Display the complete symptom list when the application starts.
search()

application.mainloop()
