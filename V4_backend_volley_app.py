# -*- coding: utf-8 -*-
#problème de robustesse quand je change le nombre de terrains et d'équipes mais fonctionne sur 12 équipes et 3 terrains ou 4 terrains 
#fonctionne sur 14 équipes en gros les nombres impairs et en dessous de 12 équipes ne fonctionne pas 
import random
import math
from itertools import combinations

class Equipe:
    def __init__(self, nom):
        self.nom = nom
        self.points = 0
        self.points_marques = 0
        self.points_encaisse = 0
        self.matchs_joues = 0
        self.matchs_enregistres = 0

    def ajouter_resultat(self, points_marques, points_encaisse, victoire, compte=True):
        if compte and self.matchs_enregistres < 2:
            self.points_marques += points_marques
            self.points_encaisse += points_encaisse
            self.points += 3 if victoire else 1
            self.matchs_joues += 1
            self.matchs_enregistres += 1

    def ajouter_resultat_force(self, points_marques, points_encaisse, victoire):
        self.points_marques += points_marques
        self.points_encaisse += points_encaisse
        self.points += 3 if victoire else 1
        self.matchs_joues += 1
        self.matchs_enregistres += 1

    def quotient_points(self):
        return self.points_marques / max(1, self.points_encaisse)

    def difference_points(self):
        return self.points_marques - self.points_encaisse

    def __repr__(self):
        return f"{self.nom} (Pts: {self.points}, Quotient: {self.quotient_points():.2f}, Diff: {self.difference_points()}, Matchs: {self.matchs_joues})"

class Match:
    def __init__(self, equipe1, equipe2, mode):
        self.equipe1 = equipe1
        self.equipe2 = equipe2
        self.mode = mode
        self.score1 = None
        self.score2 = None
        self.arbitre = None
        self.terrain = None
        self.serie = None

    def simuler(self):
        self.score1, self.score2 = random.randint(10, 25), random.randint(10, 25)
        while self.score1 == self.score2:
            self.score2 = random.randint(10, 25)

        victoire_e1 = self.score1 > self.score2

        if self.mode == "officiel":
            self.equipe1.ajouter_resultat(self.score1, self.score2, victoire_e1)
            self.equipe2.ajouter_resultat(self.score2, self.score1, not victoire_e1)
        elif self.mode == "exempt":
            self.equipe1.ajouter_resultat_force(self.score1, self.score2, victoire_e1)

    def __repr__(self):
        mode_txt = "(Comptabilise)" if self.mode == "officiel" else f"(Seuls les points de {self.equipe1.nom} comptent)"
        arbitre_txt = f" | Arbitre : {self.arbitre.nom}" if self.arbitre else " | Aucun arbitre"
        return f"[Serie {self.serie}] Terrain {self.terrain} : {self.equipe1.nom} {self.score1} - {self.score2} {self.equipe2.nom} {mode_txt}{arbitre_txt}"


def generer_matchs_brassage(equipes, nb_terrains):
    max_tries = 1000
    for _ in range(max_tries):
        try:
            matchs, equipe_exemptee = _generer_matchs_brassage_essai(equipes)
            matchs_planifies = repartir_matchs_sur_terrains(matchs, equipes, nb_terrains)
            return matchs_planifies, equipe_exemptee
        except ValueError:
            continue
    raise RuntimeError("Impossible de generer une configuration valide apres plusieurs tentatives.")

def _generer_matchs_brassage_essai(equipes):
    equipes_copy = equipes[:]
    random.shuffle(equipes_copy)
    matchs = []
    equipe_exemptee = None

    if len(equipes_copy) % 2 == 1:
        equipe_exemptee = equipes_copy.pop()

    matchs_par_equipe = {e.nom: 0 for e in equipes_copy}
    possible_matchs = list(combinations(equipes_copy, 2))
    random.shuffle(possible_matchs)

    for e1, e2 in possible_matchs:
        if matchs_par_equipe[e1.nom] < 2 and matchs_par_equipe[e2.nom] < 2:
            match = Match(e1, e2, "officiel")
            matchs.append(match)
            matchs_par_equipe[e1.nom] += 1
            matchs_par_equipe[e2.nom] += 1
        if all(v == 2 for v in matchs_par_equipe.values()):
            break

    if not all(v == 2 for v in matchs_par_equipe.values()):
        raise ValueError("Distribution incomplete")

    if equipe_exemptee:
        adversaires = random.sample(equipes_copy, 2)
        for adv in adversaires:
            match = Match(equipe_exemptee, adv, "exempt")
            matchs.append(match)

    return matchs, equipe_exemptee

