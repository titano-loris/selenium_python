import yaml
import os
import csv
#WebDriverWait est utilisé pour attendre qu'un événement se produise, avant l'exécution suivante. (gerer l'asynchrone) 
from selenium.webdriver.support.ui import WebDriverWait
# "BY" est utilisé pour spécifier éléments de recherche (ici il sert pour la location "XPATH" dans une page html).
from selenium.webdriver.common.by import By
# import du module "expected_conditions" et le nomer "EC" pour raccourcir l'utilisation.
from selenium.webdriver.support import expected_conditions as EC
# utiliser le mouse move
from selenium.webdriver.common.action_chains import ActionChains
#importer la fonction connexion 
from connexion import connexion, url_trustpilot
from selenium.webdriver.common.keys import Keys
import time, random
# utiliser plusieurs expressions des caractéres
import re
# mettre le format date dans la ligne date du fichier
import locale
from datetime import datetime
#anti_bot_sys detect
time.sleep(random.uniform(1.5, 4.2))


# ajouter la fonction "convertion_date" pour le format date
locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
def convertion_date(date_str):
    return datetime.strptime(date_str, "%d %B %Y").strftime("%d/%m/%Y")




# appel au fichier xpath.yaml pour recuperer les variables associer aux balises
def file():
    # recuperer le chemin courant 
    current_directory = os.getcwd()
    # Charger YAML  "xpath.yaml"
    # "r" signifit read pour lire le fichier yaml
    print("selenium_darty\\xpath.yaml", current_directory)
    with open("xpath.yaml", "r") as f:
        xpaths = yaml.safe_load(f)
    # Vérifiez si le fichier YAML a été chargé correctement
    if  xpaths is not None:
        print("chargement ok")
    else:
        print("Erreur lors du chargement du fichier YAML.")
    return xpaths


def scrap_trustpilote():
    # xpaths fournis les xpath de trustpilote
    xpaths = file()
    # connection trustpilote
    driver=connexion(url_trustpilot)
    wait=WebDriverWait(driver,10)
# recherche des données
    wait.until(
        EC.element_to_be_clickable((By.XPATH, xpaths['fenetre_cookies']['close']))
    ).click()
    time.sleep(0.5)
    champ_recherche=driver.find_element(By.XPATH, xpaths['actions']['champ_recherche'])
    champ_recherche.send_keys("darty")
    champ_recherche.send_keys(Keys.ENTER)
    print("recherche darty effectué")
    wait.until(
    EC.element_to_be_clickable((By.XPATH, xpaths['actions']['select_1']))
    ).click()
    title_element = wait.until(
    EC.visibility_of_element_located((By.XPATH, xpaths['actions']['title']))
    )
    #variable titre sert pour isole le mot "darty" et lower() retourne en lowercase 'darty' pour garder les caractére en minuscule
    title = title_element.text.lower()
    verification='darty'
    # verifier le bon titre
    if title == verification:
        print("verification du titre"+ title +"reussi")
    else:
        print("attention:"+title)
    # verification de url
    url = "https://fr.trustpilot.com/review/www.darty.com"
    driver.get(url)
    current=driver.current_url
    if url == current:
        print("la page existe")
    else:
        print("la page n'existe pas:", current)
    # ouvrir champs tout les avis
    wait.until(
    EC.element_to_be_clickable((By.XPATH, xpaths['actions']['tout_les_avis']))
    ).click()
# chemin du dossier csv
    folder = os.path.join(os.getcwd(), "csv")   
    # verification que le dossier exist
    os.makedirs(folder, exist_ok=True) 
    # chemin ver le fichier 
    csv_file= os.path.join(folder, "darty.csv")
# creation du fichier csv
    with open (csv_file, "w", newline="", encoding="utf-8") as f:
        writer=csv.writer(f)
        writer.writerow(["date", "note", "avis"])
        print("fichier csv établi:"+ csv_file)
        time.sleep(1)
