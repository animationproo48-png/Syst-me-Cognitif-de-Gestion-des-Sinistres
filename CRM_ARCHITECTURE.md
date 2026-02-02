# 🏢 Architecture CRM Production

## 📊 Base de Données Complète

### Schéma PostgreSQL

```sql
-- Table Clients (Assurés)
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    matricule VARCHAR(20) UNIQUE NOT NULL,
    civilite VARCHAR(10),
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    date_naissance DATE,
    email VARCHAR(100),
    telephone VARCHAR(20),
    adresse VARCHAR(255),
    code_postal VARCHAR(10),
    ville VARCHAR(100),
    date_creation TIMESTAMP DEFAULT NOW(),
    date_modification TIMESTAMP DEFAULT NOW(),
    statut VARCHAR(20) DEFAULT 'actif'
);

-- Table Contrats (Polices d'Assurance)
CREATE TABLE contrats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    numero_contrat VARCHAR(50) UNIQUE NOT NULL,
    type_contrat VARCHAR(50), -- 'auto', 'habitation', 'autre'
    date_souscription DATE,
    date_expiration DATE,
    statut VARCHAR(20), -- 'actif', 'suspendu', 'résilié'
    garanties JSONB, -- Liste des garanties actives
    franchise_tiers DECIMAL(10,2),
    franchise_tiers_collision DECIMAL(10,2),
    couverture_dommage_materiel BOOLEAN,
    couverture_tiers BOOLEAN,
    couverture_rc_civile BOOLEAN,
    date_creation TIMESTAMP DEFAULT NOW()
);

-- Table Sinistres (Dossiers)
CREATE TABLE sinistres (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_sinistre VARCHAR(50) UNIQUE NOT NULL,
    client_id UUID REFERENCES clients(id),
    contrat_id UUID REFERENCES contrats(id),
    date_sinistre TIMESTAMP NOT NULL,
    type_sinistre VARCHAR(50), -- 'collision', 'vol', 'incendie', 'dégâts', 'blessure'
    description TEXT,
    lieu VARCHAR(255),
    tiers_implique BOOLEAN,
    nom_tiers VARCHAR(100),
    contact_tiers VARCHAR(20),
    tiers_responsable BOOLEAN,
    constat_amiable BOOLEAN,
    numero_constat VARCHAR(50),
    police_intervenue BOOLEAN,
    numero_proces_verbal VARCHAR(50),
    estimation_dommage DECIMAL(12,2),
    date_estimation DATE,
    photo_urls JSONB, -- URLs des photos/documents
    cci_score SMALLINT, -- 0-100 Claim Complexity Index
    status_dossier VARCHAR(30), -- 'nouveau', 'en_cours', 'expert', 'validation', 'fermé'
    type_traitement VARCHAR(20), -- 'autonome', 'escalade', 'expert'
    conseiller_affecte_id UUID REFERENCES conseillers(id),
    date_creation TIMESTAMP DEFAULT NOW(),
    date_modification TIMESTAMP DEFAULT NOW(),
    date_fermeture TIMESTAMP
);

-- Table Historique Conversation
CREATE TABLE historique_conversation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sinistre_id UUID REFERENCES sinistres(id),
    role VARCHAR(20), -- 'bot', 'user', 'system'
    texte TEXT,
    texte_stt VARCHAR(500), -- Transcription STT brute
    confiance_stt DECIMAL(3,2), -- Confiance du STT (0-1)
    audio_url VARCHAR(255), -- URL du MP3 ElevenLabs
    timestamp TIMESTAMP DEFAULT NOW(),
    metadata JSONB -- Données additionnelles (langue détectée, etc)
);

-- Table Actions Recommandées
CREATE TABLE actions_recommandees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sinistre_id UUID REFERENCES sinistres(id),
    type_action VARCHAR(50), -- 'envoyer_constat', 'expertise', 'paiement', 'info_client'
    description TEXT,
    priorite VARCHAR(20), -- 'haute', 'normale', 'basse'
    statut VARCHAR(20), -- 'en_attente', 'en_cours', 'faite', 'ignorée'
    date_creation TIMESTAMP DEFAULT NOW(),
    date_execution TIMESTAMP
);

-- Table Remboursements
CREATE TABLE remboursements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sinistre_id UUID REFERENCES sinistres(id),
    montant_reclame DECIMAL(12,2),
    montant_accepte DECIMAL(12,2),
    franchise_appliquee DECIMAL(12,2),
    motif_rejet VARCHAR(255),
    date_acceptation TIMESTAMP,
    date_paiement TIMESTAMP,
    moyen_paiement VARCHAR(50), -- 'virement', 'chèque'
    statut VARCHAR(30), -- 'en_attente', 'accepté', 'payé', 'rejeté'
    date_creation TIMESTAMP DEFAULT NOW()
);

-- Table Conseillers
CREATE TABLE conseillers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    telephone VARCHAR(20),
    statut VARCHAR(20), -- 'disponible', 'occupe', 'pause'
    specialite VARCHAR(100), -- 'sinistre_complexe', 'réclamation', 'info_contrat'
    nb_dossiers_actifs INT DEFAULT 0,
    date_creation TIMESTAMP DEFAULT NOW()
);

-- Index pour optimisation
CREATE INDEX idx_sinistres_client ON sinistres(client_id);
CREATE INDEX idx_sinistres_status ON sinistres(status_dossier);
CREATE INDEX idx_sinistres_cci ON sinistres(cci_score);
CREATE INDEX idx_conversation_sinistre ON historique_conversation(sinistre_id);
CREATE INDEX idx_remboursement_sinistre ON remboursements(sinistre_id);
CREATE INDEX idx_clients_matricule ON clients(matricule);
```