def repartir_matchs_sur_terrains(matchs, toutes_equipes, nb_terrains):
    arbitrages = {equipe.nom: 0 for equipe in toutes_equipes}
    i = 0
    serie_num = 1
    while i < len(matchs):
        serie = matchs[i:i+nb_terrains]
        equipes_jouant = set()
        for m in serie:
            equipes_jouant.add(m.equipe1.nom)
            equipes_jouant.add(m.equipe2.nom)

        disponibles = [e for e in toutes_equipes if e.nom not in equipes_jouant]
        disponibles.sort(key=lambda e: arbitrages[e.nom])

        for j, match in enumerate(serie):
            match.terrain = (j % nb_terrains) + 1
            match.serie = serie_num
            if disponibles:
                match.arbitre = disponibles.pop(0)
                arbitrages[match.arbitre.nom] += 1
        i += nb_terrains
        serie_num += 1
    return matchs

def classer_equipes(equipes):
    return sorted(equipes, key=lambda x: (-x.points, -x.quotient_points(), -x.difference_points(), random.random()))

def creer_poules_depuis_classement(equipes_classees):
    total = len(equipes_classees)
    taille_poule_haute = (total + 1) // 2
    if taille_poule_haute % 2 != 0:
        taille_poule_haute += 1

    poule_haute = equipes_classees[:taille_poule_haute]
    poule_basse = equipes_classees[taille_poule_haute:]
    return poule_haute, poule_basse

def diviser_en_sous_poules_serpentin(poule):
    sous_poule_1, sous_poule_2 = [], []
    for i, equipe in enumerate(poule):
        if i % 2 == 0:
            sous_poule_1.append(equipe)
        else:
            sous_poule_2.append(equipe)
    return sous_poule_1, sous_poule_2

def matchs_poules(sous_poules):
    matchs = []
    for sous_poule in sous_poules:
        for i in range(len(sous_poule)):
            for j in range(i + 1, len(sous_poule)):
                matchs.append(Match(sous_poule[i], sous_poule[j], "officiel"))
    return matchs

def melanger_matchs(matchs):
    random.shuffle(matchs)
    return matchs

def planifier_matchs_dynamique_optimal(matchs_sous_poules, nb_terrains):
    tous_les_matchs = []
    for matchs in matchs_sous_poules:
        tous_les_matchs.extend(matchs)

    # Générer toutes les combinaisons possibles de séries valides
    def est_serie_valide(serie):
        equipes = set()
        for match in serie:
            if match.equipe1.nom in equipes or match.equipe2.nom in equipes:
                return False
            equipes.add(match.equipe1.nom)
            equipes.add(match.equipe2.nom)
        return True

    def chercher_series(matchs_restants, series_acc, profondeur=0):
        if not matchs_restants:
            return series_acc

        possibles_series = [list(c) for c in combinations(matchs_restants, nb_terrains) if est_serie_valide(c)]
        random.shuffle(possibles_series)  # pour variété si plusieurs solutions

        for serie in possibles_series:
            restants = [m for m in matchs_restants if m not in serie]
            resultat = chercher_series(restants, series_acc + [serie], profondeur + 1)
            if resultat:
                return resultat

        return None  # échec

    solution = chercher_series(tous_les_matchs, [])

    if not solution:
        raise RuntimeError("Impossible de planifier les matchs sans conflits en 4 séries.")

    return solution

def repartir_matchs_poules_avec_arbitres(series_planifiees, toutes_equipes, nb_terrains):
    arbitrages = {equipe.nom: 0 for equipe in toutes_equipes}
    for serie_num, serie in enumerate(series_planifiees, 1):
        equipes_jouant = set()
        for match in serie:
            equipes_jouant.add(match.equipe1.nom)
            equipes_jouant.add(match.equipe2.nom)

        disponibles = [e for e in toutes_equipes if e.nom not in equipes_jouant]
        disponibles.sort(key=lambda e: arbitrages[e.nom])

        for terrain_index, match in enumerate(serie):
            match.terrain = terrain_index + 1
            match.serie = serie_num
            if disponibles:
                match.arbitre = disponibles.pop(0)
                arbitrages[match.arbitre.nom] += 1
    return series_planifiees, arbitrages

