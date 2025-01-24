import json
import requests
import numpy as np
import cv2
import os
from pyniryo import*                                                           
from time import sleep as delay

robot_ip = "172.21.182.56"  # Remplacez par l'IP de votre robot
robot = NiryoRobot(robot_ip)
robot.set_arm_max_velocity(100)  # Set robot speed to 200%
conveyor_id = robot.set_conveyor()

color_list = [
    [15, 50, 255],
    [255, 0, 0],
    [0, 255, 0],
]

# Configure et active le TCP (Tool Center Point) du robot pour utiliser la ventouse
# Définit les coordonnées précises de l'outil par rapport à la bride du robot
def define_tcp(tool_type="2"):  # Par défaut ventouse (2)
    """Configure et active le TCP en fonction de l'outil"""
    # Définition des TCPs pour chaque outil
    # Values in meters [x, y, z, roll, pitch, yaw]
    VACUUM_TCP = [0.05, 0, 0, 0, 0, 0]  # TCP pour la ventouse
    GRIPPER_TCP = [0.085, 0, 0, 0, 0, 0]  # TCP pour la pince

    # Sélection du TCP en fonction de l'outil
    selected_tcp = VACUUM_TCP if tool_type == "2" else GRIPPER_TCP
    tool_name = "Ventouse" if tool_type == "2" else "Pince"

    # Configuration du TCP
    robot.reset_tcp()
    print('TCP Reset')
    robot.set_tcp(selected_tcp)
    print(f'TCP Set pour {tool_name}')
    robot.enable_tcp(True)
    print('TCP Activé')

# Permet à l'utilisateur de déplacer le robot vers des positions pré-enregistrées
# Affiche un menu interactif pour sélectionner et confirmer les mouvements
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

# Interface pour gérer les positions du robot
# Permet d'ajouter, modifier, supprimer et sauvegarder des positions dans un fichier JSON
def save_all_positions(robot):
    # Charger les positions existantes
    try:
        with open('positions.json', 'r') as f:
            positions = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        positions = {}

    while True:
        # Afficher simplement la liste numérotée des positions
        print("\n=== Positions enregistrées ===")
        for i, name in enumerate(positions.keys(), 1):
            print(f"{i}. {name}")
        
        print("\nOptions:")
        print("1. Ajouter/Modifier des positions")
        print("2. Supprimer une position")
        print("3. Terminer")
        
        choice = input("\nChoisissez une option (1-3): ")
        
        if choice == "1":
            # Sous-menu de modification
            while True:
                print("\n=== Mode Modification ===")
                for i, name in enumerate(positions.keys(), 1):
                    print(f"{i}. {name}")
                print("0. Retour au menu principal")
                
                pos_choice = input("\nEntrez le numéro de la position à modifier (0 pour retour, n pour nouvelle): ").lower()
                
                if pos_choice == '0':
                    break
                elif pos_choice == 'n':
                    name = input("Nom de la nouvelle position: ").strip()
                else:
                    try:
                        idx = int(pos_choice) - 1
                        if 0 <= idx < len(positions):
                            name = list(positions.keys())[idx]
                        else:
                            print("Numéro invalide")
                            continue
                    except ValueError:
                        print("Entrée invalide")
                        continue

                if name:
                    # Si c'est une position existante, montrer sa valeur actuelle
                    if name in positions:
                        print(f"\nPosition actuelle '{name}':")
                        current_pose = positions[name]
                        print(f"X: {current_pose[0]:.2f}, Y: {current_pose[1]:.2f}, Z: {current_pose[2]:.2f}")
                        print(f"RX: {current_pose[3]:.2f}, RY: {current_pose[4]:.2f}, RZ: {current_pose[5]:.2f}")
                        try:
                            robot.move_pose(positions[name])
                            confirm = input("Voulez-vous modifier cette position ? (o/n): ").lower()
                            if confirm != 'o':
                                continue
                        except Exception as e:
                            print(f"Erreur lors du déplacement: {e}")
                            continue

                    input(f"Déplacez le robot à la position '{name}' puis appuyez sur Enter...")
                    current_pose = robot.get_pose().to_list()
                    positions[name] = current_pose
                    print(f"Position '{name}' enregistrée")
                
        elif choice == "2":
            if not positions:
                print("Aucune position à supprimer")
                continue
                
            try:
                idx = int(input("\nEntrez le numéro de la position à supprimer (0 pour annuler): "))
                if idx > 0 and idx <= len(positions):
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

# Capture une image depuis la caméra réseau
# Retourne l'image au format OpenCV ou None en cas d'erreur
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