---

## 🔄 Flux Conversationnel Amélioré

### Étape 1: Authentification par Matricule
```
BOT: "Bonjour et bienvenue! Pour vous aider rapidement, 
      pouvez-vous me donner votre numéro de matricule SVP?"

USER: "XX-123-XX"

SYSTÈME:
- Vérifie matricule en BDD
- Charge: client, contrats, historique sinistres
- Prépare contextuel conversation
```

### Étape 2: Identification Client
```
BOT: "Merci! Vous êtes bien [Nom Prénom]? 
      Numéro de contrat: [XXXX], 
      assuré depuis [date]?"

USER: "Oui, c'est bien moi"

Exemples de confirmations possibles:
- "Oui, c'est moi."
- "Oui, c'est bien moi."
- "Oui, c'est exact."
- "Oui, tout à fait."
- "Oui, c'est bien mon contrat."
- "Oui, vous avez la bonne personne."
- "Oui, je confirme."
- "Oui, c'est correct."
- "Exactement."

SYSTÈME:
- Confirme identité
- Vérifie contrat actif
- Prépare questions basées sur type sinistre
```

### Étape 3: Description du Sinistre
```
BOT: "Pouvez-vous m'expliquer brièvement ce qui s'est passé?"

USER: "J'étais arrêté au feu rouge, une voiture m'a percuté par l'arrière"

SYSTÈME:
- STT + classification automatique type sinistre
- Commence analyse cognitive
- Extrait entités (date, lieu, tiers)
```

### Étape 4: Questions Contextuelles
```
BOT: "Y a-t-il des blessés ou douleurs?"
BOT: "Constat amiable rempli?"
BOT: "Police intervenue?"
BOT: "Photos/documents disponibles?"

SYSTÈME:
- Chaque réponse augmente CCI ou la complétude
- Construit dossier progressivement
```

### Étape 5: Décision Autonome vs Escalade
```
Si CCI < 40:
  BOT AUTONOME: "Votre cas peut être traité automatiquement.
                 Merci de nous envoyer le constat et les photos.
                 Un garage agréé vous sera proposé sous 24h."

Si CCI > 60:
  BOT ESCALADE: "Ce sinistre nécessite une attention particulière.
                 Je vais vous transférer à un conseiller spécialisé
                 pour une meilleure prise en charge. 
                 Un moment s'il vous plaît..."
                 
  [Audio feedback naturel via ElevenLabs]
  [Transfert WebSocket vers conseiller]
```

---

## 📱 API REST CRUD

