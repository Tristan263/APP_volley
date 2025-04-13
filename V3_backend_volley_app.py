import random
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

def generer_equipes(n):
    return [Equipe(f"\u00c9quipe {i+1}") for i in range(n)]

def generer_matchs_brassage(equipes, nb_terrains):
    max_tries = 1000
    for _ in range(max_tries):
        try:
            matchs, equipe_exemptee = _generer_matchs_brassage_essai(equipes)
            if equipe_exemptee:
                print(f"\n\u00c9quipe exemptée : {equipe_exemptee.nom}")
            return repartir_matchs_sur_terrains(matchs, equipes, nb_terrains)
        except ValueError:
            continue
    raise RuntimeError("Impossible de g\u00e9n\u00e9rer une configuration valide apr\u00e8s plusieurs tentatives.")

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
            matchs.append((e1, e2, "officiel"))
            matchs_par_equipe[e1.nom] += 1
            matchs_par_equipe[e2.nom] += 1
        if all(v == 2 for v in matchs_par_equipe.values()):
            break

    if not all(v == 2 for v in matchs_par_equipe.values()):
        raise ValueError("Distribution incompl\u00e8te")

    if equipe_exemptee:
        adversaires = random.sample(equipes_copy, 2)
        for adv in adversaires:
            matchs.append((equipe_exemptee, adv, "exempt"))

    return matchs, equipe_exemptee

def repartir_matchs_sur_terrains(matchs, toutes_equipes, nb_terrains):
    arbitrages = {equipe.nom: 0 for equipe in toutes_equipes}
    match_infos = []

    i = 0
    while i < len(matchs):
        serie = matchs[i:i+nb_terrains]
        equipes_jouant = set()
        for m in serie:
            equipes_jouant.add(m[0].nom)
            equipes_jouant.add(m[1].nom)

        disponibles = [e for e in toutes_equipes if e.nom not in equipes_jouant]
        disponibles.sort(key=lambda e: arbitrages[e.nom])

        for j, match in enumerate(serie):
            terrain = (j % nb_terrains) + 1
            if disponibles:
                arbitre = disponibles.pop(0)
                arbitrages[arbitre.nom] += 1
            else:
                arbitre = None
            match_infos.append({
                "serie": i // nb_terrains + 1,
                "terrain": terrain,
                "match": match,
                "arbitre": arbitre
            })
        i += nb_terrains

    return match_infos, arbitrages

def simuler_match(e1, e2, mode):
    score1, score2 = random.randint(10, 25), random.randint(10, 25)
    while score1 == score2:
        score2 = random.randint(10, 25)

    victoire_e1 = score1 > score2

    if mode == "officiel":
        e1.ajouter_resultat(score1, score2, victoire_e1)
        e2.ajouter_resultat(score2, score1, not victoire_e1)
    elif mode == "exempt":
        e1.ajouter_resultat_force(score1, score2, victoire_e1)

    return e1.nom, score1, e2.nom, score2, mode

def classer_equipes(equipes):
    return sorted(equipes, key=lambda x: (-x.points, -x.quotient_points(), -x.difference_points(), random.random()))

def creer_poules_depuis_classement(equipes_classees):
    total = len(equipes_classees)
    taille_poule_haute = (total + 1) // 2
    if taille_poule_haute % 2 != 0:
        taille_poule_haute += 1

    poule_haute = equipes_classees[:taille_poule_haute]
    poule_basse = equipes_classees[taille_poule_haute:]

    print(f"\n\U0001f4ca R\u00e9partition des poules :")
    print(f"Poule haute : {len(poule_haute)} \u00e9quipes")
    print(f"Poule basse : {len(poule_basse)} \u00e9quipes")

    print("\n\U0001f3c6 Poule haute :")
    for equipe in poule_haute:
        print(equipe)

    print("\n\u2699\ufe0f Poule basse :")
    for equipe in poule_basse:
        print(equipe)

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
                matchs.append((sous_poule[i], sous_poule[j]))
    return matchs

def melanger_matchs(matchs):
    random.shuffle(matchs)
    return matchs

def planifier_matchs_dynamique(matchs_sous_poules, nb_terrains):
    tous_les_matchs = []
    for matchs in matchs_sous_poules:
        tous_les_matchs.extend(matchs)
    random.shuffle(tous_les_matchs)
    series_planifiees = []
    i = 0
    while i < len(tous_les_matchs):
        serie = tous_les_matchs[i:i + nb_terrains]
        series_planifiees.append(serie)
        i += nb_terrains
    return series_planifiees

