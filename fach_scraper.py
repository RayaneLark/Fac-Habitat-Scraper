import time
import requests
import json
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium

# Initialisation de session_state
if 'map' not in st.session_state:
    st.session_state.map = folium.Map(location=[48.8566, 2.3522], zoom_start=10)
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()
if 'message' not in st.session_state:
    st.session_state.message = {'text': '', 'type': ''}

def scrap_fach_data(selected_deps):
    # Step 1: Get JSON data from URL
    url = 'https://www.fac-habitat.com/fr/residences/json'
    response = requests.get(url)

    # Check response status
    if response.status_code == 200:
        # Convert content
        data = response.json()

        # Step 2: Filter residences located in selected departments and managed by Fac-Habitat
        residences_idf = [value for value in data.values() if value.get('cp')[:2] in selected_deps and value.get('gestionnaire') == 'FACH']

        # Step 3: Generate URLs for each residence
        base_url = "https://www.fac-habitat.com/fr/residences-etudiantes/id-{id}-{titre_fr}"
        urls = [base_url.format(id=residence['id'], titre_fr=residence["titre_fr"].lower().replace(" ", "-")) for residence in residences_idf]

        # Step 4: Check availability for each URL
        available_residences = []
        count = 0
        immediate_count = 0
        upcoming_count = 0

        # Initialize progress bar
        progress_text = "Recherche en cours. Veuillez patienter..."
        my_bar = st.progress(0, text=progress_text)
        total_urls = len(urls)

        # Clear existing markers from the map
        for layer in st.session_state.map._children.copy():
            if layer.startswith('marker'):
                del st.session_state.map._children[layer]

        for url in urls:
            count += 1

            response = requests.get(url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Search for the iframe tag because the availability is in the content of the iframe
                iframe = soup.find('iframe', class_='reservation')

                if iframe:
                    # Get the URL of the iframe
                    iframe_url = iframe['src']

                    # Make a request to get the content of the iframe
                    iframe_response = requests.get(iframe_url)

                    # Check response status
                    if iframe_response.status_code == 200:
                        iframe_soup = BeautifulSoup(iframe_response.text, 'html.parser')

                        # Search for the string "Disponibilité à venir" or "Disponibilité immédiate" in the content of the iframe
                        availability = "Aucune disponibilité"
                        for string in ["Disponibilité à venir", "Disponibilité immédiate"]:
                            if string in iframe_soup.get_text():
                                price = soup.find('em', itemprop='lowPrice').find('strong').text
                                availability = string
                                if string == "Disponibilité immédiate":
                                    immediate_count += 1
                                elif string == "Disponibilité à venir":
                                    upcoming_count += 1
                                # Extract residence information
                                residence_info = {
                                    "titre": residences_idf[urls.index(url)].get("titre_fr"),
                                    "ville": residences_idf[urls.index(url)].get("ville"),
                                    "cp": residences_idf[urls.index(url)].get("cp"),
                                    "prix": price,
                                    "url": url,
                                    "email": residences_idf[urls.index(url)].get("email"),
                                    "tel": residences_idf[urls.index(url)].get("tel"),
                                    "disponibilité": availability,
                                    "latitude": float(residences_idf[urls.index(url)].get("latitude")),
                                    "longitude": float(residences_idf[urls.index(url)].get("longitude"))
                                }
                                available_residences.append(residence_info)

            # Update progress bar
            progress = count / total_urls
            my_bar.progress(progress, text=progress_text)

        # Step 5: Display available residences summary
        if available_residences:
            st.session_state.message = {'text': f'{len(available_residences)} Résidences trouvées !', 'type': 'success'}
            st.session_state.df = pd.DataFrame(available_residences)
            st.session_state.df = st.session_state.df[['titre', 'ville', 'cp', 'prix', 'url', 'email', 'tel', 'disponibilité']]  # Reorder the columns

            # Add markers for each residence to the map
            for residence in available_residences:
                folium.Marker(
                    location=[residence["latitude"], residence["longitude"]],
                    popup=f"{residence['titre']}<br>Prix: {residence['prix']}<br><a href='{residence['url']}'>Lien</a>",
                    tooltip=residence['titre']
                ).add_to(st.session_state.map)
        else:
            st.session_state.message = {'text': "Aucune résidence disponible trouvée.", 'type': 'error'}
            st.session_state.df = pd.DataFrame()  # Clear the dataframe if no residences found

if __name__ == "__main__":
    st.title("Fac Habitat Disponibilité")

    # Sidebar for department selection
    st.sidebar.title("Filtrer par départements")
    # Liste complète des départements français
    all_deps = {
        '01': '01 - Ain', '02': '02 - Aisne', '03': '03 - Allier', '04': '04 - Alpes-de-Haute-Provence', '05': '05 - Hautes-Alpes',
        '06': '06 - Alpes-Maritimes', '07': '07 - Ardèche', '08': '08 - Ardennes', '09': '09 - Ariège', '10': '10 - Aube',
        '11': '11 - Aude', '12': '12 - Aveyron', '13': '13 - Bouches-du-Rhône', '14': '14 - Calvados', '15': '15 - Cantal',
        '16': '16 - Charente', '17': '17 - Charente-Maritime', '18': '18 - Cher', '19': '19 - Corrèze', '2A': '2A - Corse-du-Sud',
        '2B': '2B - Haute-Corse', '21': '21 - Côte-d\'Or', '22': '22 - Côtes-d\'Armor', '23': '23 - Creuse', '24': '24 - Dordogne',
        '25': '25 - Doubs', '26': '26 - Drôme', '27': '27 - Eure', '28': '28 - Eure-et-Loir', '29': '29 - Finistère',
        '30': '30 - Gard', '31': '31 - Haute-Garonne', '32': '32 - Gers', '33': '33 - Gironde', '34': '34 - Hérault',
        '35': '35 - Ille-et-Vilaine', '36': '36 - Indre', '37': '37 - Indre-et-Loire', '38': '38 - Isère', '39': '39 - Jura',
        '40': '40 - Landes', '41': '41 - Loir-et-Cher', '42': '42 - Loire', '43': '43 - Haute-Loire', '44': '44 - Loire-Atlantique',
        '45': '45 - Loiret', '46': '46 - Lot', '47': '47 - Lot-et-Garonne', '48': '48 - Lozère', '49': '49 - Maine-et-Loire',
        '50': '50 - Manche', '51': '51 - Marne', '52': '52 - Haute-Marne', '53': '53 - Mayenne', '54': '54 - Meurthe-et-Moselle',
        '55': '55 - Meuse', '56': '56 - Morbihan', '57': '57 - Moselle', '58': '58 - Nièvre', '59': '59 - Nord',
        '60': '60 - Oise', '61': '61 - Orne', '62': '62 - Pas-de-Calais', '63': '63 - Puy-de-Dôme', '64': '64 - Pyrénées-Atlantiques',
        '65': '65 - Hautes-Pyrénées', '66': '66 - Pyrénées-Orientales', '67': '67 - Bas-Rhin', '68': '68 - Haut-Rhin', '69': '69 - Rhône',
        '70': '70 - Haute-Saône', '71': '71 - Saône-et-Loire', '72': '72 - Sarthe', '73': '73 - Savoie', '74': '74 - Haute-Savoie',
        '75': '75 - Paris', '76': '76 - Seine-Maritime', '77': '77 - Seine-et-Marne', '78': '78 - Yvelines', '79': '79 - Deux-Sèvres',
        '80': '80 - Somme', '81': '81 - Tarn', '82': '82 - Tarn-et-Garonne', '83': '83 - Var', '84': '84 - Vaucluse',
        '85': '85 - Vendée', '86': '86 - Vienne', '87': '87 - Haute-Vienne', '88': '88 - Vosges', '89': '89 - Yonne',
        '90': '90 - Territoire de Belfort', '91': '91 - Essonne', '92': '92 - Hauts-de-Seine', '93': '93 - Seine-Saint-Denis',
        '94': '94 - Val-de-Marne', '95': '95 - Val-d\'Oise'
    }
    
    selected_deps = st.sidebar.multiselect("Sélectionnez les départements", options=list(all_deps.keys()), format_func=lambda x: all_deps[x])

    if st.button("Lancer la recherche"):
        if selected_deps:
            scrap_fach_data(selected_deps)
        else:
            st.session_state.message = {'text': 'Veuillez sélectionner au moins un département.', 'type': 'error'}

    # Afficher le message stocké
    if st.session_state.message['text']:
        if st.session_state.message['type'] == 'success':
            st.success(st.session_state.message['text'])
        elif st.session_state.message['type'] == 'error':
            st.error(st.session_state.message['text'], icon="🚫")

    # Toujours afficher la carte et le tableau s'ils existent
    if not st.session_state.df.empty:
        st.dataframe(st.session_state.df)
    st_folium(st.session_state.map, width=725, height=500)
