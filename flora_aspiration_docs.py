# Nécessite une configuration complète de Selenium et de vos identifiants
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import requests
import time

# --- Vos identifiants et URLs ---
USERNAME = "fl.buonocore"
PASSWORD = "Ulysse:-1"
LOGIN_URL = "https://e-learning.crfpa.pre-barreau.com/accounts/login/"
TARGET_URL = "https://e-learning.crfpa.pre-barreau.com/desk/periods/43/courses/19/detail/"

# 1. Initialiser le navigateur (ex: Chrome)
driver = webdriver.Chrome()

try:
    print("Tentative de connexion...")
    driver.get(LOGIN_URL)

    wait = WebDriverWait(driver, 10)

    # 🍪 ÉTAPE 2 : Gérer la bannière de cookies 🍪
    try:
        print("Vérification de la bannière de cookies (10s)...")
        accept_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[@id='tarteaucitronAlertBig']//a[contains(text(), 'Accepter')] | //div[@id='tarteaucitronAlertBig']//button[contains(text(), 'Accepter')]"))
        )
        
        driver.execute_script("arguments[0].click();", accept_button)
        print("Bannière de cookies acceptée automatiquement.")
        time.sleep(1) 
        
    except TimeoutException:
        print("Pas de bannière de cookies trouvée ou gérée. Si la page est vide, assurez-vous de l'accepter manuellement.")
        time.sleep(3) 

    # 🔑 ÉTAPE 3 : Se connecter 🔑
    print("Saisie des identifiants...")
    
    username_field = wait.until(
        EC.visibility_of_element_located((By.ID, "id_username"))
    )
    username_field.send_keys(USERNAME)
    
    password_field = driver.find_element(By.ID, "id_password")
    password_field.send_keys(PASSWORD)
    
    login_button = driver.find_element(By.ID, "action_red")
    wait.until(EC.element_to_be_clickable((By.ID, "action_red")))
    login_button.click()
    
    print("Formulaire de connexion soumis.")
    
    # 🎯 ÉTAPE 4 : Navigation forcée vers la page cible correcte 🎯
    time.sleep(5) 
    
    print(f"Navigation forcée vers l'URL détaillée : {TARGET_URL}")
    driver.get(TARGET_URL)
    
    wait.until(EC.url_to_be(TARGET_URL))
    print("Page cible chargée.")
    
    # 5. Extraire les liens "Sujet" menant vers /view/
    time.sleep(3) 
    
    # NOUVEAU XPATH : Cible les liens qui contiennent '/documents/' et dont le texte commence par "Sujet"
    pdf_links = driver.find_elements(
        By.XPATH, 
        "//a[contains(@href, '/documents/') and starts-with(normalize-space(.), 'Sujet')]"
    )
    
    if not pdf_links:
        print("Aucun lien de document trouvé sur la page correspondant au critère 'Sujet'.")
        
    # 6. Téléchargement
    cookies = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
    
    for i, link_element in enumerate(pdf_links):
        view_url = link_element.get_attribute('href')
        link_text = link_element.text.strip()
        print(f"Préparation au téléchargement du fichier {i+1}/{len(pdf_links)} : {link_text} ({view_url})")
        
        # --- LOGIQUE DE TÉLÉCHARGEMENT MISE À JOUR ---
        
        # 6a. Transformer l'URL /view/ en une URL de téléchargement (supposition)
        # Souvent, il suffit de remplacer '/view/' par '/download/' ou '/export/' sur ces plateformes.
        # Sinon, nous devrons naviguer vers la page /view/ et trouver le VRAI lien PDF ou de téléchargement.
        download_url = view_url.replace('/view/', '/download/')
        
        print(f"   Tentative d'URL de téléchargement directe : {download_url}")
        
        try:
            # Récupérer le contenu avec l'URL de téléchargement supposée
            response = requests.get(download_url, cookies=cookies, stream=True, allow_redirects=True)
            response.raise_for_status() 
            
            # Vérification basique du type de contenu
            content_type = response.headers.get('Content-Type', '')
            if 'application/pdf' not in content_type and 'octet-stream' not in content_type:
                 print(f"   ATTENTION : Le type de contenu reçu ({content_type}) n'est pas un PDF direct. Poursuite...")
            
            # Nettoyage du nom de fichier
            file_name = f"{link_text}.pdf".replace(':', ' -').replace('/', '_').replace('\\', '_')
            
            with open(file_name, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"--> Succès : '{file_name}' sauvegardé.")
            
        except requests.exceptions.RequestException as req_err:
            print(f"--> Échec du téléchargement direct via /download/ pour {download_url} : {req_err}")
            print("   Veuillez vérifier manuellement si l'URL '/download/' fonctionne ou si une autre méthode est nécessaire.")

except Exception as e:
    print(f"Une erreur inattendue est survenue : {e}")

finally:
    driver.quit()
    print("Programme terminé.")