import os
import re

# --- Configuration ---
FICHIER_ENTREE = "synthese_pdf.csv"  # Le fichier CSV généré et trié
FICHIER_SORTIE = "synthese_notes.md"
SEPARATEUR = ';'
TITRES = ['Fichier', 'Sujet', 'Dernière Ligne']

def generate_markdown_notes():
    """
    Lit le fichier CSV, crée un bloc d'information complet pour chaque ligne,
    avec la dernière colonne dans un bloc déroulant.
    """
    
    if not os.path.exists(FICHIER_ENTREE):
        print(f"❌ Erreur : Le fichier d'entrée '{FICHIER_ENTREE}' est introuvable.")
        return

    print(f"Lecture de '{FICHIER_ENTREE}' et génération de '{FICHIER_SORTIE}'...")

    try:
        # Lire le fichier, en ignorant la première ligne (les en-têtes CSV)
        # Note: L'encodage est UTF-8 car c'est ce que nous avons écrit.
        with open(FICHIER_ENTREE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Supprimer la ligne d'en-tête (le BOM la rend parfois vide ou incorrecte)
        data_lines = [line for line in lines if line.strip() and not TITRES[0] in line]
        
        if not data_lines:
            print("Le fichier d'entrée est vide (ou ne contient que les en-têtes).")
            return
            
        markdown_content = []
        
        # Parcourir chaque ligne de données
        for line in data_lines:
            # 1. Nettoyer et diviser la ligne
            # strip() et replace('"', '') sont importants pour les données générées en QUOTE_ALL
            elements = [el.strip().replace('"', '') for el in line.split(SEPARATEUR)]
            
            if len(elements) < len(TITRES):
                print(f"⚠️ Avertissement : Ligne ignorée (format incorrect) : {line.strip()}")
                continue
            
            nom_fichier = elements[0].strip()
            intitule_sujet = "".join(elements[1:3]).strip()
            derniere_ligne_texte = "".join(elements[3:])

            # --- 2. Formatage de l'Intitulé du Sujet ---
            # Remplacer les séparateurs internes '; ' par des retours à la ligne Markdown (<br> ou double espace)
            sujet_formate = intitule_sujet.replace('; ', '  \n')
            
            # --- 3. Construction du Bloc Déroulant (Détails) ---
            
            details_bloc = ""
            if derniere_ligne_texte:
                # Utilisation du format HTML <details> pour une compatibilité maximale
                details_bloc = f"""<details>
<summary>👁️ {TITRES[2]}</summary>

{derniere_ligne_texte}
</details>"""
            
            # --- 4. Construction du Callout [!info] ---
            
            # Nous utilisons le Nom du Fichier comme titre du Callout pour faciliter le repérage
            
            callout_content = f"""
> **{TITRES[1]}** :
> 
> {sujet_formate}
>
"""
            # Ajouter le bloc déroulant à l'intérieur du callout
            # Note: Le contenu HTML doit souvent être entouré de tags vides (comme le simple >) dans un callout
            callout_content += details_bloc.replace('\n', '\n> ')
            
            # Nettoyage et finalisation du bloc [!info]
            markdown_box = f"\n> [!info] Sujet : {nom_fichier}\n" + callout_content.strip()
            
            markdown_content.append(markdown_box.strip())


        # 5. Écriture du fichier Markdown
        with open(FICHIER_SORTIE, 'w', encoding='utf-8') as f:
            f.write("# 📝 Synthèse des Documents\n\n")
            f.write("\n\n---\n\n".join(markdown_content))
            f.write("\n\n---")
            
        print(f"\n✅ Fichier Markdown généré avec succès : **{FICHIER_SORTIE}**")

    except Exception as e:
        print(f"❌ Une erreur est survenue lors du traitement : {e}")


if __name__ == "__main__":
    generate_markdown_notes()