import tkinter as tk
from tkinter import font, messagebox
from typing import NamedTuple
import random
from itertools import cycle

class Joueur(NamedTuple):
    etiquette: str
    couleur: str

class Mouvement(NamedTuple):
    ligne: int
    colonne: int
    etiquette: str = ""

TAILLE_PLATEAU = 3
JOUEURS_PAR_DEFAUT = (
    Joueur(etiquette="X", couleur="blue"),
    Joueur(etiquette="O", couleur="green"),
)

class JeuMorpion:
    def __init__(self, joueurs=JOUEURS_PAR_DEFAUT, taille_plateau=TAILLE_PLATEAU):
        self._joueurs = cycle(joueurs)
        self.taille_plateau = taille_plateau
        self.joueur_actuel = next(self._joueurs)
        self.combinaison_gagnante = []
        self._mouvements_actuels = []
        self._a_un_gagnant = False
        self._combinaisons_gagnantes = []
        self._preparer_plateau()

    def _preparer_plateau(self):
        self._mouvements_actuels = [[Mouvement(ligne, colonne) for colonne in range(self.taille_plateau)] for ligne in range(self.taille_plateau)]
        self._combinaisons_gagnantes = self._obtenir_combinaisons_gagnantes()

    def _obtenir_combinaisons_gagnantes(self):
        lignes = [[(mouvement.ligne, mouvement.colonne) for mouvement in ligne] for ligne in self._mouvements_actuels]
        colonnes = [list(col) for col in zip(*lignes)]
        premiere_diagonale = [ligne[i] for i, ligne in enumerate(lignes)]
        deuxieme_diagonale = [colonne[j] for j, colonne in enumerate(reversed(colonnes))]
        return lignes + colonnes + [premiere_diagonale, deuxieme_diagonale]

    def basculer_joueur(self):
        self.joueur_actuel = next(self._joueurs)

    def est_coup_valide(self, mouvement):
        ligne, colonne = mouvement.ligne, mouvement.colonne
        coup_non_joue = self._mouvements_actuels[ligne][colonne].etiquette == ""
        pas_de_gagnant = not self._a_un_gagnant
        return pas_de_gagnant and coup_non_joue

    def traiter_coup(self, mouvement):
        ligne, colonne = mouvement.ligne, mouvement.colonne
        self._mouvements_actuels[ligne][colonne] = mouvement
        for combinaison in self._combinaisons_gagnantes:
            resultats = set(self._mouvements_actuels[n][m].etiquette for n, m in combinaison)
            est_victoire = (len(resultats) == 1) and ("" not in resultats)
            if est_victoire:
                self._a_un_gagnant = True
                self.combinaison_gagnante = combinaison
                break

    def a_un_gagnant(self):
        return self._a_un_gagnant

    def est_nul(self):
        pas_de_gagnant = not self._a_un_gagnant
        coups_joues = (mouvement.etiquette for ligne in self._mouvements_actuels for mouvement in ligne)
        return pas_de_gagnant and all(coups_joues)

    def reinitialiser_jeu(self):
        for ligne, contenu_ligne in enumerate(self._mouvements_actuels):
            for colonne, _ in enumerate(contenu_ligne):
                contenu_ligne[colonne] = Mouvement(ligne, colonne)
        self._a_un_gagnant = False
        self.combinaison_gagnante = []

    def _choisir_coup_aleatoire(self):
        coups_disponibles = [
            Mouvement(ligne, colonne)
            for ligne in range(self.taille_plateau)
            for colonne in range(self.taille_plateau)
            if self._mouvements_actuels[ligne][colonne].etiquette == ""
        ]
        return random.choice(coups_disponibles)


class PlateauMorpion(tk.Tk):

    def __init__(self, jeu):
        super().__init__()
        self.title("Jeu du Morpion")
        self._cellules = {}
        self._jeu = jeu
        self._creer_menu()
        self._creer_affichage_plateau()
        self._creer_grille_plateau()

    def _creer_menu(self):
        barre_menu = tk.Menu(master=self)
        self.config(menu=barre_menu)
        menu_fichier = tk.Menu(master=barre_menu)
        menu_fichier.add_command(label="Rejouer", command=self.reinitialiser_plateau)
        menu_fichier.add_separator()
        menu_fichier.add_command(label="Quitter", command=quit)
        barre_menu.add_cascade(label="Fichier", menu=menu_fichier)

    def _creer_affichage_plateau(self):
        cadre_affichage = tk.Frame(master=self)
        cadre_affichage.pack(fill=tk.X)
        self.affichage = tk.Label(
            master=cadre_affichage,
            text="Prêt ?",
            font=font.Font(size=28, weight="bold"),
        )
        self.affichage.pack()

    def _creer_grille_plateau(self):
        cadre_grille = tk.Frame(master=self)
        cadre_grille.pack()
        for ligne in range(self._jeu.taille_plateau):
            for colonne in range(self._jeu.taille_plateau):
                bouton = tk.Button(
                    master=cadre_grille,
                    text="",
                    font=font.Font(size=36, weight="bold"),
                    fg="black",
                    width=3,
                    height=2,
                    highlightbackground="blue",
                )
                self._cellules[bouton] = (ligne, colonne)
                bouton.bind("<ButtonPress-1>", self.jouer)
                bouton.grid(row=ligne, column=colonne, padx=5, pady=5, sticky="nsew")

    def jouer(self, evenement):
        bouton_clique = evenement.widget
        ligne, colonne = self._cellules[bouton_clique]
        mouvement = Mouvement(ligne, colonne, self._jeu.joueur_actuel.etiquette)
        if self._jeu.est_coup_valide(mouvement):
            self._mettre_a_jour_bouton(bouton_clique)
            self._jeu.traiter_coup(mouvement)
            if self._jeu.a_un_gagnant():
                self._mettre_en_surbrillance_cellules()
                msg = f'Joueur "{self._jeu.joueur_actuel.etiquette}" a gagné !'
                couleur = self._jeu.joueur_actuel.couleur
                self._mettre_a_jour_affichage(msg, couleur)
                self.demander_rejouer()
            else:
                self._jeu.basculer_joueur()
                msg = f"C'est au tour de {self._jeu.joueur_actuel.etiquette}"
                self._mettre_a_jour_affichage(msg)

    def _mettre_a_jour_bouton(self, bouton_clique):
        bouton_clique.config(text=self._jeu.joueur_actuel.etiquette)
        bouton_clique.config(fg=self._jeu.joueur_actuel.couleur)

    def _mettre_a_jour_affichage(self, msg, couleur="black"):
        self.affichage["text"] = msg
        self.affichage["fg"] = couleur

    def _mettre_en_surbrillance_cellules(self):
        for bouton, coordonnees in self._cellules.items():
            if coordonnees in self._jeu.combinaison_gagnante:
                bouton.config(highlightbackground="red")

    def reinitialiser_plateau(self):
        self._jeu.reinitialiser_jeu()
        self._mettre_a_jour_affichage(msg="Prêt ?")
        for bouton in self._cellules.keys():
            bouton.config(highlightbackground="blue")
            bouton.config(text="")
            bouton.config(fg="black")

    def demander_rejouer(self):
        resultat = messagebox.askyesno("Partie terminée", "Voulez-vous rejouer ?")
        if resultat:
            self.reinitialiser_plateau()
        else:
            self.quit()


def main():
    jeu = JeuMorpion()
    plateau = PlateauMorpion(jeu)
    plateau.mainloop()

if __name__ == "__main__":
    main()
