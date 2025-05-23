#!/usr/bin/env python
#@author Foltêto
#@contributors Ybeattie
#@Version 3.0

import argparse
from utilities import argument_check, api_requests, recursive_checker

gares_file = "data/gares.txt"

def train_station_list(prefix, parsed_args, **kwargs):
    '''Imprime à l'écran la liste des gares qui match l'entrée de l'utilisateur'''
    with open(gares_file, "r", encoding="utf-8") as f:
        return (gare.strip() for gare in f.readlines() if gare.startswith(prefix))

def get_args():
    '''Défini les arguments de notre scrapper de train'''
    parser = argparse.ArgumentParser(
    prog="TGVMAXiSchlag",
    description="Find the best TGVmax route for your trip, regardless where you have to stop",
)

    parser.add_argument("-d", "--depart", help="Departure station", required=True)
    
    parser.add_argument("-a", "--arrivee", help="Arrival station", required=True)
    parser.add_argument("-t", "--date", help="Date of the trip", required=True)
    parser.add_argument(
        "-s", "--steps", help="Number of max steps", required=False, default=2
    )
    parser.add_argument(
        "-l",
        "--list-gares",
        help="List all available stations",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "-p",
        "--propale",
        help="List TGVmax trains from your station at your desired date",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "-f",
        "--force",
        help="The algorithm searches for routes with the minimum number of possible steps. This option activates the forcing of the route search up to the specified number of steps.",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "-hh",
        "--hour",
        help="Hour of departure  if you'd like to specify one",
        required=False,
        default="00:00",
    )
    return parser.parse_args()

# Corps
def print_graph():
    '''Imprime à l'écran un joli dessin'''
    print("\n\n")
    print(" /$$$$$$$$ /$$$$$$  /$$    /$$ /$$      /$$  /$$$$$$  /$$   /$$ /$$  /$$$$$$            /$$       /$$")
    print("|__  $$__//$$__  $$| $$   | $$| $$$    /$$$ /$$__  $$| $$  / $$|__/ /$$__  $$          | $$      | $$")
    print("   | $$  | $$  \\__/| $$   | $$| $$$$  /$$$$| $$  \\ $$|  $$/ $$/ /$$| $$  \\__/  /$$$$$$$| $$$$$$$ | $$  /$$$$$$   /$$$$$$")
    print("   | $$  | $$ /$$$$|  $$ / $$/| $$ $$/$$ $$| $$$$$$$$ \\  $$$$/ | $$|  $$$$$$  /$$_____/| $$__  $$| $$ |____  $$ /$$__  $$")
    print("   | $$  | $$|_  $$ \\  $$ $$/ | $$  $$$| $$| $$__  $$  >$$  $$ | $$ \\____  $$| $$      | $$  \\ $$| $$  /$$$$$$$| $$  \\ $$")
    print("   | $$  | $$  \\ $$  \\  $$$/  | $$\\  $ | $$| $$  | $$ /$$/\\  $$| $$ /$$  \\ $$| $$      | $$  | $$| $$ /$$__  $$| $$  | $$")
    print("   | $$  |  $$$$$$/   \\  $/   | $$ \\/  | $$| $$  | $$| $$  \\ $$| $$|  $$$$$$/|  $$$$$$$| $$  | $$| $$|  $$$$$$$|  $$$$$$$")
    print("   |__/   \\______/     \\_/    |__/     |__/|__/  |__/|__/  |__/|__/ \\______/  \\_______/|__/  |__/|__/ \\_______/ \\____  $$")
    print("                                                                                                                /$$  \\ $$")
    print("                                                                                                               |  $$$$$$/")
    print("                                                                                                                \\______/ ")
    return 0

def check_direct_trains(available_trains, depart, arrivee, date):
    '''Check les trains en tgvmax qui sont direct entre les 2 gares'''
    #available_trains = api_requests.simple_request(depart_req, arrivee_req, date, hour)
    if len(available_trains) > 0:
        print(
            "Il existe au moins un trajet direct entre "
            + depart
            + " et "
            + arrivee
            + " le "
            + date
        )
        print("Voici les trains disponibles :")
        for train in available_trains:
            print("Heure de départ : " + train[2] + " Heure d'arrivée : " + train[3])
    else:
        print(
            "Il n'existe pas de trajet direct entre "
            + depart
            + " et "
            + arrivee
            + " le "
            + date
        )
    return available_trains

