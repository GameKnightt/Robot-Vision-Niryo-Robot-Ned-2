import json
import requests
import numpy as np
import cv2
from pyniryo import*
from time import sleep as delay

robot_ip = "172.21.182.53"  # Remplacez par l'IP de votre robot
robot = NiryoRobot(robot_ip)
conveyor_id = robot.set_conveyor()

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

def save_all_positions(robot):
    # Charger les positions existantes
    try:
        with open('positions.json', 'r') as f:
            positions = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        positions = {}

    while True:
        print("\n=== Positions enregistrées ===")
        for name, pose in positions.items():
            print(f"\nPosition: {name}")
            print(f"X: {pose[0]:.2f}, Y: {pose[1]:.2f}, Z: {pose[2]:.2f}")
            print(f"RX: {pose[3]:.2f}, RY: {pose[4]:.2f}, RZ: {pose[5]:.2f}")
        
        print("\nOptions:")
        print("1. Ajouter/Modifier une position")
        print("2. Supprimer une position")
        print("3. Terminer")
        
        choice = input("\nChoisissez une option (1-3): ")
        
        if choice == "1":
            name = input("\nNom de la position: ").strip()
            if name:
                # Vérifier si la position existe déjà
                if name in positions:
                    print(f"\nLa position '{name}' existe déjà.")
                    print("Le robot va se déplacer à cette position...")
                    try:
                        robot.move_pose(positions[name])
                        confirm = input("Voulez-vous modifier cette position ? (o/n): ").lower()
                        if confirm != 'o':
                            print("Modification annulée")
                            continue
                    except Exception as e:
                        print(f"Erreur lors du déplacement: {e}")
                        continue

                input(f"Déplacez le robot à la position '{name}' puis appuyez sur Enter...")
                current_pose = robot.get_pose().to_list()
                positions[name] = current_pose
                print(f"\nPosition '{name}' enregistrée:")
                print(f"X: {current_pose[0]:.2f}, Y: {current_pose[1]:.2f}, Z: {current_pose[2]:.2f}")
                print(f"RX: {current_pose[3]:.2f}, RY: {current_pose[4]:.2f}, RZ: {current_pose[5]:.2f}")
                
        elif choice == "2":
            if not positions:
                print("Aucune position à supprimer")
                continue
                
            print("\nPositions disponibles:")
            for i, name in enumerate(positions.keys(), 1):
                print(f"{i}. {name}")
                
            try:
                idx = int(input("\nEntrez le numéro de la position à supprimer (0 pour annuler): "))
                if idx > 0:
                    pos_name = list(positions.keys())[idx-1]
                    confirm = input(f"Confirmer la suppression de {pos_name}? (o/n): ").lower()
                    if confirm == 'o':
                        del positions[pos_name]
                        print(f"Position {pos_name} supprimée")
            except (ValueError, IndexError):
                print("Sélection invalide")
                
        elif choice == "3":
            break
    
    # Sauvegarder les modifications
    with open('positions.json', 'w') as f:
        json.dump(positions, f, indent=4)
    print("\nPositions sauvegardées dans positions.json")
    return positions

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
    # Charger les couleurs existantes
    try:
        with open('couleurs.json', 'r') as f:
            colors = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        colors = {}

    while True:
        print("\n=== Couleurs enregistrées ===")
        for name, value in colors.items():
            print(f"{name}: {value}")
        
        print("\nOptions:")
        print("1. Ajouter/Modifier une couleur")
        print("2. Supprimer une couleur")
        print("3. Terminer")
        
        choice = input("\nChoisissez une option (1-3): ")
        
        if choice == "1":
            # Capturer une image
            img = get_camera_image()
            if img is None:
                print("Impossible de capturer l'image")
                continue
                
            cv2.imshow("Image", img)
            print("\nUtilisez la souris pour sélectionner une zone de couleur.")
            print("Instructions:")
            print("1. Entrez le nom de la couleur")
            print("2. Cliquez et faites glisser pour sélectionner une zone")
            print("3. Appuyez sur ENTER pour confirmer la sélection")
            
            color_name = input("\nNom de la couleur: ").strip()
            if color_name:
                roi = cv2.selectROI("Image", img, False)
                if roi[2] and roi[3]:
                    x, y, w, h = roi
                    selected_region = img[int(y):int(y+h), int(x):int(x+w)]
                    avg_color = np.mean(selected_region, axis=(0, 1))
                    colors[color_name] = avg_color.tolist()
                    print(f"Couleur {color_name} enregistrée: {colors[color_name]}")
            
            cv2.destroyAllWindows()
            
        elif choice == "2":
            if not colors:
                print("Aucune couleur à supprimer")
                continue
                
            print("\nCouleurs disponibles:")
            for i, name in enumerate(colors.keys(), 1):
                print(f"{i}. {name}")
                
            try:
                idx = int(input("\nEntrez le numéro de la couleur à supprimer (0 pour annuler): "))
                if idx > 0:
                    color_name = list(colors.keys())[idx-1]
                    confirm = input(f"Confirmer la suppression de {color_name}? (o/n): ").lower()
                    if confirm == 'o':
                        del colors[color_name]
                        print(f"Couleur {color_name} supprimée")
            except (ValueError, IndexError):
                print("Sélection invalide")
                
        elif choice == "3":
            break
    
    # Sauvegarder les modifications
    with open('couleurs.json', 'w') as f:
        json.dump(colors, f, indent=4)
    print("\nCouleurs sauvegardées dans couleurs.json")
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
    # Normaliser le nom de la couleur en minuscules
    color_name = color_name.lower()
    
    led_colors = {
        "rouge": [255, 0, 0],
        "vert": [0, 255, 0],
        "bleu": [0, 0, 255],
        "noir": [10, 10, 10],
        # Ajouter des variantes possibles des noms de couleurs
        "red": [255, 0, 0],
        "green": [0, 255, 0],
        "blue": [0, 0, 255],
        "black": [10, 10, 10]
    }
    
    # Si la couleur n'est pas trouvée, utiliser le blanc
    color_values = led_colors.get(color_name, [255, 255, 255])
    print(f"Couleur LED sélectionnée pour {color_name}: {color_values}")  # Debug
    return color_values

