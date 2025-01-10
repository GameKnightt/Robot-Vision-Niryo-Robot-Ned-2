import json
import requests
import numpy as np
import cv2
from pyniryo import*
from time import sleep as delay

robot_ip = "172.21.182.53"  # Remplacez par l'IP de votre robot
robot = NiryoRobot(robot_ip)

color_list = [
    [15, 50, 255],
    [255, 0, 0],
    [0, 255, 0],
]

#robot.pull_air_vacuum_pump()  # Activer la ventouse
#robot.push_air_vacuum_pump()  # Désactiver la ventouse

def define_tcp():
    # Définition du TCP pour la ventouse
    # Values in meters [x, y, z, roll, pitch, yaw]
    VACUUM_TCP = [0.05, 0, 0, 0, 0, 0]  # Adjust these values based on your specific vacuum tool

    # Configuration du TCP
    robot.reset_tcp()
    print('TCP Reset')
    robot.set_tcp(VACUUM_TCP)
    print('TCP Set')
    robot.enable_tcp(True)
    print('TCP Activate')

def save_all_positions(robot):
    positions = {}
    position_names = []
    
    # Get list of positions to save
    print("\n=== Position Recording Setup ===")
    print("Enter position names (one per line). Enter empty line when done.")
    while True:
        name = input("Position name (or press Enter to finish): ").strip()
        if not name:
            break
        position_names.append(name)
    
    print("\n=== Starting Position Recording ===")
    # Record each position
    for position_name in position_names:
        input(f"\nPlease move robot to position '{position_name}' then press Enter to save...")
        current_pose = robot.get_pose().to_list()
        positions[position_name] = current_pose
        print(f"Position '{position_name}' saved!")
    
    # Save all positions to file
    with open('positions.json', 'w') as f:
        json.dump(positions, f, indent=4)
    
    # Show recap
    print("\n=== Saved Positions Recap ===")
    for name, pose in positions.items():
        print(f"\nPosition: {name}")
        print(f"X: {pose[0]:.2f}, Y: {pose[1]:.2f}, Z: {pose[2]:.2f}")
        print(f"RX: {pose[3]:.2f}, RY: {pose[4]:.2f}, RZ: {pose[5]:.2f}")
    
    print("\nAll positions have been saved to positions.json")
    return positions

def move_to_saved_positions(robot):
    # Load saved positions
    with open('positions.json', 'r') as f:
        positions = json.load(f)
    
    while True:
        # Show available positions
        print("\n=== Available Positions ===")
        for i, name in enumerate(positions.keys(), 1):
            print(f"{i}. {name}")
        print("0. Exit")
        
        # Get user choice
        choice = input("\nEnter position number to move to (0 to exit): ")
        if choice == '0':
            break
            
        try:
            index = int(choice) - 1
            position_name = list(positions.keys())[index]
            target_pose = positions[position_name]
            
            # Confirm movement
            print(f"\nMoving to position: {position_name}")
            print(f"Target coordinates:")
            print(f"X: {target_pose[0]:.2f}, Y: {target_pose[1]:.2f}, Z: {target_pose[2]:.2f}")
            print(f"RX: {target_pose[3]:.2f}, RY: {target_pose[4]:.2f}, RZ: {target_pose[5]:.2f}")
            
            confirm = input("Confirm movement? (y/n): ")
            if confirm.lower() == 'y':
                # Move robot to position
                robot.move_pose(target_pose)
                print(f"Moved to position: {position_name}")
            else:
                print("Movement cancelled")
                
        except (ValueError, IndexError):
            print("Invalid selection")
            
        except Exception as e:
            print(f"Error moving robot: {e}")