def check_indirect_trains(all_compatible_journey, steps):
    '''Check les tgvmax disponible entre les deux gares fourni avec des correspondances'''
    print("")
    print("Recherche de trajets avec étapes...")
    print("")

    print("Tentative de trouver des trajets avec ", steps, " étapes...")

    if len(all_compatible_journey) > 0:
        print("\n####################################\n")
        print("Récapitulatif des différents trajets trouvés :")
        for trajet in all_compatible_journey:
            print("Trajet :")
            for i in range(len(trajet)):
                train = trajet[i]
                print("Train ", i + 1)
                print(
                    "Départ de ",
                    train[0],
                    " à ",
                    train[2],
                    " ---> Arrivée à ",
                    train[1],
                    " à ",
                    train[3],
                )
            print("------------------")
    else:
        print("Aucun train trouvé, essayez avec plus d'étapes !")

def parse_trains(available_trains, all_compatible_journey, depart, arrivee):
    parsed_trajets_direct = []
    for trajet in available_trains:
        parsed_trajets_direct.append({
            'depart': depart,
            'heure_depart': trajet[2],
            'arrivee': arrivee,
            'heure_arrivee': trajet[3]
        })

    parsed_trajets_indirect = []
    for trajet in all_compatible_journey:
        parsed_trains = []
        for train in trajet:
            parsed_trains.append({
                'depart': train[0],
                'heure_depart': train[2],
                'arrivee': train[1],
                'heure_arrivee': train[3],
            })
        parsed_trajets_indirect.append(parsed_trains)
    return parsed_trajets_direct, parsed_trajets_indirect

def main(args={}):
    '''Fonction principal récupérant les argument utilisateur avant de checker les trains direct et indirect disponible en tgvmax'''
    if args == {}:
        args = get_args()

    print_graph()
    depart = args.depart
    arrivee = args.arrivee
    date = args.date
    hour = args.hour
    force_maxsteps = args.force
    steps = int(args.steps)

    # import des gares depuis le fichier txt
    with open(gares_file, "r", encoding="utf-8") as f:
        gares = f.readlines()
        gares = [gare.strip() for gare in gares]
        gares.sort()

    if args.list_gares:
        print("Liste des gares disponibles :")
        for gare in gares:
            print(gare)
        exit()

    if args.propale:
        try :
            print("Trains TGVmax disponibles depuis " + depart + " le " + date)
            trains = api_requests.check_available_gares(
                argument_check.formalize_gare(depart), date, hour
            )
            for train in trains:
                print("Vers la gare de " + train[1])
                print("Heure de départ : " + train[2] + " Heure d'arrivée : " + train[3])
            exit()
        except api_requests.SNCFLimitReached as e:
            print('Error raised !')
    # vérification des arguments et formalisation des gares
    argument_check.verify_argument(depart, arrivee, date, steps, gares)
    depart_req = argument_check.formalize_gare(depart)
    arrivee_req = argument_check.formalize_gare(arrivee)
    try : 
        # on commence par vérifier qu'il n'existe pas de trajet direct entre les deux gares
        available_trains = check_direct_trains(api_requests.simple_request(depart_req, arrivee_req, date, hour), depart, arrivee, date)

        
        all_compatible_journey = []
        recursive_checker.gare_checker(
            all_compatible_journey, arrivee, depart, date, [], steps, force_maxsteps, hour
        )
        check_indirect_trains(all_compatible_journey, steps)
        trajet_direct, trajet_indirect = parse_trains(available_trains, all_compatible_journey, depart, arrivee)
    except api_requests.SNCFLimitReached as e:
        print(e)
        raise(api_requests.SNCFLimitReached(e))
    return trajet_direct, trajet_indirect


if __name__=='__main__':
    main(get_args())
