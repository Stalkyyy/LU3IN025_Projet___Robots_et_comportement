# Projet "robotique" IA&Jeux 2021
#
# Binome: 
#  Prénom Nom: Enzo PINHO FERNANDES 
#  Prénom Nom: Maximilien Piron-Palliser
#
# Groupe 4 === 2023-2024

import random

def get_team_name():
    return "SILKSONG PITY" # à compléter (comme vous voulez)
    
def get_extended_sensors(sensors):
    for key in sensors:
        sensors[key]["distance_to_robot"] = 1.0
        sensors[key]["distance_to_wall"] = 1.0
        if sensors[key]["isRobot"] == True:
            sensors[key]["distance_to_robot"] = sensors[key]["distance"]
        else:
            sensors[key]["distance_to_wall"] = sensors[key]["distance"]
    return sensors
    


# "la mémoire autorisée d'un step à l'autre limité **un seul et unique entier** par robot."
#   -> Les robots pairs garde en mémoire leur sens de suivi de murs. Un nombre positif représente la droite, un nombre négatif la gauche. Le sens est réinialisé quand il tombe à 0.
#   -> Les robots impairs garde en mémoire leur itération. Cela permet d'activer ou de désactiver le suivi de murs.
follow_mode_and_iter : list[int] = [0,0,0,100,0,200,0,300]


# Architecture de subsomption :
#   avancer -> suivre murs -> stop Stalker -> aller vers/eviter les robots ennemis/alliés
def step(robotId, sensors):
    global follow_mode_and_iter
    sensors = get_extended_sensors(sensors)

    if testDetectionRobotFront(sensors) :
        # Si un robot adverse est devant nous, on le suit.
        if not isSameTeamFront(sensors) : 
            translation, rotation = aller_vers_les_robots(sensors) 

        # Si un robot allié est devant nous, on tourne vers la droite.
        else :
            translation, rotation = eviter_les_robots_ally(sensors)


    # Si un robot adverse nous suit derrière, on essaye de s'en débarasser.
    elif testDetectionStalker(sensors) and not isSameTeamBack(sensors) :
        translation, rotation = stopStalker(sensors)

    
    elif (testFollowMurs(robotId)) :
        # Si un robot détecte un mur à sa gauche et à sa droite, il en choisira un à suivre. Les robots impairs prendront par défaut à gauche.
        if (sensors["sensor_right"]["distance_to_wall"] < 1 and sensors["sensor_left"]["distance_to_wall"] < 1) :
            if (follow_mode_and_iter[int(robotId)] == 0) :
                changeModFollow(robotId, random.choice([-4,4]))
            
            if (follow_mode_and_iter[int(robotId)] <= 0) :
                translation, rotation = suivre_murs_droite(sensors)
            else :
                translation, rotation = suivre_murs_gauche(sensors)

        # Si un robot détecte un mur à sa droite, il le suivra.
        elif sensors["sensor_right"]["distance_to_wall"] < 1:
            changeModFollow(robotId, 4)
            translation, rotation = suivre_murs_droite(sensors)
        
        # Si un robot détecte un mur à sa gauche, il le suivra.               
        else :
            changeModFollow(robotId, -4)
            translation, rotation = suivre_murs_gauche(sensors)


    # Si on détecte un mur et qu'on ne le suit pas, on l'évite.
    elif testDetectionWallFront(sensors) :
        translation, rotation = eviter_les_murs(sensors)


    # On continue d'avancer.
    else :
        translation, rotation = avancer(sensors)
        
    
    # Changement d'état du robot.
    changeModFollow(robotId)    
    
    # limite les valeurs de sortie entre -1 et +1
    translation = max(-1,min(translation,1))
    rotation = max(-1, min(rotation, 1))
    
    return translation, rotation
    
    
    
    
# ==============================================================================================================
# Tests de détection
    
def testDetectionWallFront(sensors) :
    return sensors["sensor_front"]["distance_to_wall"] * sensors["sensor_front_left"]["distance_to_wall"] * sensors["sensor_front_right"]["distance_to_wall"] < 0.8
    
def testDetectionRobotFront(sensors) :
    return sensors["sensor_front"]["distance_to_robot"] * sensors["sensor_front_left"]["distance_to_robot"] * sensors["sensor_front_right"]["distance_to_robot"] < 1

def testDetectionStalker(sensors) :
    return sensors["sensor_back"]["distance_to_robot"] * sensors["sensor_back_left"]["distance_to_robot"] * sensors["sensor_back_right"]["distance_to_robot"] < 0.8

# ==============================================================================================================
# Vérification équipiers/ennemies

def isSameTeamFront(sensors) :
    return sensors["sensor_front"]["isSameTeam"] or sensors["sensor_front_left"]["isSameTeam"] or sensors["sensor_front_right"]["isSameTeam"]

def isSameTeamBack(sensors) :
    return sensors["sensor_back"]["isSameTeam"] or sensors["sensor_back_left"]["isSameTeam"] or sensors["sensor_back_right"]["isSameTeam"]
    
