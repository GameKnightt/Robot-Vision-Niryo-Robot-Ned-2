Je souhaite que lorsque on lance le programme donc le main() s'exécute et affiche en menu dans le terminal et que l'utilisateur puisse utiliser, naviguer, comprendre et intéragir avec ce menu de façon simple et intuitive. Je souhaite donc que au démarage on affiche un menu avec plusieurs options disponible : 

1. Lancement de la séquence : affiche la liste des séquence enregistrée et les lance en entrant le numéro associé.
2. Création de séquence : Cette fonctionnalité permet de créer une nouvelle séquence adaptée aux besoins de l'utilisateur. Au début du processus, plusieurs choix sont proposés pour configurer la séquence : type d'outil utilisé (pince ou ventouse), utilisation ou non d'un convoyeur, activation ou non de l'analyse de couleurs, etc. En fonction des choix effectués, la création de la séquence est personnalisée. Chaque séquence créée génère automatiquement un fichier JSON, sauvegardé dans un dossier spécifique nommé "sequences". Ce fichier porte le nom de la séquence et contient toutes les positions enregistrées associées à celle-ci.

- Étapes de création de la séquence :

Nom et configuration initiale :
L'utilisateur définit le nom de la séquence, puis choisit les paramètres spécifiques, comme l'utilisation de la pince, du convoyeur ou de l'analyse de couleurs. Ces choix influencent les questions et options proposées lors de la création.

Enregistrement des positions :
À chaque enregistrement de position, les étapes suivantes sont suivies :

L'utilisateur donne un nom à la position.
Il positionne l'outil ou le dispositif selon les besoins pour enregistrer la position.
Après l'enregistrement, une action est spécifiée : prendre, poser, activer le convoyeur, ou ne rien faire. Cette action est associée à la position enregistrée.
Le processus se répète jusqu'à ce que toutes les positions nécessaires soient enregistrées.

- Analyse des couleurs (si activée) :
Lorsque l'analyse des couleurs est requise, des questions supplémentaires sont posées, comme :

La séquence doit-elle capturer une image via la caméra ?
Quelle est la couleur de la pièce à analyser ?
Par exemple, si l'on souhaite trier des pièces par couleur, chaque position doit être nommée de manière explicite et distincte pour éviter les conflits entre les positions des différentes couleurs. Lorsqu’une pièce d’une couleur spécifique est déplacée, l'utilisateur doit indiquer si la position de dépose/prise doit être :

Générale (utilisable pour toutes les couleurs).
Spécifique (associée uniquement à une couleur particulière, ce qui nécessite de veiller aux conflits entre positions).
Validation et récapitulatif :
Une fois toutes les positions enregistrées, un récapitulatif complet de la séquence est affiché. Ce récapitulatif permet de vérifier qu’aucune erreur n’a été commise. Après validation, la séquence peut être exécutée directement, sans nécessiter d'ajouts manuels pour définir les mouvements ou les actions (prise, dépose, activation du convoyeur, capture d’image, analyse, etc.).

3. Modification de séquence : liste les séquence créer et propose des choix de modification
4. Calibration des couleurs
5. Quitter

Si l'analyse de couleur est sélectionné il faudrait demandé si il faut recadré la zone ou pas en utilisant la fonction save_crop_zone() et aussi quand la zone de couleur est sélectionné lors de l'exécution de la séquence l'anneau du robot doit s'allumer de la couleur de la pièce détecter. Si l'utilisation du convoyeur est sélectionné lors de l'exécution de la séquence il faut utiliser la fonction activate_conveyor(). Il faut rajouter dans la fonction execute_sequence() que si c'est la pince qui est choisi, pour prendre l'action est : robot.close_gripper et pour poser : robot.open_gripper