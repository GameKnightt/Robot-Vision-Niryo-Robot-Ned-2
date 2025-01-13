# Projet Robot Vision

Ce projet met en œuvre un robot Niryo pour détecter, trier et déplacer des jetons en fonction de leur couleur.  
Il comprend plusieurs fonctions pour configurer le robot, détecter la couleur d'un objet et exécuter le mouvement d'un convoyeur.

## Fonctionnalités principales

- Détection de jetons à l'aide d'une caméra réseau (get_camera_image, detect_token).  
- Configuration du TCP pour la ventouse (define_tcp).  
- Gestion et enregistrement des positions du robot (save_all_positions).  
- Système de pick and place pour trier les jetons selon leur couleur (pick_and_place).  
- Contrôle du convoyeur pour déplacer ou retirer les pièces (activate_conveyor). 

## Prérequis

1. Python v3.10 minimum installé.  
2. Bibliothèques Python requises :  
   - requests  
   - numpy  
   - opencv-python  
   - pyniryo (v1.1.2)
   - json (intégré par défaut dans Python)  
3. Robot Niryo configuré et connecté sur le même réseau.  
4. Caméra réseau accessible pour la capture d'images (adresse IP configurée dans le code).  

## Installation

1. Clonez ou téléchargez ce dépôt sur votre machine.  
2. Créez et activez un environnement virtuel :
   ```bash
   python -m venv robot_venv
   source robot_venv/bin/activate  # Sur Windows, utilisez `robot_venv\Scripts\activate`
   ```
3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
4. Éditez les adresses IP si nécessaire (robot_ip et URL de la caméra).

## Usage

1. Assurez-vous que le robot et la caméra sont opérationnels.  
2. Lancez le script main.py :  
   ```bash
   python main.py
   ```
3. Suivez les instructions affichées :  
   - Définissez ou chargez les positions pré-enregistrées.  
   - Lancez la détection colorimétrique et le tri automatique des jetons.  
   - Ajustez les couleurs et les positions selon le besoin via les menus interactifs.

## Licence MIT

Ce projet est fourni à titre d’exemple et peut être adapté librement en fonction de vos besoins.