# Interface pour enregistrer et gérer les couleurs des jetons
# Permet de sélectionner des zones sur l'image et de sauvegarder leurs valeurs RGB
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

# Définit la zone de détection des jetons sur l'image de la caméra
# Permet de sélectionner visuellement la zone et sauvegarde ses coordonnées
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

# Analyse l'image pour détecter et identifier la couleur d'un jeton
# Compare la couleur moyenne de la zone avec les couleurs enregistrées
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

# Convertit le nom d'une couleur en valeurs RGB pour l'anneau LED du robot
# Gère différentes variantes de noms de couleurs (français/anglais)
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

# Contrôle le convoyeur pour évacuer les jetons
# Active le convoyeur pendant une durée spécifiée puis l'arrête
def activate_conveyor(robot, duration=5):
    """Active le convoyeur pendant une durée spécifiée"""
    try:
        robot.run_conveyor(conveyor_id, speed=50, direction=ConveyorDirection.BACKWARD)
        delay(duration)  # Attendre la durée spécifiée
        robot.stop_conveyor(conveyor_id)
    except Exception as e:
        print(f"Erreur lors de l'activation du convoyeur: {e}")

def create_sequence():
    """Création d'une nouvelle séquence de mouvements"""
    # Définir le chemin absolu pour le dossier sequences
    base_path = "/var/home/E222668F/reseau/Perso/BUT_GEII_3/Robot_JPO/Robot-Vision-Niryo-Robot-Ned-2"
    sequences_dir = f"{base_path}/sequences"

    sequence_name = input("Nom de la séquence: ").strip()
    if not sequence_name:
        print("Nom de séquence invalide")
        return
    
    # Configuration initiale
    config = {
        "name": sequence_name,
        "tool_type": input("Type d'outil (1: Pince, 2: Ventouse): ").strip(),
        "use_conveyor": input("Utiliser le convoyeur ? (o/n): ").lower() == 'o',
        "analyze_colors": input("Analyser les couleurs ? (o/n): ").lower() == 'o',
        "positions": []
    }
    
    # Initialise l'outil
    if config["tool_type"] == "1":  # Pince
        robot.open_gripper()
        print("Pince initialisée (ouverte)")
    else:  # Ventouse
        robot.push_air_vacuum_pump()
        print("Ventouse initialisée (air expulsé)")
    
    # Si analyse des couleurs activée, demander pour le recadrage
    if config["analyze_colors"]:
        if input("Voulez-vous recadrer la zone de détection ? (o/n): ").lower() == 'o':
            crop_params = save_crop_zone()
            if crop_params:
                config["crop_params"] = crop_params
        else:
            try:
                with open('crop_params.json', 'r') as f:
                    config["crop_params"] = json.load(f)
            except FileNotFoundError:
                print("Aucune zone de prise définie. Définition nécessaire.")
                crop_params = save_crop_zone()
                if crop_params:
                    config["crop_params"] = crop_params
    
    # Enregistrement des positions
    while True:
        print("\n=== Ajout de position ===")
        print("1. Ajouter une position")
        print("0. Terminer")
        
        if input("Choix: ") != "1":
            break
            
        name = input("Nom de la position: ").strip()
        print("\nDéplacez maintenant le robot à la position souhaitée")
        input("Appuyez sur Enter une fois le robot positionné...")
        
        position = {
            "name": name,
            "coordinates": robot.get_pose().to_list(),
            "action": input("Action à effectuer à cette position (prendre/poser/conveyor/rien): ").lower()
        }
        
        # Ajouter la durée si l'action est conveyor
        if position["action"] == "conveyor":
            try:
                duration = float(input("Durée d'activation du convoyeur (en secondes): "))
                if duration > 0:
                    position["conveyor_duration"] = duration
                else:
                    position["conveyor_duration"] = 5  # Durée par défaut
                    print("Durée invalide, utilisation de la durée par défaut (5 secondes)")
            except ValueError:
                position["conveyor_duration"] = 5  # Durée par défaut
                print("Durée invalide, utilisation de la durée par défaut (5 secondes)")
        
        if config["analyze_colors"] and position["action"] in ["prendre", "poser"]:
            position["color_specific"] = input("Position spécifique à une couleur ? (o/n): ").lower() == 'o'
            if position["color_specific"]:
                position["color"] = input("Couleur associée (rouge/vert/bleu): ").lower()
        
        config["positions"].append(position)
        print(f"Position {position['name']} enregistrée")
    
    # Sauvegarder la séquence avec le chemin absolu
    import os
    if not os.path.exists(sequences_dir):
        try:
            os.makedirs(sequences_dir)
            print(f"Création du dossier sequences: {sequences_dir}")
        except Exception as e:
            print(f"Erreur lors de la création du dossier: {e}")
            return
    
    sequence_path = os.path.join(sequences_dir, f"{sequence_name}.json")
    try:
        with open(sequence_path, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"\nSéquence sauvegardée dans: {sequence_path}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la séquence: {e}")

