# Projet "robotique" IA&Jeux 2021
#
# Binome:
#  Prénom Nom: Enzo PINHO FERNANDES
#  Prénom Nom: Maximilien Piron-Palliser

import random
import math

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
    
    
def step(robotId, sensors):
    sensors = get_extended_sensors(sensors)


    if testDetectionRobotFront(sensors) :
        # Si un robot adverse est devant nous, et qu'on est un robot assigné, on le suit. Sinon on l'évite.
        if not isSameTeamFront(sensors) : 
            if robotId%5 == 0 :
                translation, rotation = aller_vers_les_robots(sensors) 
            else :
                translation, rotation = eviter_les_robots_adverse(sensors)

        # Si un robot allié est devant nous, on tourne vers la droite.
        else :
            translation, rotation = eviter_les_robots_ally(sensors)

    # Si on détecte un mur, on l'évite.
    elif testDetectionWallFront(sensors) :
        translation, rotation = suivre_les_murs(sensors)

    # Si un robot adverse nous suit derrière, on s'arrête.
    elif testDetectionStalker(sensors) and not isSameTeamBack(sensors) :
        translation, rotation = stopStalker(sensors)

    # On continue au hasard.
    else :
        translation, rotation = avancer_no_opti(robotId)
        

    # limite les valeurs de sortie entre -1 et +1
    translation = max(-1,min(translation,1))
    rotation = max(-1, min(rotation, 1))
    
    return translation, rotation
    
# ==============================================================================================================
    
def testDetectionWallFront(sensors) :
    return sensors["sensor_front"]["distance_to_wall"] * sensors["sensor_front_left"]["distance_to_wall"] * sensors["sensor_front_right"]["distance_to_wall"] < 0.5
    
def testDetectionRobotFront(sensors) :
    return sensors["sensor_front"]["distance_to_robot"] * sensors["sensor_front_left"]["distance_to_robot"] * sensors["sensor_front_right"]["distance_to_robot"] < 1

def testDetectionStalker(sensors) :
    return sensors["sensor_back"]["distance_to_robot"] * sensors["sensor_back_left"]["distance_to_robot"] * sensors["sensor_back_right"]["distance_to_robot"] < 0.8

# ==============================================================================================================

def isSameTeamFront(sensors) :
    return sensors["sensor_front"]["isSameTeam"] or sensors["sensor_front_left"]["isSameTeam"] or sensors["sensor_front_right"]["isSameTeam"]

def isSameTeamBack(sensors) :
    return sensors["sensor_back"]["isSameTeam"] or sensors["sensor_back_left"]["isSameTeam"] or sensors["sensor_back_right"]["isSameTeam"]

# ==============================================================================================================
# Braitenberg

def avancer_no_opti(sensors) :
    translation = 1
    rotation = random.uniform(-0.20, 0.20)
    return translation, rotation

def eviter_les_murs(sensors) :
    translation = 1 * sensors["sensor_front"]["distance_to_wall"]
    rotation = (3) * sensors["sensor_front_right"]["distance_to_wall"] + (-2) * sensors["sensor_front_left"]["distance_to_wall"] + (-1) * sensors["sensor_front"]["distance_to_wall"]
    return translation, rotation
    
def aller_vers_les_robots(sensors) :
    translation = 1
    rotation = (-1) * sensors["sensor_front_right"]["distance_to_robot"] + (1) * sensors["sensor_front_left"]["distance_to_robot"]
    return translation, rotation

def eviter_les_robots_ally(sensors) :
    translation = 1 * sensors["sensor_front"]["distance_to_robot"]
    rotation = 1
    return translation, rotation

def eviter_les_robots_adverse(sensors) :
    translation = 1 * sensors["sensor_front"]["distance_to_robot"]
    rotation = (3) * sensors["sensor_front_right"]["distance_to_robot"] + (-2) * sensors["sensor_front_left"]["distance_to_robot"] + (-1) * sensors["sensor_front"]["distance_to_wall"]
    return translation, rotation

def stopStalker(sensors) :
    translation = (0.1) * sensors["sensor_back"]["distance_to_robot"] + (0.1) * sensors["sensor_back_left"]["distance_to_robot"] + (0.1) * sensors["sensor_back_right"]["distance_to_robot"]
    rotation = 0
    return translation, rotation

# ==============================================================================================================
# Mécanisme pour suivre les murs