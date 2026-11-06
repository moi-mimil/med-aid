
import customtkinter as ctk # for the general GUI
from unidecode import unidecode # for removing accents from the search bar input
from conditions import give_condition # for the list of conditions and their associated symptoms

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("1920x1080")
app.title("MED AID")

frame = ctk.CTkFrame(app)
frame.pack(pady=20)

symptom_list = [
    "Fièvre", "Toux", "Fatigue", "Maux de tête",
    "Essoufflement", "Mal de gorge",
    "Perte du goût ou de l'odorat", "Nausées", "Vomissements",
    "Diarrhée", "Douleurs musculaires ou corporelles", "Frissons",
    "Écoulement nasal", "Congestion", "Douleurs thoraciques",
    "Étourdissements", "Éruption cutanée", "Gonflement", "Douleurs articulaires",
    "Douleurs abdominales", "Éternuements", "Démangeaisons", "Yeux rouges","Yeux larmoyants",
    "Sifflements respiratoires", "Brûlures d'estomac", "Ballonnements", "Constipation",
    "Douleurs à la miction", "Envies fréquentes d'uriner", "Sensibilité à la lumière", "Sensibilité au bruit",
    "Douleurs cervicales"
]

conditions = give_condition()


selected_symptoms = []


active_button = []

# Search bar
search_var = ctk.StringVar()

search_entry = ctk.CTkEntry(
    app,
    placeholder_text="recherche des symptomes ...",
    textvariable=search_var,
    width=300
)
search_entry.pack(pady=20)





def toggle_symptom(symptom):
    """
    Selects or deselects a symptom.

    If the symptom is already in selected_symptoms,
    remove it. Otherwise, add it.
    """

    if symptom in selected_symptoms:
        selected_symptoms.remove(symptom)
        print(f"Symptom '{symptom}' removed.")
    else:
        selected_symptoms.append(symptom)
        print(f"Symptom '{symptom}' added.")

    # Refresh the buttons so their colors reflect
    # the updated selection state.
    search()

    print("Selected symptoms:", selected_symptoms)


def search(*args):
    """
    Filters the symptom list according to the search bar
    and creates a button for each matching symptom.
    """

    # Remove all previously displayed buttons.
    for widget in frame.winfo_children():
        widget.destroy()

    # Clear the list of old button references.
    active_button.clear()

    # Get the current search text and convert it to lowercase.
    query = search_var.get().lower()
    if not query:
        search_symptom_list = ["cherchez un symptôme"]
    else:
        # Keep symptoms containing the search text.
        search_symptom_list = [
            symptom for symptom in symptom_list
            if query in unidecode(symptom).lower()
        ]

    # Prioritise symptoms that START with the search text.
    # For example, "Frissons" comes before "Essoufflement"
    # when searching for "f".
    search_symptom_list.sort(
        key=lambda symptom: not symptom.lower().startswith(query)
    )
    if len(search_symptom_list) > 21:
        l= len(search_symptom_list)-21
        del search_symptom_list[20:]
        search_symptom_list.append(f"et {l} autres résultats...")


    # Create a button for each matching symptom.
    for symptom in search_symptom_list:
        if symptom not in symptom_list:
            check= False  # Skip if the symptom is not in the original list.
        else:
            check= True  # Proceed if the symptom is valid.

        # Determine whether this symptom is already selected.
        is_selected = symptom in selected_symptoms

        # Create the button with a different colour depending
        # on whether the symptom is selected or not.
        button = ctk.CTkButton(frame,text=symptom,fg_color="green" if is_selected else None and check,hover_color="darkgreen" if is_selected else None and check,
            # lambda s=symptom captures the current symptom.
            # Without this, every button could end up using
            # the last symptom in the loop.
            command=lambda s=symptom: toggle_symptom(s) if check else None
        )

        button.pack(pady=5)

        # Store the actual button widget.
        active_button.append(button)

def validate_symptoms():
    """
    Prints the list of selected symptoms to the console.
    This function is called when the "Validate Symptoms" button is clicked.
    """
    if not selected_symptoms:
        print("aucun symptôme sélectionné.")
    else:
        print("symptômes sélectionnés:", selected_symptoms)
        print("recherche des conditions possibles...")

validate_button = ctk.CTkButton(
    app,
    text="Valider les symptômes",
    command=validate_symptoms
)
validate_button.pack(pady=10)



# Call search whenever the contents of the search bar change.
search_var.trace_add("write", search)

# Display the complete symptom list when the application starts.
search()

app.mainloop()