def afficher_classement_par_sous_poule(sous_poules):
    for nom_sous_poule, equipes in sous_poules.items():
        classement = classer_equipes([e for e in equipes if e.matchs_enregistres > 0])
        print(f"\nClassement sous-poule {nom_sous_poule} :")
        for equipe in classement:
            print(equipe)

def reinitialiser_stats_equipes(equipes):
    for equipe in equipes:
        equipe.points = 0
        equipe.points_marques = 0
        equipe.points_encaisse = 0
        equipe.matchs_joues = 0
        equipe.matchs_enregistres = 0

def generer_matchs_finals(classements_par_sous_poule):
    """
    Génère les matchs de classement final à partir des sous-poules hautes (H1, H2)
    et basses (B1, B2). Ne mélange pas les niveaux.
    """
    def extraire_matchs_final_par_rang(classement_a, classement_b, rang):
        if len(classement_a) >= rang and len(classement_b) >= rang:
            return Match(classement_a[rang-1], classement_b[rang-1], "officiel")
        return None

    labels = [
        "Finale (1ere/2e place)",
        "Petite finale (3e/4e place)",
        "Match pour la 5e/6e place",
        "Match pour la 7e/8e place",
        "Match pour la 9e/10e place",
        "Match pour la 11e/12e place"
    ]

    matchs = []
    noms_matchs = []

    # Matchs entre H1 et H2
    h1 = classements_par_sous_poule.get("H1", [])
    h2 = classements_par_sous_poule.get("H2", [])
    for i in range(3):
        match = extraire_matchs_final_par_rang(h1, h2, i+1)
        if match:
            matchs.append(match)
            noms_matchs.append(labels[i])

    # Matchs entre B1 et B2
    b1 = classements_par_sous_poule.get("B1", [])
    b2 = classements_par_sous_poule.get("B2", [])
    for i in range(3):
        match = extraire_matchs_final_par_rang(b1, b2, i+1)
        if match:
            matchs.append(match)
            noms_matchs.append(labels[i + 3])

    return matchs, noms_matchs

def estimer_temps_par_serie(matchs_brassage, matchs_poules, matchs_finals, nb_terrains, temps_total_max_minutes):
    """
    Calcule le temps maximal disponible pour chaque série (matchs joués en parallèle),
    afin de tenir dans le temps total alloué. Compte 5 min de pause entre chaque série.
    """
    import math

    # Total matchs
    tous_les_matchs = []
    tous_les_matchs.extend(matchs_brassage)
    tous_les_matchs.extend(matchs_poules)
    tous_les_matchs.extend(matchs_finals)

    total_matchs = len(tous_les_matchs)

    # Nombre de séries nécessaires
    total_series = math.ceil(total_matchs / nb_terrains)

    # Pauses : 5 min entre les séries (n-1 pauses)
    total_pause_time = max(0, total_series - 1) * 4

    # Temps dispo pour le jeu
    temps_dispo_matchs = temps_total_max_minutes - total_pause_time
    if temps_dispo_matchs <= 0:
        raise ValueError("Temps total trop court pour caser les pauses.")

    # Temps max par série (matchs joués en parallèle)
    temps_par_serie = temps_dispo_matchs / total_series

    return {
        "total_matchs": total_matchs,
        "total_series": total_series,
        "temps_total_pauses": total_pause_time,
        "temps_par_serie_max": temps_par_serie,
        "temps_total_max": temps_total_max_minutes
    }


