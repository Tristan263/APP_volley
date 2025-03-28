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
    return [Equipe(f"Équipe {i+1}") for i in range(n)]

def generer_matchs_brassage(equipes):
    max_tries = 1000
    for _ in range(max_tries):
        try:
            matchs, equipe_exemptee = _generer_matchs_brassage_essai(equipes)
            if equipe_exemptee:
                print(f"\nÉquipe exemptée : {equipe_exemptee.nom}")
            return matchs, equipe_exemptee
        except ValueError:
            continue
    raise RuntimeError("Impossible de générer une configuration valide après plusieurs tentatives.")

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
        raise ValueError("Distribution incomplète")

    if equipe_exemptee:
        adversaires = random.sample(equipes_copy, 2)
        for adv in adversaires:
            matchs.append((equipe_exemptee, adv, "exempt"))

    return matchs, equipe_exemptee

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

# --- EXÉCUTION DU TOURNOI ---
if __name__ == "__main__":
    random.seed(42)
    nombre_equipes = 11
    equipes = generer_equipes(nombre_equipes)
    matchs_brassage, equipe_exemptee = generer_matchs_brassage(equipes)

    print("\nMatchs de brassage:")
    for e1, e2, mode in matchs_brassage:
        nom1, s1, nom2, s2, m = simuler_match(e1, e2, mode)
        if m == "officiel":
            print(f"{nom1} {s1} - {s2} {nom2} (Comptabilisé)")
        else:
            print(f"{nom1} {s1} - {s2} {nom2} (Seuls les points de {nom1} comptent)")

    print(f"\nNombre total de matchs joués (officiels + amicaux) : {len(matchs_brassage)}")

    equipes_classees = classer_equipes(equipes)
    print("\nClassement après brassage :")
    for equipe in equipes_classees:
        print(equipe)