def list_sequences():
    """Liste toutes les séquences disponibles"""
    base_path = "/var/home/E222668F/reseau/Perso/BUT_GEII_3/Robot_JPO/Robot-Vision-Niryo-Robot-Ned-2"
    sequences_dir = f"{base_path}/sequences"
    
    sequences = []
    if os.path.exists(sequences_dir):
        sequences = [f for f in os.listdir(sequences_dir) if f.endswith('.json')]
    return sequences

def load_sequence(sequence_name):
    """Charge une séquence depuis un fichier"""
    try:
        base_path = "/var/home/E222668F/reseau/Perso/BUT_GEII_3/Robot_JPO/Robot-Vision-Niryo-Robot-Ned-2"
        sequence_path = os.path.join(base_path, "sequences", sequence_name)
        with open(sequence_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement de la séquence: {e}")
        return None

def execute_sequence(sequence_config, loop_mode=False):
    """Exécute une séquence chargée"""
    try:
        print(f"Exécution de la séquence: {sequence_config['name']}")
        print(f"Mode boucle: {'Activé' if loop_mode else 'Désactivé'}")
        
        while True:  # Boucle principale pour le mode répétition
            # Configure le TCP pour l'outil de la séquence
            define_tcp(sequence_config["tool_type"])
            
            # Initialise l'outil
            if sequence_config["tool_type"] == "1":  # Pince
                robot.open_gripper()
                print("Pince initialisée (ouverte)")
            else:  # Ventouse
                robot.push_air_vacuum_pump()
                print("Ventouse initialisée (air expulsé)")
            
            # Charger les couleurs si nécessaire
            colors = None
            if sequence_config["analyze_colors"]:
                try:
                    with open('couleurs.json', 'r') as f:
                        colors = json.load(f)
                except FileNotFoundError:
                    print("Fichier de couleurs non trouvé")
                    return False
            
            for position in sequence_config["positions"]:
                print(f"\nDéplacement vers: {position['name']}")
                robot.move_pose(position["coordinates"])
                
                if position["action"] == "prendre":
                    if sequence_config["tool_type"] == "1":  # Pince
                        robot.close_gripper()
                    else:  # Ventouse
                        robot.pull_air_vacuum_pump()
                elif position["action"] == "poser":
                    if sequence_config["tool_type"] == "1":  # Pince
                        robot.open_gripper()
                    else:  # Ventouse
                        robot.push_air_vacuum_pump()
                elif position["action"] == "conveyor" and sequence_config["use_conveyor"]:
                    duration = position.get("conveyor_duration", 5)  # Utilise 5 secondes par défaut si non spécifié
                    print(f"Activation du convoyeur pour {duration} secondes...")
                    activate_conveyor(robot, duration)
                
                if sequence_config["analyze_colors"] and colors:
                    img = get_camera_image()
                    if img is not None and position.get("color_specific"):
                        color, _ = detect_token(img, colors, sequence_config["crop_params"])
                        if color:
                            print(f"Couleur détectée: {color}")
                            # Allumer l'anneau LED avec la couleur détectée
                            led_color = get_led_color(color)
                            robot.led_ring_solid(led_color)
                
                delay(0.15)
            
            print("Séquence terminée")
            
            if not loop_mode:
                break
            else:
                # Suppression de la pause entre les cycles
                print("\nDémarrage du prochain cycle...")
                # Vérification de l'arrêt d'urgence ou si une touche a été pressée
                if cv2.waitKey(1) & 0xFF == ord('q'):  # Vérifie si 'q' est pressé
                    print("Arrêt de la séquence")
                    break
        
        # Remettre l'anneau LED en mode alternatif à la fin
        robot.led_ring_alternate(color_list)
        print("Séquence terminée")
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'exécution de la séquence: {e}")
        return False

def modify_sequence(sequence_name):
    """Modifie une séquence existante"""
    sequence = load_sequence(sequence_name)
    if not sequence:
        return
    
    base_path = "/var/home/E222668F/reseau/Perso/BUT_GEII_3/Robot_JPO/Robot-Vision-Niryo-Robot-Ned-2"
    sequence_path = os.path.join(base_path, "sequences", sequence_name)
    
    while True:
        print("\n=== Modification de séquence ===")
        print(f"Séquence: {sequence['name']}")
        print("1. Ajouter une position")
        print("2. Supprimer une position")
        print("3. Modifier une position existante")
        print("4. Modifier la configuration de la séquence")
        print("0. Sauvegarder et quitter")
        
        choice = input("Choix: ")
        
        if choice == "1":
            # Ajouter une nouvelle position
            name = input("Nom de la position: ").strip()
            print("\nDéplacez maintenant le robot à la position souhaitée")
            input("Appuyez sur Enter une fois le robot positionné...")
            
            position = {
                "name": name,
                "coordinates": robot.get_pose().to_list(),
                "action": input("Action à effectuer (prendre/poser/conveyor/rien): ").lower()
            }
            
            if sequence["analyze_colors"] and position["action"] in ["prendre", "poser"]:
                position["color_specific"] = input("Position spécifique à une couleur ? (o/n): ").lower() == 'o'
                if position["color_specific"]:
                    position["color"] = input("Couleur associée (rouge/vert/bleu): ").lower()
            
            sequence["positions"].append(position)
            print(f"Position {name} ajoutée")

        elif choice == "2":
            # Supprimer une position
            if not sequence["positions"]:
                print("Aucune position à supprimer")
                continue
            
            print("\nPositions disponibles:")
            for i, pos in enumerate(sequence["positions"], 1):
                print(f"{i}. {pos['name']} - Action: {pos['action']}")
            
            try:
                idx = int(input("\nNuméro de la position à supprimer (0 pour annuler): ")) - 1
                if 0 <= idx < len(sequence["positions"]):
                    del sequence["positions"][idx]
                    print("Position supprimée")
            except ValueError:
                print("Sélection invalide")

        elif choice == "3":
            # Modifier une position existante
            if not sequence["positions"]:
                print("Aucune position à modifier")
                continue
            
            print("\nPositions disponibles:")
            for i, pos in enumerate(sequence["positions"], 1):
                print(f"{i}. {pos['name']} - Action: {pos['action']}")
            
            try:
                idx = int(input("\nNuméro de la position à modifier (0 pour annuler): ")) - 1
                if 0 <= idx < len(sequence["positions"]):
                    pos = sequence["positions"][idx]
                    
                    # Déplacer d'abord le robot à la position actuelle
                    print(f"\nDéplacement vers la position: {pos['name']}")
                    try:
                        robot.move_pose(pos["coordinates"])
                        print("Robot en position")
                    except Exception as e:
                        print(f"Erreur lors du déplacement: {e}")
                        continue
                    
                    print(f"\nModification de la position: {pos['name']}")
                    print("1. Modifier la position physique")
                    print("2. Modifier l'action")
                    print("3. Modifier les paramètres de couleur")
                    print("0. Annuler")
                    
                    sub_choice = input("Choix: ")
                    
                    if sub_choice == "1":
                        print("Déplacez le robot à la nouvelle position")
                        input("Appuyez sur Enter une fois le robot positionné...")
                        pos["coordinates"] = robot.get_pose().to_list()
                        print("Position mise à jour")
                    
                    elif sub_choice == "2":
                        pos["action"] = input("Nouvelle action (prendre/poser/conveyor/rien): ").lower()
                        print("Action mise à jour")
                    
                    elif sub_choice == "3":
                        if sequence["analyze_colors"]:
                            pos["color_specific"] = input("Position spécifique à une couleur ? (o/n): ").lower() == 'o'
                            if pos["color_specific"]:
                                pos["color"] = input("Couleur associée (rouge/vert/bleu): ").lower()
                            print("Paramètres de couleur mis à jour")
            except ValueError:
                print("Sélection invalide")

        elif choice == "4":
            # Modifier la configuration générale
            print("\nConfiguration actuelle:")
            print(f"Type d'outil: {sequence['tool_type']}")
            print(f"Utilise le convoyeur: {sequence['use_conveyor']}")
            print(f"Analyse les couleurs: {sequence['analyze_colors']}")
            
            if input("\nModifier la configuration ? (o/n): ").lower() == 'o':
                sequence["tool_type"] = input("Type d'outil (1: Pince, 2: Ventouse): ").strip()
                sequence["use_conveyor"] = input("Utiliser le convoyeur ? (o/n): ").lower() == 'o'
                sequence["analyze_colors"] = input("Analyser les couleurs ? (o/n): ").lower() == 'o'
                
                if sequence["analyze_colors"] and input("Reconfigurer la zone de détection ? (o/n): ").lower() == 'o':
                    crop_params = save_crop_zone()
                    if crop_params:
                        sequence["crop_params"] = crop_params

        elif choice == "0":
            # Sauvegarder et quitter
            try:
                with open(sequence_path, 'w') as f:
                    json.dump(sequence, f, indent=4)
                print("Modifications sauvegardées")
                break
            except Exception as e:
                print(f"Erreur lors de la sauvegarde: {e}")
                if input("Réessayer ? (o/n): ").lower() != 'o':
                    break

def delete_sequence():
    """Supprime une séquence existante"""
    sequences = list_sequences()
    if not sequences:
        print("Aucune séquence à supprimer")
        return
    
    print("\nSéquences disponibles:")
    for i, seq in enumerate(sequences, 1):
        print(f"{i}. {seq}")
    
    try:
        idx = int(input("\nChoisissez une séquence à supprimer (0 pour annuler): ")) - 1
        if 0 <= idx < len(sequences):
            sequence_name = sequences[idx]
            confirm = input(f"Êtes-vous sûr de vouloir supprimer {sequence_name} ? (o/n): ").lower()
            if confirm == 'o':
                base_path = "/var/home/E222668F/reseau/Perso/BUT_GEII_3/Robot_JPO/Robot-Vision-Niryo-Robot-Ned-2"
                sequence_path = os.path.join(base_path, "sequences", sequence_name)
                try:
                    os.remove(sequence_path)
                    print(f"Séquence {sequence_name} supprimée")
                except Exception as e:
                    print(f"Erreur lors de la suppression: {e}")
    except ValueError:
        print("Sélection invalide")

def display_ascii_logos():
    """Affiche le logo ASCII GEII"""
    try:
        base_path = "/var/home/E222668F/reseau/Perso/BUT_GEII_3/Robot_JPO/Robot-Vision-Niryo-Robot-Ned-2/ASCII-Arts"
        # Lecture du fichier ASCII
        with open(f'{base_path}/GEII_Art_ASCII.txt', 'r') as f:
            lines = f.readlines()
            print("\n") # Espace avant le logo
            for line in lines:
                print(line.rstrip())
            print("\n") # Espace après le logo
    except FileNotFoundError:
        print("Fichier ASCII introuvable")
    except Exception as e:
        print(f"Erreur lors de l'affichage du logo: {e}")

def main_menu():
    """Menu principal du programme"""
    while True:
        display_ascii_logos()
        print("\n=== Menu Principal ===")
        print("1. Lancement de séquence")
        print("2. Création de séquence")
        print("3. Modification de séquence")
        print("4. Suppression de séquence")  # Nouvelle option
        print("5. Calibration des couleurs")
        print("6. Quitter")  # Décalage du numéro
        
        choice = input("\nChoisissez une option (1-6): ")  # Mise à jour du range
        
        if choice == "1":
            sequences = list_sequences()
            if not sequences:
                print("Aucune séquence disponible")
                continue
                
            print("\nSéquences disponibles:")
            for i, seq in enumerate(sequences, 1):
                print(f"{i}. {seq}")
            
            try:
                idx = int(input("\nChoisissez une séquence (0 pour annuler): ")) - 1
                if 0 <= idx < len(sequences):
                    sequence = load_sequence(sequences[idx])
                    if sequence:
                        loop_mode = input("Voulez-vous exécuter la séquence en boucle ? (o/n): ").lower() == 'o'
                        execute_sequence(sequence, loop_mode)
            except ValueError:
                print("Sélection invalide")
                
        elif choice == "2":
            create_sequence()
            
        elif choice == "3":
            sequences = list_sequences()
            if not sequences:
                print("Aucune séquence à modifier")
                continue
                
            print("\nSéquences disponibles:")
            for i, seq in enumerate(sequences, 1):
                print(f"{i}. {seq}")
            
            try:
                idx = int(input("\nChoisissez une séquence à modifier (0 pour annuler): ")) - 1
                if 0 <= idx < len(sequences):
                    modify_sequence(sequences[idx])
            except ValueError:
                print("Sélection invalide")
                
        elif choice == "4":  # Nouvelle option
            delete_sequence()
            
        elif choice == "5":  # Décalage des numéros
            save_token_colors()
            
        elif choice == "6":  # Décalage des numéros
            print("Arrêt du programme...")
            break

robot.led_ring_alternate(color_list)
main_menu()
delay(3)
robot.close_connection()