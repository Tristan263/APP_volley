#problème avec les matchs et répartition des terrains sur les matchs de poules 
#gérer les matchs de fin de tournoi
#gérer le système de temps pour ajuster le temps de jeu par match 
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
        mode_txt = "(Comptabilis\u00e9)" if self.mode == "officiel" else f"(Seuls les points de {self.equipe1.nom} comptent)"
        arbitre_txt = f" | Arbitre : {self.arbitre.nom}" if self.arbitre else " | Aucun arbitre"
        return f"[S\u00e9rie {self.serie}] Terrain {self.terrain} : {self.equipe1.nom} {self.score1} - {self.score2} {self.equipe2.nom} {mode_txt}{arbitre_txt}"


def generer_matchs_brassage(equipes, nb_terrains):
    max_tries = 1000
    for _ in range(max_tries):
        try:
            matchs, equipe_exemptee = _generer_matchs_brassage_essai(equipes)
            matchs_planifies = repartir_matchs_sur_terrains(matchs, equipes, nb_terrains)
            return matchs_planifies, equipe_exemptee
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
            match = Match(e1, e2, "officiel")
            matchs.append(match)
            matchs_par_equipe[e1.nom] += 1
            matchs_par_equipe[e2.nom] += 1
        if all(v == 2 for v in matchs_par_equipe.values()):
            break

    if not all(v == 2 for v in matchs_par_equipe.values()):
        raise ValueError("Distribution incompl\u00e8te")

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

def planifier_matchs_dynamique(matchs_sous_poules, nb_terrains):
    tous_les_matchs = []
    for matchs in matchs_sous_poules:
        tous_les_matchs.extend(matchs)
    random.shuffle(tous_les_matchs)

    series_planifiees = []
    i = 0
    while tous_les_matchs:
        serie = []
        equipes_utilisees = set()
        j = 0
        while j < len(tous_les_matchs) and len(serie) < nb_terrains:
            match = tous_les_matchs[j]
            if match.equipe1.nom not in equipes_utilisees and match.equipe2.nom not in equipes_utilisees:
                serie.append(match)
                equipes_utilisees.add(match.equipe1.nom)
                equipes_utilisees.add(match.equipe2.nom)
                tous_les_matchs.pop(j)
            else:
                j += 1
        if not serie:
            raise RuntimeError("Impossible de planifier les matchs sans conflits d\u00e9j\u00e0 jou\u00e9s dans une s\u00e9rie.")
        series_planifiees.append(serie)
    return series_planifiees
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
        # On recalcule les stats à partir des objets actuels
        classement = classer_equipes([e for e in equipes if e.matchs_enregistres > 0])
        print(f"\n\U0001f4ca Classement sous-poule {nom_sous_poule} :")
        for equipe in classement:
            print(equipe)
def reinitialiser_stats_equipes(equipes):
    for equipe in equipes:
        equipe.points = 0
        equipe.points_marques = 0
        equipe.points_encaisse = 0
        equipe.matchs_joues = 0
        equipe.matchs_enregistres = 0
if __name__ == "__main__":
    random.seed()
    nb_equipes = 12
    nb_terrains = 3

    equipes = [Equipe(f"\u00c9quipe {i+1}") for i in range(nb_equipes)]

    matchs_brassage, exempt = generer_matchs_brassage(equipes, nb_terrains)

    print("\nMatchs de brassage (avec terrain et arbitre) :")
    arbitrages = {equipe.nom: 0 for equipe in equipes}
    for match in matchs_brassage:
        match.simuler()
        print(match)
        if match.arbitre:
            arbitrages[match.arbitre.nom] += 1

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
    classement = classer_equipes(equipes)
    for equipe in classement:
        print(equipe)

    print("\n\U0001f4ca R\u00e9partition des poules :")
    haute, basse = creer_poules_depuis_classement(classement)
    print(f"Poule haute : {len(haute)} \u00e9quipes")
    print(f"Poule basse : {len(basse)} \u00e9quipes")

    print("\n\U0001f3c6 Poule haute :")
    for equipe in haute:
        print(equipe)

    print("\n\u2699\ufe0f Poule basse :")
    for equipe in basse:
        print(equipe)

    print("\n\U0001f537 Sous-poules Haute")
    h1, h2 = diviser_en_sous_poules_serpentin(haute)
    print("H1:")
    for e in h1:
        print(f" - {e.nom}")
    print("H2:")
    for e in h2:
        print(f" - {e.nom}")

    if len(basse) % 2 == 0:
        print("\n\U0001f536 Sous-poules Basse")
        b1, b2 = diviser_en_sous_poules_serpentin(basse)
        print("B1:")
        for e in b1:
            print(f" - {e.nom}")
        print("B2:")
        for e in b2:
            print(f" - {e.nom}")
    else:
        b1, b2 = basse, []
        print("\n\U0001f536 Poule basse non divis\u00e9e (nombre impair)")
        for e in b1:
            print(f" - {e.nom}")

    print("\n\U0001f537 Matchs sous-poule H1 :")
    matchs_h1 = melanger_matchs(matchs_poules([h1]))
    for match in matchs_h1:
        print(f"{match.equipe1.nom} vs {match.equipe2.nom}")

    print("\n\U0001f537 Matchs sous-poule H2 :")
    matchs_h2 = melanger_matchs(matchs_poules([h2]))
    for match in matchs_h2:
        print(f"{match.equipe1.nom} vs {match.equipe2.nom}")

    print("\n\U0001f536 Matchs sous-poule B1 :")
    matchs_b1 = melanger_matchs(matchs_poules([b1]))
    for match in matchs_b1:
        print(f"{match.equipe1.nom} vs {match.equipe2.nom}")

    if b2:
        print("\n\U0001f536 Matchs sous-poule B2 :")
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

    series = planifier_matchs_dynamique([matchs_h1, matchs_h2, matchs_b1] + ([matchs_b2] if b2 else []), nb_terrains)
    series, arbitrages_poules = repartir_matchs_poules_avec_arbitres(series, equipes, nb_terrains)

    print("\n--- Planning des matchs de poules ---")
    for i, serie in enumerate(series):
        print(f"\nSérie {i+1}:")
        for match in serie:
            sous_poule = getattr(match, 'sous_poule', 'Inconnue')
            print(f"({sous_poule}) {match}")

    print("\nRésumé arbitrage poules par équipe :")
    for nom, count in arbitrages_poules.items():
        print(f"{nom} : {count} arbitrage(s)")

    manquants = [nom for nom, count in arbitrages_poules.items() if count == 0]
    if manquants:
        print("\n⚠️ Attention : les équipes suivantes n'ont jamais arbitré pendant les poules :")
        for nom in manquants:
            print(f"❌ {nom}")
    else:
        print("\n✅ Toutes les équipes ont arbitré au moins une fois pendant les poules.")
    print("\n--- Classement final ---")
    afficher_classement_par_sous_poule({
        "H1": h1,
        "H2": h2,
        "B1": b1,
        "B2": b2
    })