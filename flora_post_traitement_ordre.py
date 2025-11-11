import os
import csv
import re
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError

# --- Configuration ---
REPERTOIRE_COURANT = "."
NOM_FICHIER_CSV = "synthese_pdf.csv"

# Constante pour le BOM UTF-8 (nécessaire pour forcer Excel à lire le bon encodage)
UTF8_BOM = b'\xef\xbb\xbf'

def extract_sujet_and_last_line(pdf_path):
    # ... (Le contenu de cette fonction reste inchangé, car elle extrait les données) ...
    """
    Extrait le bloc d'intitulé "Sujet" et la dernière ligne conditionnelle d'un PDF.
    """
    
    intitule_sujet_bloc = "Non trouvé"
    derniere_ligne = ""

    try:
        reader = PdfReader(pdf_path)
        
        num_pages = len(reader.pages)
        if num_pages == 0:
            return intitule_sujet_bloc, derniere_ligne

        # 1. Extraction du bloc d'intitulé "Sujet" sur la première page
        first_page_text = reader.pages[0].extract_text()
        
        if first_page_text:
            # Séparer le texte de la première page en lignes et nettoyer les espaces
            all_lines = [line.strip() for line in first_page_text.split('\n') if line.strip()]
            
            sujet_index = -1
            
            # Rechercher l'index de la ligne qui commence par "Sujet" dans les 20 premières lignes
            for i, line in enumerate(all_lines[:20]):
                match = re.search(r"^\s*Sujet.*", line, re.IGNORECASE)
                if match:
                    sujet_index = i
                    break 

            if sujet_index != -1:
                # Définir les limites du bloc (1 ligne avant, 1 ligne après)
                start_index = max(0, sujet_index - 1)
                end_index = min(len(all_lines), sujet_index + 2)
                
                # Joindre les lignes avec le séparateur '; '
                intitule_sujet_bloc = '; '.join(all_lines[start_index:end_index])
            
            # 2. Extraction conditionnelle de la dernière ligne
            if "Commentaire" not in intitule_sujet_bloc:
                last_page_text = reader.pages[-1].extract_text()
                
                if last_page_text:
                    lines = [line.strip() for line in last_page_text.split('\n') if line.strip()]
                    if lines:
                        derniere_ligne = lines[-1]

    except PdfReadError: 
        print(f"  [ERREUR] Le fichier {os.path.basename(pdf_path)} est corrompu ou illisible.")
    except Exception as e:
        print(f"  [ERREUR] Impossible de traiter {os.path.basename(pdf_path)}: {e}")

    return intitule_sujet_bloc, derniere_ligne
# ------------------------------------------------------------------------------------------------


def get_sujet_number_for_sorting(filename):
    """
    Extrait le numéro du sujet d'un nom de fichier et le formate en 3 chiffres.
    Ex: "Sujet 5 - Droit.pdf" -> 005
    """
    # 1. Rechercher un nombre après "Sujet"
    match = re.search(r"Sujet\s*(\d+)", filename, re.IGNORECASE)
    
    if match:
        number = int(match.group(1))
        # 2. Formater le nombre en une chaîne de 3 chiffres avec des zéros à gauche
        return f"{number:03d}"
    
    # Retourner une chaîne vide ou autre pour les fichiers qui ne correspondent pas, afin qu'ils soient triés à la fin
    return "999" 


def generate_synthesis_csv(directory):
    """
    Génère le fichier CSV de synthèse en incluant le tri par numéro de sujet.
    """
    
    pdf_files = [f for f in os.listdir(directory) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print("Aucun fichier PDF trouvé dans le répertoire courant.")
        return

    print(f"Traitement de {len(pdf_files)} fichiers PDF...")

    data_to_write = []

    # 1. EXTRACTION ET MISE EN FORME DES DONNÉES EN MÉMOIRE
    for i, filename in enumerate(pdf_files):
        pdf_path = os.path.join(directory, filename)
        print(f"  Extraction ({i+1}/{len(pdf_files)}): {filename}")
        
        sujet, last_line = extract_sujet_and_last_line(pdf_path)
        sujet_formaté = get_sujet_number_for_sorting(filename)
        
        # Stocker les données avec le numéro formaté (qui servira pour le tri)
        data_to_write.append({
            'Sujet_Formaté': sujet_formaté, # Utilisé uniquement pour le tri
            'Nom_Fichier': filename,
            'Intitule_Sujet': sujet,
            'Derniere_Ligne_Conditionnelle': last_line
        })

    # 2. TRI DES DONNÉES
    print("Tri des données par numéro de sujet...")
    data_to_write.sort(key=lambda x: x['Sujet_Formaté'])


    # 3. ÉCRITURE DU CSV FINAL
    # Ouvrir en mode binaire pour écrire le BOM
    with open(NOM_FICHIER_CSV, 'wb') as f:
        f.write(UTF8_BOM) 
        
        # Rouvrir en mode ajout texte pour l'écriture CSV
        with open(NOM_FICHIER_CSV, 'a', newline='', encoding='utf-8') as csvfile:
            # On retire 'Sujet_Formaté' des en-têtes du fichier final
            fieldnames = ['Nom_Fichier', 'Intitule_Sujet', 'Derniere_Ligne_Conditionnelle']
            
            # Configuration du DictWriter avec les guillemets (pour éviter les problèmes de colonnes)
            writer = csv.DictWriter(
                csvfile, 
                fieldnames=fieldnames, 
                delimiter=';', 
                quoting=csv.QUOTE_ALL
            )

            writer.writeheader() # Écriture de l'en-tête du CSV

            # Écriture des données triées
            for row in data_to_write:
                # Créer un dictionnaire de sortie sans la clé 'Sujet_Formaté'
                output_row = {k: row[k] for k in fieldnames}
                writer.writerow(output_row)

    print(f"\n✅ Synthèse terminée et triée. Le fichier CSV a été créé : **{NOM_FICHIER_CSV}**")


if __name__ == "__main__":
    generate_synthesis_csv(REPERTOIRE_COURANT)