def activate_conveyor(robot, duration=5):
    """Active le convoyeur pendant une durée spécifiée"""
    try:
        robot.run_conveyor(conveyor_id, speed=50, direction=ConveyorDirection.BACKWARD)
        delay(duration)  # Attendre la durée spécifiée
        robot.stop_conveyor(conveyor_id)
    except Exception as e:
        print(f"Erreur lors de l'activation du convoyeur: {e}")

def pick_and_place(robot, color, positions, color_counters):
    try:
        # Normaliser le nom de la couleur en minuscules
        color = color.lower()
        
        # Récupérer toutes les positions nécessaires depuis le paramètre positions
        pickup_position = positions.get(f"pick_{color}")
        place_position = positions.get(f"place_{color}_table")
        intermediate_position = positions.get("intermediate_pick")
        intermediate_place_position = positions.get(f"intermediate_place_table_{color}")
        pick_table_position = positions.get(f"pick_{color}_table")
        intermediate_convoyeur_position = positions.get("intermediate_place_convoyeur")
        place_convoyeur_position = positions.get("place_convoyeur")
        
        if not all([pickup_position, place_position, intermediate_position, intermediate_place_position, 
                   pick_table_position, intermediate_convoyeur_position, place_convoyeur_position]):
            print(f"Positions manquantes pour la couleur {color}")
            print("Positions trouvées:")
            print(f"pickup_position: {pickup_position is not None}")
            print(f"place_position: {place_position is not None}")
            print(f"intermediate_position: {intermediate_position is not None}")
            print(f"intermediate_place_position: {intermediate_place_position is not None}")
            print(f"pick_table_position: {pick_table_position is not None}")
            print(f"intermediate_convoyeur_position: {intermediate_convoyeur_position is not None}")
            print(f"place_convoyeur_position: {place_convoyeur_position is not None}")
            return False

        # Changer la couleur de l'anneau LED
        led_color = get_led_color(color)
        print(f"Configuration de l'anneau LED pour la couleur: {color}")  # Debug
        robot.led_ring_solid(led_color)
        delay(0.1)  # Petit délai pour s'assurer que la LED change

        # Si une pièce de cette couleur est déjà sur la table, la déplacer vers le convoyeur
        if color_counters[color] > 0:
            print(f"Déplacement de la pièce {color} déjà sur la table vers le convoyeur...")
            robot.move_pose(intermediate_position)
            robot.move_pose(pick_table_position)
            robot.pull_air_vacuum_pump()
            delay(0.15)
            robot.move_pose(intermediate_position)
            robot.move_pose(intermediate_convoyeur_position)
            robot.move_pose(place_convoyeur_position)
            robot.push_air_vacuum_pump()
            delay(0.15)
            # Activer le convoyeur après avoir déposé la pièce
            activate_conveyor(robot)
            robot.move_pose(intermediate_convoyeur_position)
            robot.move_pose(intermediate_position)
            color_counters[color] -= 1

        print("Déplacement vers la position intermédiaire pick...")
        robot.move_pose(intermediate_position)
            
        print("Déplacement vers la position de prise...")
        robot.move_pose(pickup_position)
        robot.pull_air_vacuum_pump()
        delay(0.15)
        
        print("Déplacement vers la position intermédiaire générale...")
        robot.move_pose(intermediate_position)
        
        print(f"Déplacement vers la position intermédiaire de pose {color}...")
        robot.move_pose(intermediate_place_position)
        
        print("Déplacement vers la position de pose...")
        robot.move_pose(place_position)
        robot.push_air_vacuum_pump()
        delay(0.15)

        print("Déplacement vers la position intermédiaire pick...")
        robot.move_pose(intermediate_position)
        
        # Incrémenter le compteur
        color_counters[color] += 1
        return True
        
    except Exception as e:
        print(f"Erreur lors du pick and place: {e}")
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
        
        # Initialiser les compteurs de couleurs
        color_counters = {"rouge": 0, "vert": 0, "bleu": 0}
        
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
            delay(0.15)  # Attendre la stabilisation
            
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
                delay(0.15)
                continue
            
            no_token_count = 0  # Réinitialiser le compteur si un jeton est trouvé
            print(f"Jeton {color} détecté à la position {position}")
            
            # Définir la couleur de l'anneau LED avant le pick and place
            led_color = get_led_color(color)
            robot.led_ring_solid(led_color)
            
            # Exécuter la séquence pick and place
            if pick_and_place(robot, color, positions, color_counters):
                print(f"Jeton {color} trié avec succès")
                # Remettre l'anneau LED en mode alternatif après succès
                robot.led_ring_alternate(color_list)
            else:
                print(f"Échec du tri du jeton {color}")
                # Remettre l'anneau LED en mode alternatif après échec
                robot.led_ring_alternate(color_list)
            
            delay(0.15)  # Pause entre chaque cycle
            
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
    #save_token_colors()
    #save_all_positions(robot)
    main()
    delay(3)
    robot.close_connection()