# ==============================================================================================================
# Braitenberg

def avancer(sensors) :
    global follow_mode_and_iter
    
    translation = 1 * sensors["sensor_front"]["distance"]
    rotation = random.uniform(-0.25, 0.25)
    print(rotation)
    return translation, rotation


def eviter_les_murs(sensors) :
    translation = 1 * sensors["sensor_front"]["distance_to_wall"]
    rotation = (random.uniform(1,5)) * sensors["sensor_front_right"]["distance_to_wall"] + (random.uniform(-5,-1)) * sensors["sensor_front_left"]["distance_to_wall"]
    return translation, rotation
    
    
def aller_vers_les_robots(sensors) :
    translation = 1
    rotation = (-1) * sensors["sensor_front_right"]["distance_to_robot"] + (1) * sensors["sensor_front_left"]["distance_to_robot"]
    return translation, rotation


def eviter_les_robots_ally(sensors) :
    translation = 1 * sensors["sensor_front"]["distance_to_robot"]
    rotation = (-2) + (-1) * sensors["sensor_front"]["distance_to_robot"] + (2) * sensors["sensor_front_right"]["distance_to_robot"] + (-1) * sensors["sensor_front_left"]["distance_to_robot"]
    return translation, rotation


def stopStalker(sensors) :
    translation = 1
    rotation = (-2) + (-1) * sensors["sensor_back"]["distance_to_robot"] + (2) * sensors["sensor_back_right"]["distance_to_robot"] + (-1) * sensors["sensor_back_left"]["distance_to_robot"]
    return translation, rotation

#==============================================================================================================
# Système de suivi de murs

def testFollowMurs(robotId : float) :
    global follow_mode_and_iter
    return (robotId % 2 == 0 and random.choice([True, False])) or (robotId % 2 == 1 and follow_mode_and_iter[int(robotId)] % 400 < 300)

def suivre_murs_droite(sensors) :
    translation = 1
    rotation = 0
    
    # Si aucun mur avant ou avant droit ne nous bloque, on continue.
    if (sensors["sensor_front"]["distance_to_wall"] * sensors["sensor_right"]["distance_to_wall"] == 1) :
        translation = 1
        rotation = 0
       
    # Si un mur avant ou avant droit est détecté, on tourne le plus possible à gauche. Cela permettra d'être à sa droite et donc de le suivre. 
    elif (sensors["sensor_front"]["distance_to_wall"] < 1 or sensors["sensor_front_right"]["distance_to_wall"] < 1) :
        translation = 1 * sensors["sensor_front"]["distance_to_wall"] * sensors["sensor_front_right"]["distance_to_wall"]
        rotation = -1
    
    # Cela permet de suivre un mur à sa droite.
    elif (sensors["sensor_front"]["distance_to_wall"] == 1) :
        if (sensors["sensor_right"]["distance_to_robot"] < 0.2) :
            rotation = -0.2
        elif (sensors["sensor_right"]["distance_to_robot"] > 0.8) :
            rotation = 0.2
            
    return translation, rotation


def suivre_murs_gauche(sensors) :
    translation = 1
    rotation = 0
    
    # Si aucun mur avant ou avant gauche ne nous bloque, on continue.
    if (sensors["sensor_front"]["distance_to_wall"] * sensors["sensor_left"]["distance_to_wall"] == 1) :
        translation = 1
        rotation = 0
        
    # Si un mur avant ou avant gauche est détecté, on tourne le plus possible à droite. Cela permettra d'être à sa gauche et donc de le suivre. 
    elif (sensors["sensor_front"]["distance_to_wall"] < 1 or sensors["sensor_front_left"]["distance_to_wall"] < 1) :
        translation = 1 * sensors["sensor_front"]["distance_to_wall"] * sensors["sensor_front_left"]["distance_to_wall"]
        rotation = 1
    
    # Cela permet de suivre un mur à sa gauche.
    elif (sensors["sensor_front"]["distance_to_wall"] == 1) :
        if (sensors["sensor_left"]["distance_to_robot"] < 0.2) :
            rotation = +0.2
        elif (sensors["sensor_left"]["distance_to_robot"] > 0.8) :
            rotation = -0.2
            
    return translation, rotation

# ==============================================================================================================
# Changements d'états

def changeModFollow(robotId : float, init : int | None = None) :
    global follow_mode_and_iter
    
    # Si le robot est pair
    if (int(robotId) % 2 == 0) :
        # On initialise sa nouvelle valeur de suivi
        if (init != None) :
            follow_mode_and_iter[int(robotId)] = init
            
        # On incrémente ou décrémente sa valeur de suivi pour s'approcher du stade de réinitialisation.
        elif (follow_mode_and_iter[int(robotId)] != 0) :
            follow_mode_and_iter[int(robotId)] += 1 if follow_mode_and_iter[int(robotId)] < 0 else 1
            
    # Si le robot est impair, on incrémente son itération.
    else :
        follow_mode_and_iter[int(robotId)] += 1