def get_camera_image():
    try:
        response = requests.get("http://172.21.182.15:8000/image.jpg")
        if response.status_code == 200:
            # Convertir l'image reçue en format numpy array
            nparr = np.frombuffer(response.content, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return img
    except Exception as e:
        print(f"Erreur lors de la récupération de l'image: {e}")
    return None

def save_token_colors():
    colors = {}
    
    while True:
        # Capturer une image
        img = get_camera_image()
        if img is None:
            print("Impossible de capturer l'image")
            continue
            
        # Afficher l'image
        cv2.imshow("Image", img)
        print("\nUtilisez la souris pour sélectionner une zone de couleur.")
        print("Instructions:")
        print("1. Entrez le nom de la couleur (ex: 'rouge', 'vert', etc.)")
        print("2. Cliquez et faites glisser pour sélectionner une zone")
        print("3. Appuyez sur ENTER pour confirmer la sélection")
        print("4. Appuyez sur 'q' pour terminer")
        
        color_name = input("\nNom de la couleur (ou 'q' pour quitter): ")
        if color_name.lower() == 'q':
            break
            
        # Fonction de callback pour la sélection de la zone
        roi = cv2.selectROI("Image", img, False)
        if roi[2] and roi[3]:  # Si une zone valide a été sélectionnée
            # Extraire la zone sélectionnée
            x, y, w, h = roi
            selected_region = img[int(y):int(y+h), int(x):int(x+w)]
            
            # Calculer la moyenne des couleurs RGB
            avg_color = np.mean(selected_region, axis=(0, 1))
            colors[color_name] = avg_color.tolist()
            
            print(f"Couleur moyenne pour {color_name}: {colors[color_name]}")
        
        cv2.destroyAllWindows()
    
    # Sauvegarder les couleurs dans un fichier JSON
    with open('couleurs.json', 'w') as f:
        json.dump(colors, f, indent=4)
    print("\nLes couleurs ont été sauvegardées dans couleurs.json")
    return colors

def save_crop_zone():
    """Permet de définir et sauvegarder la zone de prise des pièces"""
    img = get_camera_image()
    if img is None:
        print("Impossible de capturer l'image")
        return None
        
    print("\nSélectionnez la zone de prise des pièces")
    print("1. Cliquez et faites glisser pour sélectionner la zone")
    print("2. Appuyez sur ENTER pour confirmer")
    print("3. Appuyez sur 'c' pour annuler")
    
    roi = cv2.selectROI("Selection zone de prise", img, False)
    cv2.destroyAllWindows()
    
    if roi[2] and roi[3]:  # Si une zone valide a été sélectionnée
        crop_params = {
            "x": int(roi[0]),
            "y": int(roi[1]),
            "width": int(roi[2]),
            "height": int(roi[3])
        }
        # Sauvegarder les paramètres de recadrage
        with open('crop_params.json', 'w') as f:
            json.dump(crop_params, f, indent=4)
        print("Zone de prise sauvegardée")
        return crop_params
    return None

def detect_token(img, colors, crop_params):
    """Détecte la couleur du jeton dans la zone de prise recadrée"""
    try:
        # Recadrer l'image selon les paramètres
        roi = img[crop_params["y"]:crop_params["y"]+crop_params["height"], 
                 crop_params["x"]:crop_params["x"]+crop_params["width"]]
        
        # Afficher la zone recadrée pour debug
        cv2.imshow("Zone de prise", roi)
        cv2.waitKey(1)
        
        # Calculer la couleur moyenne dans la ROI
        avg_color = cv2.mean(roi)[:3]  # On ne garde que RGB
        
        # Trouver la couleur la plus proche
        best_match = None
        min_diff = float('inf')
        
        for color_name, color_values in colors.items():
            if color_name.lower() == "sol":  # Ignorer la couleur du sol
                continue
            
            # Calculer la différence de couleur (distance euclidienne)
            diff = np.sqrt(sum((a - b) ** 2 for a, b in zip(avg_color, color_values)))
            
            if diff < min_diff:
                min_diff = diff
                best_match = color_name
        
        # Si la différence est trop grande, pas de jeton
        if min_diff > 100:  # Seuil à ajuster
            print(f"Aucune correspondance de couleur trouvée (diff: {min_diff})")
            return None, None
            
        print(f"Couleur détectée: {best_match} (diff: {min_diff})")
        center_x = crop_params["x"] + crop_params["width"]//2
        center_y = crop_params["y"] + crop_params["height"]//2
        return best_match, (center_x, center_y)
        
    except Exception as e:
        print(f"Erreur lors de la détection: {e}")
        return None, None

def get_led_color(color_name):
    """Convertit le nom de la couleur en valeurs RGB pour l'anneau LED"""
    led_colors = {
        "Rouge": [255, 0, 0],
        "Vert": [0, 255, 0],
        "Bleu": [0, 0, 255],
        "Noir": [10, 10, 10],  # Gris très sombre pour représenter le noir
    }
    return led_colors.get(color_name, [255, 255, 255])  # Blanc par défaut

def pick_and_place(robot, color, positions):
    """Prend un jeton de la couleur spécifiée et le place à la position correspondante"""
    try:
        # Charger les positions sauvegardées
        with open('positions.json', 'r') as f:
            saved_positions = json.load(f)
        
        # Récupérer toutes les positions nécessaires
        pickup_position = saved_positions.get(f"pick_{color.lower()}")
        place_position = saved_positions.get(f"place_{color.lower()}")
        intermediate_position = saved_positions.get("intermediate")  # Position sécurisée intermédiaire générale
        intermediate_place_position = saved_positions.get(f"intermediate_place_{color.lower()}")  # Position intermédiaire spécifique
        
        if not all([pickup_position, place_position, intermediate_position, intermediate_place_position]):
            print(f"Positions manquantes pour la couleur {color}")
            return False

        # Changer la couleur de l'anneau LED
        led_color = get_led_color(color)
        robot.led_ring_solid(led_color)
        print(f"Anneau LED changé pour la couleur: {color}")

        # Mouvement vers la position intermédiaire générale après la prise
        print("Déplacement vers la position intermédiaire générale...")
        robot.move_pose(intermediate_position)
            
        # Séquence de prise
        print("Déplacement vers la position de prise...")
        robot.move_pose(pickup_position)
        robot.pull_air_vacuum_pump()  # Activer la ventouse
        delay(0.25)  # Attendre que le jeton soit bien saisi
        
        # Mouvement vers la position intermédiaire générale après la prise
        print("Déplacement vers la position intermédiaire générale...")
        robot.move_pose(intermediate_position)
        
        # Mouvement vers la position intermédiaire spécifique avant la pose
        print(f"Déplacement vers la position intermédiaire de pose {color}...")
        robot.move_pose(intermediate_place_position)
        
        # Mouvement vers la position de pose
        print("Déplacement vers la position de pose...")
        robot.move_pose(place_position)
        robot.push_air_vacuum_pump()  # Désactiver la ventouse
        delay(0.25)  # Attendre que le jeton soit bien déposé
        
        # Retour à la position intermédiaire spécifique
        print("Retour à la position intermédiaire spécifique...")
        robot.move_pose(intermediate_place_position)
        
        # Remettre l'anneau LED en mode alternatif à la fin
        robot.led_ring_alternate(color_list)
        return True
        
    except Exception as e:
        print(f"Erreur lors du pick and place: {e}")
        robot.led_ring_alternate(color_list)  # Remettre l'anneau en mode alternatif en cas d'erreur
        return False

def main():
    """Fonction principale du programme"""
    try:
        # Charger les couleurs
        with open('couleurs.json', 'r') as f:
            colors = json.load(f)
        
        # Charger les positions
        with open('positions.json', 'r') as f:
            positions = json.load(f)
        
        # Demander si on veut redéfinir la zone de prise
        redefine = input("Voulez-vous redéfinir la zone de prise ? (o/n): ").lower() == 'o'
        
        # Charger ou définir les paramètres de recadrage
        crop_params = None
        if redefine:
            crop_params = save_crop_zone()
        else:
            try:
                with open('crop_params.json', 'r') as f:
                    crop_params = json.load(f)
            except FileNotFoundError:
                print("Aucune zone de prise définie. Définition nécessaire.")
                crop_params = save_crop_zone()
        
        if crop_params is None:
            print("Impossible de continuer sans zone de prise définie")
            return
            
        # Vérifier que la position Home existe
        if "home" not in positions:
            print("Erreur: Position 'home' non définie dans positions.json")
            return
        
        no_token_count = 0
        
        # Aller à la position home au début
        print("Déplacement vers la position Home initiale...")
        robot.move_pose(positions["home"])
        
        while True:
            # Retourner à la position home avant chaque détection
            print("\nRetour à la position Home pour la détection...")
            robot.move_pose(positions["home"])
            delay(0.25)  # Attendre la stabilisation
            
            img = get_camera_image()
            if img is None:
                continue
            
            # Utiliser la nouvelle version de detect_token avec les paramètres de recadrage
            color, position = detect_token(img, colors, crop_params)
            
            if color is None:
                no_token_count += 1
                print("Aucun jeton détecté")
                if no_token_count >= 3:  # Après 3 tentatives sans jeton
                    print("Plus de jetons à trier")
                    print("Robot déjà en position Home")
                    break
                delay(1)
                continue
            
            no_token_count = 0  # Réinitialiser le compteur si un jeton est trouvé
            print(f"Jeton {color} détecté à la position {position}")
            
            # Exécuter la séquence pick and place
            if pick_and_place(robot, color, positions):
                print(f"Jeton {color} trié avec succès")
            else:
                print(f"Échec du tri du jeton {color}")
            
            delay(1)  # Pause entre chaque cycle
            
    except KeyboardInterrupt:
        print("\nArrêt du programme demandé par l'utilisateur")
        print("Retour à la position Home...")
        robot.move_pose(positions["home"])
        print("Robot en position Home")
    except Exception as e:
        print(f"Erreur dans le programme principal: {e}")
    finally:
        robot.close_connection()

if __name__ == "__main__":
    define_tcp()
    robot.led_ring_alternate(color_list)
    main()
    delay(3)
    robot.close_connection()

# Fin du programme