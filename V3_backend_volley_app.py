#questions : Faut il mélanger les équipes au moment des sous-poules ? car actuellement c'est simplement dans l'ordre du classement 
# Faut il être égaux parfaitement sur les arbitrages ? 
# Trouver un système équilibré de répartition des terrains selons les sous-poules actuellement problème de logique il attribue
#un terrain par principe sans partager les ressources
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

    print(f"\n📊 Répartition des poules :")
    print(f"Poule haute : {len(poule_haute)} équipes")
    print(f"Poule basse : {len(poule_basse)} équipes")

    print("\n🏆 Poule haute :")
    for equipe in poule_haute:
        print(equipe)

    print("\n⚙️ Poule basse :")
    for equipe in poule_basse:
        print(equipe)

    return poule_haute, poule_basse

def diviser_en_sous_poules(poule, nom):
    taille = len(poule)
    moitie = taille // 2
    if taille % 2 == 0:
        return (poule[:moitie], poule[moitie:])
    else:
        return (poule, [])  # ne pas diviser si impair
    
def matchs_poules(sous_poules):
    matchs = []
    # Pour chaque sous-poule, générer tous les matchs possibles
    for sous_poule in sous_poules:
        for i in range(len(sous_poule)):
            for j in range(i + 1, len(sous_poule)):
                matchs.append((sous_poule[i], sous_poule[j]))
    return matchs

def melanger_matchs(matchs):
    # Mélanger les matchs pour ne pas que les équipes jouent à la suite
    random.shuffle(matchs)
    return matchs

def attribuer_terrains_par_sous_poule(sous_poules, nb_terrains):
    total_equipes = sum(len(poule) for poule in sous_poules)
    total_matchs = sum(len(matchs_poules([poule])) for poule in sous_poules)
    
    terrains_par_sous_poule = {}
    series_par_sous_poule = {}

    # Calculer le nombre de séries et le coefficient d'importance pour chaque sous-poule
    for index, sous_poule in enumerate(sous_poules):
        nb_equipes = len(sous_poule)
        nb_matchs = len(matchs_poules([sous_poule]))  # Nombre de matchs dans la sous-poule
        coefficient = nb_equipes / total_equipes  # Coefficient basé sur le nombre d'équipes
        
        # Calculer le nombre de séries (matchs divisés par le nombre de terrains)
        series = (nb_matchs + nb_terrains - 1) // nb_terrains  # Arrondi vers le haut
        series_par_sous_poule[index] = series
        
        # Calculer le nombre de terrains à attribuer
        terrains = round(coefficient * nb_terrains)  # Nombre de terrains basé sur le coefficient
        terrains_par_sous_poule[index] = terrains

    # Rééquilibrer les terrains pour que leur somme soit égale à nb_terrains
    total_attribue = sum(terrains_par_sous_poule.values())
    if total_attribue != nb_terrains:
        diff = nb_terrains - total_attribue
        for index in terrains_par_sous_poule:
            if diff > 0:
                terrains_par_sous_poule[index] += 1
                diff -= 1
            elif diff < 0:
                terrains_par_sous_poule[index] -= 1
                diff += 1

    return terrains_par_sous_poule, series_par_sous_poule