def repartir_matchs_finals_sur_terrains(matchs_finals, equipes, nb_terrains):
    """
    Répartit les matchs de classement final sur les terrains par série.
    Priorité aux petits classements d'abord.
    Attribution d’arbitres équilibrée.
    """
    arbitrages = {e.nom: 0 for e in equipes}
    series = []
    serie_num = 1

    # On joue les petites places d'abord : 11e/12e → 1ère/2e
    matchs_finals_reverses = list(reversed(matchs_finals))

    i = 0
    while i < len(matchs_finals_reverses):
        serie = []
        equipes_utilisees = set()
        j = 0
        while j < len(matchs_finals_reverses) and len(serie) < nb_terrains:
            match = matchs_finals_reverses[j]
            if match.equipe1.nom not in equipes_utilisees and match.equipe2.nom not in equipes_utilisees:
                serie.append(match)
                equipes_utilisees.update([match.equipe1.nom, match.equipe2.nom])
                matchs_finals_reverses.pop(j)
            else:
                j += 1

        # Attribution terrain et arbitres
        non_joueurs = [e for e in equipes if e.nom not in equipes_utilisees]
        non_joueurs.sort(key=lambda e: arbitrages[e.nom])  # Priorité à ceux qui ont le moins arbitré

        for terrain_index, match in enumerate(serie):
            match.terrain = terrain_index + 1
            match.serie = serie_num
            if non_joueurs:
                match.arbitre = non_joueurs.pop(0)
                arbitrages[match.arbitre.nom] += 1

        series.append(serie)
        serie_num += 1

    return series, arbitrages

def generer_classement_final(matchs_finals):
    """
    Retourne une liste ordonnée des équipes selon leur classement final (1er à 12e)
    basé sur les résultats des matchs de classement.
    """
    classement = []

    # Dictionnaire de correspondance match => place
    positions = [
        (1, 2),    # finale
        (3, 4),    # petite finale
        (5, 6),    # match 5e/6e
        (7, 8),    # match 7e/8e
        (9, 10),   # match 9e/10e
        (11, 12)   # match 11e/12e
    ]

    for match, (place_gagnant, place_perdant) in zip(matchs_finals, positions):
        if match.score1 is None or match.score2 is None:
            continue  # match non simulé
        gagnant = match.equipe1 if match.score1 > match.score2 else match.equipe2
        perdant = match.equipe2 if gagnant == match.equipe1 else match.equipe1
        classement.append((place_gagnant, gagnant))
        classement.append((place_perdant, perdant))

    classement.sort(key=lambda x: x[0])  # trier par position
    return classement