# etablir le fichier csv
        
        # Compteur pour le nombre d'avis collectés
        avis_collectes = 0
        objectif_avis = 200

        while avis_collectes < objectif_avis:
            # Récupérer les éléments de la page courante
            revue = driver.find_elements(By.XPATH, xpaths['client']['fiche_xpath'])
            
            if not revue:
                print("Aucun avis trouvé sur cette page.")
                break

            # Parcourir les avis de la page
            for profile in revue:
                if avis_collectes >= objectif_avis:
                    break
                
                try:
                    # nom
                    format_date = profile.find_element(By.XPATH, xpaths["client"]["date_xpath"]).text.strip()
                    date = convertion_date(format_date)
                    
                    # extraction du nombre sur /5
                    img = profile.find_element(By.XPATH, xpaths["client"]["note_xpath"])
                    src = img.get_attribute("src")     
                    print(src)
                    
                    # extraire la note en fonction du src 
                    note = src.split("stars-")[1].split(".")[0]   
                    note = f"{note}/5"
                    
                    # commentaire client
                    avis = profile.find_element(By.XPATH, xpaths["client"]["comment_xpath"]).text.strip()
                    
                    # nettoyer les commentaires
                    avis_lignes = avis.split("\n")
                    avis = "\n".join(
                        line for line in avis_lignes
                        if not any(
                            excl in line.lower()
                            for excl in ["avis spontané", "avis vérifié"]
                        )
                        and not re.match(r".*\d{1,2}\s+\w+\s+20\d{2}.*", line)
                    ).strip()
                    
                    # ecrire les ligne dans csv
                    writer.writerow([date, note, avis])
                    avis_collectes += 1
                    print(f"Added: #{avis_collectes}")
                    
                except Exception :
                    print(f"Erreur lors de l'extraction d'un avis")
                    continue

            # Gestion de la pagination si on n'a pas encore atteint l'objectif
            if avis_collectes < objectif_avis:
                try:
                    page_suivant = driver.find_element(By.XPATH, xpaths["actions"]["page_suivante"])
                    
                    # mouse move
                    actions = ActionChains(driver)
                    actions.move_to_element(page_suivant).perform()
                    time.sleep(1)
                    
                    wait.until(EC.element_to_be_clickable((By.XPATH, xpaths["actions"]["page_suivante"])))
                    
                    # changer de page et relancer la boucle
                    page_suivant.click()
                    print("Passage à la page suivante...")
                    # Pause aléatoire pour simuler un comportement humain
                    time.sleep(random.uniform(4, 7))
                except Exception:
                    print("Fin du scraping (pas de page suivante ou erreur).")
                    break


















                    # # nom
                    # try:
                    #     format_date=profile.find_element(By.XPATH, xpaths["client"]["date_xpath"]).text.strip()
                    #     date=convertion_date(format_date)
                    # except:
                    #     date = ""
                    # # exctraction du nombre sur /5
                    # try:
                    #     img = profile.find_element(By.XPATH, xpaths["client"]["note_xpath"])
                    #     src = img.get_attribute("src")     
                    #     print(src)
                    # # extraire la note en fonction du src 
                    #     note = src.split("stars-")[1].split(".")[0]   
                    #     note = f"{note}/5"
                    # except:
                    #     note = ""
                    # # commentaire client
                    # try:
                    #     comment = profile.find_element(By.XPATH, xpaths["client"]["comment_xpath"]).text.strip()
                    # # nettoyer les commentaires (retirer date + "Avis spontané")
                    #     comment_lines = comment.split("\n")
                    #     comment = "\n".join(
                    #         line for line in comment_lines
                    #         if not any(
                    #             excl in line.lower()
                    #             for excl in ["avis spontané", "avis vérifié"]
                    #         )
                    #         and not re.match(r".*\d{1,2}\s+\w+\s+20\d{2}.*", line)   # supprime une date 
                    #     ).strip()
                    # except:
                    #     comment = ""

                    # # ecrire les ligne dans csv
                    # writer.writerow([date, note, comment])
                    # print(f"Added:#{i}")







                        # clicker sur la page suivante quand le dernier article est atteint   






                    # page_suivant = driver.find_element(By.XPATH, xpaths["actions"]["page_suivante"])
                    # if page_suivant.is_enabled():
                    #         # mouse move
                    #         actions = ActionChains(driver)
                    #         actions.move_to_element(page_suivant).perform()
                    #         time.sleep(1)
                    #         wait.until(EC.element_to_be_clickable((By.XPATH, xpaths["actions"]["page_suivante"])))
                    #         #changer de page et relancer la boucle
                    #         page_suivant.click()
                    #         print("page suivante")
                    #         time.sleep(3)
                    # else:
                    #         print("scraping darty terminé")
                    #         break
scrap_trustpilote()


# # ////// truc perso, injection javascript pour evité les interferences, mais uniquement pour certain cas précis "ne pas prendre en compte" 
#     # search_input = driver.find_element(By.XPATH, xpaths['actions']['formulaire'])
#     # driver.execute_script("arguments[0].value = 'selva';", search_input)
#     # time.sleep(1.5)
#     # search_input.send_keys(Keys.ENTER)
#     # print("Recherche 'selva' effectuée.")
# # ////////