### Endpoints Clients
```
GET    /api/v1/clients/:matricule          # Récupérer client
POST   /api/v1/clients                      # Créer client
PUT    /api/v1/clients/:id                  # Modifier client
DELETE /api/v1/clients/:id                  # Supprimer client (RGPD)
```

### Endpoints Sinistres
```
GET    /api/v1/sinistres/:id                # Détail dossier
POST   /api/v1/sinistres                    # Créer sinistre
PUT    /api/v1/sinistres/:id                # Mettre à jour
DELETE /api/v1/sinistres/:id                # Archiver

GET    /api/v1/sinistres?client_id=X        # Tous dossiers client
GET    /api/v1/sinistres?status=en_cours    # Filtrer par statut
GET    /api/v1/sinistres?cci=60,100         # Filtrer par complexité
```

### Endpoints Conversation
```
POST   /api/v1/sinistres/:id/conversation   # Ajouter message
GET    /api/v1/sinistres/:id/historique     # Récupérer historique
```

### Endpoints Remboursement
```
GET    /api/v1/remboursements/:sinistre_id  # État remboursement
POST   /api/v1/remboursements               # Créer remboursement
PUT    /api/v1/remboursements/:id           # Mettre à jour
```

### Endpoints Escalade
```
POST   /api/v1/escalade/:sinistre_id        # Escalader cas
GET    /api/v1/escalade/queue               # Queue d'attente
PUT    /api/v1/escalade/:id/assigner        # Assigner à conseiller
```

---

## 🤖 Conversation Manager Amélioré

### Phases

```python
class ConversationPhase(Enum):
    AUTHENTIFICATION = "auth"           # Matricule + confirmation
    DESCRIPTION = "description"          # Qu'est-il arrivé?
    SINISTRE_DETAILS = "sinistre_details"  # Y a-t-il blessés?
    CONSTAT = "constat"                # Constat rempli?
    DOCUMENTS = "documents"             # Photos/pièces justificatives
    DECISION = "decision"              # Autonome ou escalade
    TRANSFERT = "transfert"            # Vers conseiller si escalade
    SUIVI = "suivi"                    # Questions sur dossier existant
```

### Contexte Persistant

```json
{
  "sinistre_id": "uuid",
  "client_id": "uuid",
  "phase_actuelle": "description",
  "data_collectee": {
    "matricule": "XX-123-XX",
    "nom": "Dupont",
    "type_sinistre": "collision",
    "date_sinistre": "2026-02-02T14:30:00Z",
    "blessures": true,
    "constat_amiable": true,
    "cci_score": 45,
    "decision": "autonome"
  },
  "messages": [
    {"role": "bot", "texte": "Bonjour..."},
    {"role": "user", "texte": "Oui j'ai eu un accident..."}
  ]
}
```

---

## 📊 Suivi de Dossier

### États du Dossier
```
NOUVEAU           → Créé à l'instant
EN_COURS          → En traitement automatique
EXPERT            → En attente expertise
VALIDATION        → En validation avant paiement
FERMÉ             → Traité et fermé
ESCALADE          → En attente conseiller
EN_ATTENTE_CLIENT → Attend documents de client
```

### Actions Affichables
- ✅ Documents reçus
- 🔄 Expertise en cours
- 💰 Montant validé
- 📅 Rendez-vous garage prévu
- 📧 Courrier envoyé
- 🔔 Alerte (délai dépassé, info manquante)

---

## 🎯 Système d'Escalade

### Triggers Automatiques
```
CCI > 60           → Escalade
Blessures          → Escalade
Tiers responsable  → Escalade
Documents manquants → Alerte (pas escalade)
Délai > 5 jours    → Escalade
```

### Flux Escalade
```
1. Détection trigger CCI/règles
2. Audio feedback: "Je vais transférer..."
3. Recherche conseiller disponible
4. Assignation sinistre
5. Transfert WebSocket
6. Conseiller reçoit contexte complet
7. Historique conversation accessible
```

---

## 🔐 Sécurité

- ✅ Authentification matricule + PIN optionnel
- ✅ Chiffrement données sensibles (RGPD)
- ✅ Audit complet (qui a changé quoi, quand)
- ✅ Masquage numéros sensibles en logs
- ✅ Rate limiting (prévention brute-force)

