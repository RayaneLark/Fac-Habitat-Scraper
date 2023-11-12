# fach_scraper.py

import requests
import json
from bs4 import BeautifulSoup
import os

def scrap_fach_data():
    # Step 1: Get JSON data from URL
    url = 'https://www.fac-habitat.com/fr/residences/json'
    response = requests.get(url)

    # Check response status
    if response.status_code == 200:
        # Convert content
        data = response.json()

        # Step 2: Filter residences located in Île-de-France and managed by Fac-Habitat
        idf_deps = {'75', '78', '91', '92', '93', '94', '95'}

        residences_idf = [value for value in data.values() if value.get('cp')[:2] in idf_deps and value.get('gestionnaire') == 'FACH']

        # Step 3: Save filtered data to a JSON file
        with open('output.json', 'w', encoding='utf-8') as json_file:
            json.dump(residences_idf, json_file, ensure_ascii=False, indent=2)

        # Step 4: Generate URLs for each residence
        base_url = "https://www.fac-habitat.com/fr/residences-etudiantes/id-{id}-{titre_fr}"
        urls = [base_url.format(id=residence['id'], titre_fr=residence["titre_fr"].lower().replace(" ", "-")) for residence in residences_idf]

        # Step 5: Check availability for each URL
        available_residences = []
        count = 0
        immediate_count = 0
        upcoming_count = 0
        for url in urls:
            count += 1

            # Clear terminal screen
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{count}/{len(urls)}: {url}")
            response = requests.get(url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Search for the iframe tag because the availability is in the content of the iframe
                iframe = soup.find('iframe')

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
                                availability = string
                                if string == "Disponibilité immédiate":
                                    immediate_count += 1
                                elif string == "Disponibilité à venir":
                                    upcoming_count += 1
                                # Extract residence information
                                residence_info = {
                                    "id": residences_idf[urls.index(url)].get("id"),
                                    "url": url,
                                    "cp": residences_idf[urls.index(url)].get("cp"),
                                    "ville": residences_idf[urls.index(url)].get("ville"),
                                    "titre": residences_idf[urls.index(url)].get("titre_fr"),
                                    "email": residences_idf[urls.index(url)].get("email"),
                                    "tel": residences_idf[urls.index(url)].get("tel"),
                                    "available": availability
                                }
                                available_residences.append(residence_info)

                    # If the response status is not 200 (OK) for the iframe
                    else:
                        print(f"Error during request for the iframe of {url}. Response status: {iframe_response.status_code}")

                # If the iframe tag is not found or if the src attribute is not found
                else:
                    print(f"{url} : Aucune disponibilité (iframe non trouvée)")

            # If the response status is not 200 (OK) for the residence URL
            else:
                print(f"Error during request for {url}. Response status: {response.status_code}")

        # Step 6: Save and print available residences
        with open('available_residences.json', 'w', encoding='utf-8') as json_file:
            json.dump(available_residences, json_file, ensure_ascii=False, indent=2)
        print(f"Résidence disponibles immédiatement: {immediate_count}")
        print(f"Résidence disponibles prochainement: {upcoming_count}")

if __name__ == "__main__":
    scrap_fach_data()