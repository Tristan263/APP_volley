import random
from itertools import combinations

class Equipe:
    def __init__(self, nom):
        self.nom = nom
        self.points = 0
        self.points_marques = 0
        self.points_encaisse = 0
        self.matchs_joues = 0  # Ajout d'un compteur de matchs joués

    def ajouter_resultat(self, points_marques, points_encaisse, victoire, compte=True):
        self.points_marques += points_marques
        self.points_encaisse += points_encaisse
        if compte:
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
    
    # Si le nombre d'équipes est impair, ajouter 2 matchs à l'équipe qui n'a pas joué
    if len(equipes) % 2 == 1:
        equipes_sans_match = [e for e in equipes if matchs_par_equipe[e.nom] == 0]
        if equipes_sans_match:  # Vérifier qu'il y a bien une équipe sans match
            equipe_non_jouee = equipes_sans_match[0]  # Prendre la première équipe sans match
            adversaires = random.sample([e for e in equipes if matchs_par_equipe[e.nom] == 2], 2)
            for adversaire in adversaires:
                matchs.append((equipe_non_jouee, adversaire))
                matchs_par_equipe[equipe_non_jouee.nom] += 1
                matchs_par_equipe[adversaire.nom] += 1
                
    return matchs

# Phase 3: Simuler les résultats des matchs
def simuler_match(equipe1, equipe2, compte=True):
    score1, score2 = random.randint(10, 25), random.randint(10, 25)
    while score1 == score2:
        score2 = random.randint(10, 25)
    
    victoire_e1 = score1 > score2
    equipe1.ajouter_resultat(score1, score2, victoire_e1, compte)
    equipe2.ajouter_resultat(score2, score1, not victoire_e1, compte)
    return equipe1.nom, score1, equipe2.nom, score2, compte

# Phase 4: Classer les équipes avec critères de départage
def classer_equipes(equipes):
    return sorted(equipes, key=lambda x: (-x.points, -x.quotient_points(), -x.difference_points(), random.random()))

# Exécution du tournoi
nombre_equipes = 11  # Exemple avec un nombre impair
equipes = generer_equipes(nombre_equipes)
matchs_brassage = generer_matchs_brassage(equipes)

print("\nMatchs de brassage:")
matchs_joues = []
for e1, e2 in matchs_brassage:
    match_info = simuler_match(e1, e2, compte=(e1.matchs_joues < 2 or e2.matchs_joues < 2))
    matchs_joues.append(match_info)
    status = "(Comptabilisé)" if match_info[4] else "(Ne compte pas)"
    print(f"{match_info[0]} {match_info[1]} - {match_info[3]} {match_info[2]} {status}")

# Vérification du nombre de matchs
total_matchs = len(matchs_brassage)
print(f"\nNombre total de matchs: {total_matchs} (Attendu: {nombre_equipes + 2} si impair)")

# Classement après les matchs
equipes_classees = classer_equipes(equipes)

print("\nClassement après brassage:")
for equipe in equipes_classees:
    print(equipe)
