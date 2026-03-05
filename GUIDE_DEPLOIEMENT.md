# 🚀 Guide de déploiement — Simulateur Jeanbrun

## Ce que vous allez obtenir

Une URL sécurisée (ex : `https://jeanbrun-sim.streamlit.app`) accessible uniquement
avec un mot de passe, hébergée **gratuitement** sur Streamlit Cloud.

---

## ÉTAPE 1 — Préparer votre dossier de fichiers

Votre dossier `jeanbrun-app` doit contenir exactement :

```
jeanbrun-app/
├── app.py                          ← le code de l'application
├── requirements.txt                ← dépendances Python
├── packages.txt                    ← LibreOffice (recalcul des formules)
├── .gitignore                      ← sécurité (exclut le mot de passe)
├── Simulation_JEANBRUN_V9.xlsx     ← votre fichier Excel de référence
└── .streamlit/
    └── config.toml                 ← thème couleurs
    (secrets.toml NE va PAS sur GitHub)
```

---

## ÉTAPE 2 — Créer un dépôt GitHub

1. Allez sur **https://github.com** et connectez-vous
2. Cliquez sur le bouton vert **"New"** (ou **"+ → New repository"**)
3. **Repository name** : `simulateur-jeanbrun` (ou autre nom de votre choix)
4. Laissez sur **Private** (votre code ne sera pas public)
5. Cliquez **"Create repository"**
6. GitHub vous montre une page vide avec des instructions

---

## ÉTAPE 3 — Envoyer les fichiers sur GitHub

### Option A — Interface web (la plus simple, sans code)

1. Sur la page de votre nouveau dépôt GitHub, cliquez **"uploading an existing file"**
2. Glissez-déposez **tous les fichiers** du dossier `jeanbrun-app` :
   - `app.py`
   - `requirements.txt`
   - `packages.txt`
   - `.gitignore`
   - `Simulation_JEANBRUN_V9.xlsx`
   - Le dossier `.streamlit/config.toml`
   
   ⚠️ **Ne déposez PAS** le fichier `secrets.toml` !

3. En bas, dans "Commit changes", tapez : `Premier déploiement simulateur Jeanbrun`
4. Cliquez **"Commit changes"**

### Option B — GitHub Desktop (recommandé pour les mises à jour futures)

1. Téléchargez **GitHub Desktop** : https://desktop.github.com
2. Connectez-vous avec votre compte GitHub
3. **File → Add Local Repository** → sélectionnez votre dossier `jeanbrun-app`
4. Cliquez **"Publish repository"** → choisissez votre dépôt `simulateur-jeanbrun`
5. Cochez **"Keep this code private"** → **Publish**

---

## ÉTAPE 4 — Déployer sur Streamlit Cloud

1. Allez sur **https://share.streamlit.io** et connectez-vous avec votre compte GitHub
2. Cliquez **"New app"**
3. Remplissez :
   - **Repository** : sélectionnez `simulateur-jeanbrun`
   - **Branch** : `main`
   - **Main file path** : `app.py`
4. Cliquez **"Advanced settings"** → section **"Secrets"**
5. Collez exactement ceci (en remplaçant votre mot de passe) :
   ```toml
   password = "MonMotDePasseConseiller2025"
   ```
6. Cliquez **"Save"** puis **"Deploy!"**

⏳ Le déploiement prend **5-10 minutes** (installation de LibreOffice).
Une URL vous est fournie immédiatement, ex : `https://simulateur-jeanbrun.streamlit.app`

---

## ÉTAPE 5 — Tester et partager

1. Ouvrez votre URL
2. Entrez le mot de passe défini à l'étape 4
3. Renseignez des hypothèses et cliquez **"Lancer la simulation"**
4. Partagez l'URL et le mot de passe à vos conseillers

---

## MISES À JOUR — Version suivante du fichier Excel

Quand vous recevrez une V10 ou V11 du simulateur Excel :

### Avec GitHub Desktop :
1. Remplacez `Simulation_JEANBRUN_V9.xlsx` par le nouveau fichier
   (en le renommant `Simulation_JEANBRUN_V9.xlsx` OU en modifiant `app.py`
   ligne : `TEMPLATE = Path("Simulation_JEANBRUN_V9.xlsx")`)
2. Dans GitHub Desktop, vous verrez le fichier modifié
3. Tapez un message de commit : `Mise à jour vers V10`
4. Cliquez **"Commit to main"** puis **"Push origin"**
5. Streamlit Cloud se redéploie automatiquement en 2-3 minutes ✅

### Avec l'interface web GitHub :
1. Sur votre dépôt, cliquez sur le fichier Excel existant
2. Cliquez l'icône crayon (Edit) → puis **"Delete file"** → committez
3. Sur le dépôt principal, cliquez **"Add file → Upload files"**
4. Déposez le nouveau fichier Excel → committez

---

## CHANGER LE MOT DE PASSE

1. Sur https://share.streamlit.io, ouvrez votre app
2. Cliquez sur les **3 points (⋮)** → **"Settings"**
3. Section **"Secrets"** → modifiez la ligne `password = "..."`
4. **"Save"** → l'app redémarre automatiquement

---

## AJOUTER DES CONSEILLERS

Chaque conseiller reçoit simplement :
- L'URL : `https://votre-nom.streamlit.app`
- Le mot de passe

Tous partagent la même instance — c'est suffisant pour des simulations
(chaque calcul est indépendant et non sauvegardé).

---

## RÉSOLUTION DE PROBLÈMES FRÉQUENTS

| Problème | Solution |
|----------|----------|
| "Streamlit error" au démarrage | Vérifiez que `packages.txt` contient `libreoffice` |
| "FileNotFoundError" | Vérifiez que `Simulation_JEANBRUN_V9.xlsx` est bien dans le dépôt |
| Calcul toujours les mêmes valeurs | Streamlit met les résultats en cache — ajoutez `?v=2` à l'URL |
| Mot de passe incorrect | Vérifiez les "Secrets" dans les settings Streamlit Cloud |
| Timeout après 90s | Streamlit Cloud est lent parfois — relancez la simulation |

---

## ARCHITECTURE TECHNIQUE

```
Conseiller (navigateur)
       ↓ URL + mot de passe
Streamlit Cloud (serveur gratuit)
       ↓ remplit les cellules bleues
openpyxl → template Excel V9
       ↓ recalcule toutes les formules
LibreOffice headless (installé automatiquement)
       ↓ lit les valeurs calculées
Résultats affichés dans les 4 onglets
```

**Coût** : 0 € (Streamlit Cloud Free tier)
**Limite** : 1 Go RAM, mise en veille après 7 jours sans visite (redémarre automatiquement)

---

*Guide rédigé pour Bertrand — Mai 2025*