# --- EXÉCUTION DU TOURNOI ---
if __name__ == "__main__":
    random.seed()
    nombre_equipes = 11
    nb_terrains = 3

    equipes = generer_equipes(nombre_equipes)
    match_infos, arbitrages = generer_matchs_brassage(equipes, nb_terrains)

    print("\nMatchs de brassage (avec terrain et arbitre) :")
    for info in match_infos:
        e1, e2, mode = info["match"]
        nom1, s1, nom2, s2, m = simuler_match(e1, e2, mode)
        arbitre_txt = f" | Arbitre : {info['arbitre'].nom}" if info["arbitre"] else " | Aucun arbitre"
        type_txt = "(Comptabilisé)" if mode == "officiel" else f"(Seuls les points de {nom1} comptent)"
        print(f"[Série {info['serie']}] Terrain {info['terrain']} : {nom1} {s1} - {s2} {nom2} {type_txt}{arbitre_txt}")

    print("\nRésumé arbitrage par équipe :")
    for nom, count in arbitrages.items():
        print(f"{nom} : {count} arbitrage(s)")

    manquants = [nom for nom, count in arbitrages.items() if count == 0]
    if manquants:
        print("\n⚠️ Attention : les équipes suivantes n'ont jamais arbitré :")
        for nom in manquants:
            print(f"❌ {nom}")
    else:
        print("\n✅ Toutes les équipes ont arbitré au moins une fois.")

    print("\nClassement après brassage :")
    equipes_classees = classer_equipes(equipes)
    for equipe in equipes_classees:
        print(equipe)

    # Phase 3 : Création des poules
    poule_haute, poule_basse = creer_poules_depuis_classement(equipes_classees)

    # Phase 4 : Division en sous-poules
    sous_poule_H1, sous_poule_H2 = diviser_en_sous_poules(poule_haute, "Haute")
    sous_poule_B1, sous_poule_B2 = diviser_en_sous_poules(poule_basse, "Basse")

    print("\n🔷 Sous-poules Haute")
    print("H1:")
    for equipe in sous_poule_H1:
        print(f" - {equipe.nom}")
    print("H2:")
    for equipe in sous_poule_H2:
        print(f" - {equipe.nom}")

    if sous_poule_B2:
        print("\n🔶 Sous-poules Basse")
        print("B1:")
        for equipe in sous_poule_B1:
            print(f" - {equipe.nom}")
        print("B2:")
        for equipe in sous_poule_B2:
            print(f" - {equipe.nom}")
    else:
        print("\n🔶 Poule basse non divisée (nombre impair)")
        for equipe in sous_poule_B1:
            print(f" - {equipe.nom}")

# Phase 5 : Génération des matchs

# Générer les matchs pour chaque sous-poule
matchs_H1 = matchs_poules([sous_poule_H1])
matchs_H2 = matchs_poules([sous_poule_H2])
if sous_poule_B2:
    matchs_B1 = matchs_poules([sous_poule_B1])
    matchs_B2 = matchs_poules([sous_poule_B2])
else:
    matchs_B1 = matchs_poules([sous_poule_B1])

# Mélanger les matchs pour chaque sous-poule
matchs_H1 = melanger_matchs(matchs_H1)
matchs_H2 = melanger_matchs(matchs_H2)
if sous_poule_B2:
    matchs_B1 = melanger_matchs(matchs_B1)
    matchs_B2 = melanger_matchs(matchs_B2)
else:
    matchs_B1 = melanger_matchs(matchs_B1)

# Afficher les matchs mélangés pour chaque sous-poule
print("\n🔷 Matchs sous-poule H1 :")
for match in matchs_H1:
    print(f"{match[0].nom} vs {match[1].nom}")

print("\n🔷 Matchs sous-poule H2 :")
for match in matchs_H2:
    print(f"{match[0].nom} vs {match[1].nom}")

if sous_poule_B2:
    print("\n🔶 Matchs sous-poule B1 :")
    for match in matchs_B1:
        print(f"{match[0].nom} vs {match[1].nom}")

    print("\n🔶 Matchs sous-poule B2 :")
    for match in matchs_B2:
        print(f"{match[0].nom} vs {match[1].nom}")
else:
    print("\n🔶 Matchs poule B1 :")
    for match in matchs_B1:
        print(f"{match[0].nom} vs {match[1].nom}")


sous_poules = [sous_poule_H1, sous_poule_H2, sous_poule_B1, sous_poule_B2]
    
terrains_attribues, series_par_sous_poule = attribuer_terrains_par_sous_poule(sous_poules, nb_terrains)

# Affichage des résultats
print("\n🎯 Attribution des terrains par sous-poule :")
for i, terrains in terrains_attribues.items():
    print(f"Sous-poule {i + 1} : {terrains} terrain(s), séries nécessaires : {series_par_sous_poule[i]}")