if __name__ == "__main__":
    random.seed()
    nombre_equipes = 12
    nb_terrains = 3

    equipes = generer_equipes(nombre_equipes)
    match_infos, arbitrages = generer_matchs_brassage(equipes, nb_terrains)

    print("\nMatchs de brassage (avec terrain et arbitre) :")
    for info in match_infos:
        e1, e2, mode = info["match"]
        nom1, s1, nom2, s2, m = simuler_match(e1, e2, mode)
        arbitre_txt = f" | Arbitre : {info['arbitre'].nom}" if info["arbitre"] else " | Aucun arbitre"
        type_txt = "(Comptabilis\u00e9)" if mode == "officiel" else f"(Seuls les points de {nom1} comptent)"
        print(f"[S\u00e9rie {info['serie']}] Terrain {info['terrain']} : {nom1} {s1} - {s2} {nom2} {type_txt}{arbitre_txt}")

    print("\nR\u00e9sum\u00e9 arbitrage par \u00e9quipe :")
    for nom, count in arbitrages.items():
        print(f"{nom} : {count} arbitrage(s)")

    manquants = [nom for nom, count in arbitrages.items() if count == 0]
    if manquants:
        print("\n\u26a0\ufe0f Attention : les \u00e9quipes suivantes n'ont jamais arbitr\u00e9 :")
        for nom in manquants:
            print(f"\u274c {nom}")
    else:
        print("\n\u2705 Toutes les \u00e9quipes ont arbitr\u00e9 au moins une fois.")

    print("\nClassement apr\u00e8s brassage :")
    equipes_classees = classer_equipes(equipes)
    for equipe in equipes_classees:
        print(equipe)

    poule_haute, poule_basse = creer_poules_depuis_classement(equipes_classees)

    sous_poule_H1, sous_poule_H2 = diviser_en_sous_poules_serpentin(poule_haute)
    if len(poule_basse) % 2 == 0:
        sous_poule_B1, sous_poule_B2 = diviser_en_sous_poules_serpentin(poule_basse)
    else:
        sous_poule_B1, sous_poule_B2 = poule_basse, []

    print("\n\U0001f537 Sous-poules Haute")
    print("H1:")
    for equipe in sous_poule_H1:
        print(f" - {equipe.nom}")
    print("H2:")
    for equipe in sous_poule_H2:
        print(f" - {equipe.nom}")

    if sous_poule_B2:
        print("\n\U0001f536 Sous-poules Basse")
        print("B1:")
        for equipe in sous_poule_B1:
            print(f" - {equipe.nom}")
        print("B2:")
        for equipe in sous_poule_B2:
            print(f" - {equipe.nom}")
    else:
        print("\n\U0001f536 Poule basse non divis\u00e9e (nombre impair)")
        for equipe in sous_poule_B1:
            print(f" - {equipe.nom}")

    matchs_H1 = melanger_matchs(matchs_poules([sous_poule_H1]))
    matchs_H2 = melanger_matchs(matchs_poules([sous_poule_H2]))
    matchs_B1 = melanger_matchs(matchs_poules([sous_poule_B1]))
    matchs_B2 = melanger_matchs(matchs_poules([sous_poule_B2])) if sous_poule_B2 else []

    print("\n\U0001f537 Matchs sous-poule H1 :")
    for match in matchs_H1:
        print(f"{match[0].nom} vs {match[1].nom}")
    print("\n\U0001f537 Matchs sous-poule H2 :")
    for match in matchs_H2:
        print(f"{match[0].nom} vs {match[1].nom}")
    print("\n\U0001f536 Matchs sous-poule B1 :")
    for match in matchs_B1:
        print(f"{match[0].nom} vs {match[1].nom}")
    if sous_poule_B2:
        print("\n\U0001f536 Matchs sous-poule B2 :")
        for match in matchs_B2:
            print(f"{match[0].nom} vs {match[1].nom}")

    series_planifiees = planifier_matchs_dynamique(
        [matchs_H1, matchs_H2, matchs_B1] + ([matchs_B2] if sous_poule_B2 else []), nb_terrains)

    print("\n\U0001f4c5 Planning des matchs de poules par s\u00e9rie (r\u00e9partition dynamique) :")
    for idx, serie in enumerate(series_planifiees):
        print(f"\n\U0001f4cd S\u00e9rie {idx + 1} :")
        for terrain, match in enumerate(serie, start=1):
            print(f"  Terrain {terrain} : {match[0].nom} vs {match[1].nom}")
