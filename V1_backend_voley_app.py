import random
from itertools import combinations

class Equipe:
    def __init__(self, nom):
        self.nom = nom
        self.points = 0
        self.points_marques = 0
        self.points_encaisse = 0
        self.matchs_joues = 0  # Ajout d'un compteur de matchs joués

    def ajouter_resultat(self, points_marques, points_encaisse, victoire):
        self.points_marques += points_marques
        self.points_encaisse += points_encaisse
        self.points += 3 if victoire else 1
        self.matchs_joues += 1

    def quotient_points(self):
        return self.points_marques / max(1, self.points_encaisse)
    
    def difference_points(self):
        return self.points_marques - self.points_encaisse

    def __repr__(self):
        return f"{self.nom} (Pts: {self.points}, Quotient: {self.quotient_points():.2f}, Diff: {self.difference_points()}, Matchs: {self.matchs_joues})"

# Phase 1: Génération aléatoire des équipes
def generer_equipes(n):
    return [Equipe(f"Équipe {i+1}") for i in range(n)]

# Phase 2: Génération des matchs de brassage avec garantie de 2 matchs/équipe
def generer_matchs_brassage(equipes):
    random.shuffle(equipes)
    matchs = []
    matchs_par_equipe = {equipe.nom: 0 for equipe in equipes}
    
    while any(v < 2 for v in matchs_par_equipe.values()):
        candidats = [equipe for equipe in equipes if matchs_par_equipe[equipe.nom] < 2]
        if len(candidats) < 2:
            break  # Si moins de 2 équipes restantes, on arrête
        e1, e2 = random.sample(candidats, 2)
        matchs.append((e1, e2))
        matchs_par_equipe[e1.nom] += 1
        matchs_par_equipe[e2.nom] += 1
    
    return matchs

# Phase 3: Simuler les résultats des matchs
def simuler_match(equipe1, equipe2):
    score1, score2 = random.randint(10, 25), random.randint(10, 25)
    while score1 == score2:
        score2 = random.randint(10, 25)
    
    victoire_e1 = score1 > score2
    equipe1.ajouter_resultat(score1, score2, victoire_e1)
    equipe2.ajouter_resultat(score2, score1, not victoire_e1)

# Phase 4: Classer les équipes avec critères de départage
def classer_equipes(equipes):
    return sorted(equipes, key=lambda x: (-x.points, -x.quotient_points(), -x.difference_points(), random.random()))

# Phase 5: Répartition en poules avec équilibre et alternance
def repartir_poules(equipes):
    equipes = classer_equipes(equipes)
    n = len(equipes)
    
    poule_haute1, poule_haute2, poule_basse1, poule_basse2 = [], [], [], []
    
    if n % 2 == 0:
        poule_haute = equipes[:n//2]
        poule_basse = equipes[n//2:]
    else:
        poule_haute = equipes[:(n//2) + 1]  # La poule haute est toujours paire
        poule_basse = equipes[(n//2) + 1:]
    
    # Alternance des équipes dans les poules hautes
    for i in range(len(poule_haute)):
        if i % 2 == 0:
            poule_haute1.append(poule_haute[i])
        else:
            poule_haute2.append(poule_haute[i])
    
    if len(poule_basse) % 2 == 0:
        for i in range(len(poule_basse)):
            if i % 2 == 0:
                poule_basse1.append(poule_basse[i])
            else:
                poule_basse2.append(poule_basse[i])
    else:
        choix_style = input("Voulez-vous faire une seule poule basse (n) ou deux poules basses (y) ? ")
        if choix_style == "y":
            for i in range(len(poule_basse)):
                if i % 2 == 0:
                    poule_basse1.append(poule_basse[i])
                else:
                    poule_basse2.append(poule_basse[i])
            return {"haut1": poule_haute1, "haut2": poule_haute2, "bas1": poule_basse1, "bas2": poule_basse2}
        else:
            poule_basse1 = poule_basse
            return {"haut1": poule_haute1, "haut2": poule_haute2, "bas": poule_basse1}
    
    return {"haut1": poule_haute1, "haut2": poule_haute2, "bas1": poule_basse1, "bas2": poule_basse2}

# Phase 6: Génération des matchs de poules
def generer_matchs_poule(poule):
    return list(combinations(poule, 2))

# Phase 7: Planification des matchs sur les terrains
def planifier_matchs(poules, terrains):
    matchs = []
    for key in poules:
        matchs += generer_matchs_poule(poules[key])
    return [matchs[i::terrains] for i in range(terrains)]

# Phase 8: Estimation du temps total
def calculer_temps_total(n_matchs, duree_match=12, temps_pause=5):
    return (n_matchs * duree_match) + ((n_matchs - 1) * temps_pause)

# Exécution du tournoi
nombre_equipes = 11  # Exemple avec un nombre impair
equipes = generer_equipes(nombre_equipes)
matchs_brassage = generer_matchs_brassage(equipes)

for e1, e2 in matchs_brassage:
    simuler_match(e1, e2)

equipes_classees = classer_equipes(equipes)
poules = repartir_poules(equipes_classees)

matchs_planifies = planifier_matchs(poules, terrains=4)
nombre_total_matchs = sum(len(p) for p in matchs_planifies)
temps_total = calculer_temps_total(nombre_total_matchs)

# Affichage des résultats
print("Classement après brassage:")
for equipe in equipes_classees:
    print(equipe)

print("\nRépartition en poules:")
for niveau, groupe in poules.items():
    print(f"\nTableau {niveau.capitalize()}: {', '.join([e.nom for e in groupe])}")

print(f"\nTemps total estimé: {temps_total} minutes")