if __name__ == "__main__":
    random.seed()
    nb_equipes = 12
    nb_terrains = 3

    equipes = [Equipe(f"Equipe {i+1}") for i in range(nb_equipes)]

    matchs_brassage, exempt = generer_matchs_brassage(equipes, nb_terrains)

    print("\nMatchs de brassage (avec terrain et arbitre) :")
    arbitrages = {equipe.nom: 0 for equipe in equipes}
    for match in matchs_brassage:
        match.simuler()
        print(match)
        if match.arbitre:
            arbitrages[match.arbitre.nom] += 1

    print("\nResume arbitrage par equipe :")
    for nom, count in arbitrages.items():
        print(f"{nom} : {count} arbitrage(s)")

    manquants = [nom for nom, count in arbitrages.items() if count == 0]
    if manquants:
        print("\n Attention : les equipes suivantes n'ont jamais arbitre :")
        for nom in manquants:
            print(f" {nom}")
    else:
        print("\n Toutes les equipes ont arbitre au moins une fois.")

    print("\nClassement apres brassage :")
    classement = classer_equipes(equipes)
    for equipe in classement:
        print(equipe)

    print("\nRepartition des poules :")
    haute, basse = creer_poules_depuis_classement(classement)
    print(f"Poule haute : {len(haute)} equipes")
    print(f"Poule basse : {len(basse)} equipes")

    print("\nPoule haute :")
    for equipe in haute:
        print(equipe)

    print("\nPoule basse :")
    for equipe in basse:
        print(equipe)

    print("\nSous-poules Haute")
    h1, h2 = diviser_en_sous_poules_serpentin(haute)
    print("H1:")
    for e in h1:
        print(f" - {e.nom}")
    print("H2:")
    for e in h2:
        print(f" - {e.nom}")

    if len(basse) % 2 == 0:
        print("\nSous-poules Basse")
        b1, b2 = diviser_en_sous_poules_serpentin(basse)
        print("B1:")
        for e in b1:
            print(f" - {e.nom}")
        print("B2:")
        for e in b2:
            print(f" - {e.nom}")
    else:
        b1, b2 = basse, []
        print("\nPoule basse non divisee (nombre impair)")
        for e in b1:
            print(f" - {e.nom}")

    print("\nMatchs sous-poule H1 :")
    matchs_h1 = melanger_matchs(matchs_poules([h1]))
    for match in matchs_h1:
        print(f"{match.equipe1.nom} vs {match.equipe2.nom}")

    print("\nMatchs sous-poule H2 :")
    matchs_h2 = melanger_matchs(matchs_poules([h2]))
    for match in matchs_h2:
        print(f"{match.equipe1.nom} vs {match.equipe2.nom}")

    print("\nMatchs sous-poule B1 :")
    matchs_b1 = melanger_matchs(matchs_poules([b1]))
    for match in matchs_b1:
        print(f"{match.equipe1.nom} vs {match.equipe2.nom}")

    if b2:
        print("\nMatchs sous-poule B2 :")
        matchs_b2 = melanger_matchs(matchs_poules([b2]))
        for match in matchs_b2:
            print(f"{match.equipe1.nom} vs {match.equipe2.nom}")
    else:
        matchs_b2 = []

    reinitialiser_stats_equipes(equipes)
    for match in matchs_h1:
        match.sous_poule = "H1"
    for match in matchs_h2:
        match.sous_poule = "H2"
    for match in matchs_b1:
        match.sous_poule = "B1"
    for match in matchs_b2:
        match.sous_poule = "B2"

    for match in matchs_h1 + matchs_h2 + matchs_b1 + matchs_b2:
        match.simuler()

    series = planifier_matchs_dynamique_optimal([matchs_h1, matchs_h2, matchs_b1] + ([matchs_b2] if b2 else []), nb_terrains)
    series, arbitrages_poules = repartir_matchs_poules_avec_arbitres(series, equipes, nb_terrains)

    print("\n--- Planning des matchs de poules ---")
    for i, serie in enumerate(series):
        print(f"\nSerie {i+1}:")
        for match in serie:
            sous_poule = getattr(match, 'sous_poule', 'Inconnue')
            print(f"({sous_poule}) {match}")

    print("\nResume arbitrage poules par equipe :")
    for nom, count in arbitrages_poules.items():
        print(f"{nom} : {count} arbitrage(s)")

    manquants = [nom for nom, count in arbitrages_poules.items() if count == 0]
    if manquants:
        print("\n Attention : les equipes suivantes n'ont jamais arbitre pendant les poules :")
        for nom in manquants:
            print(f" {nom}")
    else:
        print("\n Toutes les equipes ont arbitre au moins une fois pendant les poules.")

    print("\n--- Classement final ---")
    afficher_classement_par_sous_poule({
        "H1": h1,
        "H2": h2,
        "B1": b1,
        "B2": b2
    })

    classements = {
    "H1": classer_equipes(h1),
    "H2": classer_equipes(h2),
    "B1": classer_equipes(b1),
    "B2": classer_equipes(b2)
    }

    matchs_finals, noms_matchs = generer_matchs_finals(classements)

    print("\n--- Matchs de classement final ---")
    for nom, match in zip(noms_matchs, matchs_finals):
        print(f"{nom} : {match.equipe1.nom} vs {match.equipe2.nom}")

    series_finals, arbitrages_finals = repartir_matchs_finals_sur_terrains(matchs_finals, equipes, nb_terrains)
    # Simuler les scores des matchs de finale
    for serie in series_finals:
        for match in serie:
            match.simuler()

    print("\n--- Planning des matchs de classement final ---")
    for i, serie in enumerate(series_finals):
        print(f"\nSerie finale {i+1}:")
        for match in serie:
            print(f"{match}")

    classement_final = generer_classement_final(matchs_finals)
    print("\n--- Classement final ---")
    for place, equipe in classement_final:
        print(f"{place} : {equipe.nom}")


    estimation = estimer_temps_par_serie(
        matchs_brassage,
        matchs_h1 + matchs_h2 + matchs_b1 + matchs_b2,
        matchs_finals,
        nb_terrains,
        temps_total_max_minutes=120  # ← durée max en minutes
    )

    print("\n>>> ESTIMATION TEMPORELLE DU TOURNOI <<<")
    print(f"Nombre total de matchs        : {estimation['total_matchs']}")
    print(f"Nombre total de series        : {estimation['total_series']} (avec {nb_terrains} terrains)")
    print(f"Total temps reserve aux pauses : {estimation['temps_total_pauses']} min")
    print(f"Duree max autorisee par serie  : {estimation['temps_par_serie_max']:.2f} min")



