# Microsoft Security Incident Prediction — README del Dataset

> **GUIDE**: Generalized User Incident Detection and Evaluation
>
Fonte: [Kaggle — Microsoft Security Incident Prediction](https://www.kaggle.com/datasets/Microsoft/microsoft-security-incident-prediction/data)
> Pubblicato da: Microsoft Research

---

## Indice

1. [Panoramica](#1-panoramica)
2. [Struttura del Dataset](#2-struttura-del-dataset)
3. [Dizionario dei Dati](#3-dizionario-dei-dati)
4. [Come il Dataset viene Utilizzato per Modello](#4-come-il-dataset-viene-utilizzato-per-modello)
5. [Privacy e Anonimizzazione dei Dati](#5-privacy-e-anonimizzazione-dei-dati)

---

## 1. Panoramica

### Cos'è questo dataset?

GUIDE è un dataset di cybersecurity del mondo reale raccolto da Microsoft dalla sua piattaforma **Defender XDR** (Extended Detection and Response) — il prodotto di sicurezza distribuito in migliaia di aziende in tutto il mondo.

In un periodo di due settimane, Microsoft ha registrato ogni evento di sicurezza rilevato in **oltre 6.100 organizzazioni**, catturando più di **13 milioni di singoli elementi di prova** organizzati in **1,6 milioni di avvisi** e **1 milione di incidenti**. Ogni incidente è stato esaminato da un analista di sicurezza umano che ha assegnato un'etichetta di triage.

### Perché esiste questo dataset?

I team di sicurezza ricevono migliaia di avvisi di sicurezza ogni giorno. La stragrande maggioranza sono falsi allarmi. Gli analisti perdono enormi quantità di tempo a investigare minacce inesistenti. Questo dataset è stato creato per addestrare modelli di machine learning in grado di classificare automaticamente se un avviso è una minaccia reale — aiutando gli analisti a concentrarsi solo su ciò che conta.

### Cosa lo rende insolito?

Sia la suddivisione di training che quella di test contengono l'insieme completo delle colonne, **inclusa la colonna target `IncidentGrade`**. Questo è insolito nei dataset di Kaggle. Significa che il set di test può essere utilizzato per una corretta valutazione finale di benchmark invece che solo per il punteggio di sottomissione.

### Dimensioni a colpo d'occhio

| Metrica                           | Valore           |
|-----------------------------------|------------------|
| Dimensione file di training       | ~2 GB            |
| Dimensione file di test           | ~1 GB            |
| Record totali di prove (train)    | ~13 milioni di righe |
| Incidenti totali                  | ~1 milione       |
| Avvisi totali                     | ~1,6 milioni     |
| Organizzazioni rappresentate      | 6.100+           |
| Tecniche MITRE ATT&CK coperte     | 441              |
| Tipi di entità                    | 33               |
| Finestra di osservazione          | 2 settimane      |

---

## 2. Struttura del Dataset

### La gerarchia a tre livelli

Ogni **riga nel CSV è un elemento di prova (evidence)**. L'elemento di prova è l'unità più granulare. Più elementi di prova sono raggruppati in un avviso, e più avvisi sono raggruppati in un incidente.

```
Incident  (1 row per incident — identified by IncidentId)
  └── Alert  (1 or more alerts per incident — identified by AlertId)
        └── Evidence  (1 or more evidence rows per alert — each CSV row)
                └── Entity  (the object involved: a file, an IP, a user...)
```

Poiché un singolo incidente può coinvolgere molte entità attraverso molti avvisi, **lo stesso IncidentId e IncidentGrade si ripetono in più righe**. Questo è voluto — l'etichetta è assegnata a livello di incidente e propagata a ogni riga di prova appartenente a quell'incidente.

### Suddivisione Train vs Test

| Caratteristica              | Train                        | Test                              |
|-----------------------------|------------------------------|-----------------------------------|
| Righe approssimative        | ~13 milioni                  | ~6 milioni                        |
| Contiene `IncidentGrade`    | Sì                           | Sì                                |
| Contiene colonna `Usage`    | No                           | Sì                                |
| Utilizzo consigliato        | Tutte le fasi di sviluppo (2–4) | Solo valutazione finale (Fase 4.3) |

La colonna `Usage` appare solo nel set di test. Indica come ogni riga doveva essere utilizzata nella partizione originale del benchmark di Kaggle.

---

## 3. Dizionario dei Dati

Le colonne sono raggruppate per il loro ruolo semantico. Il **tipo di archiviazione** riflette come pandas legge la colonna dopo la codifica delle etichette applicata da Microsoft — la maggior parte degli identificatori e delle proprietà delle entità sono memorizzati come interi codificati (`BIGINT`), non come stringhe grezze.

### 3.1 Identificatori Strutturali

Queste colonne definiscono la gerarchia. **Non sono caratteristiche (features)** per la modellazione — sono chiavi per raggruppare e unire.

| # | Colonna       | Tipo   | Descrizione                                                                                                                                |
|---|---------------|--------|--------------------------------------------------------------------------------------------------------------------------------------------|
| 0 | `Id`          | BIGINT | La colonna 'Id' è stata identificata come chiave surrogata (surrogate key) risultante dalla concatenazione di OrgId e IncidentId. Poiché garantisce l'unicità di ogni record (1:1), essa non fornisce alcun potere predittivo ai modelli di apprendimento automatico e viene rimossa in fase di pre-processing per evitare il rischio di overfitting |
| 1 | `OrgId`       | BIGINT | Identificatore codificato dell'organizzazione cliente. Utile come caratteristica di raggruppamento — diverse organizzazioni hanno diverse baseline di sicurezza. |
| 2 | `IncidentId`  | BIGINT | Raggruppa tutte le righe di prova che appartengono allo stesso incidente. Usare come chiave di groupby per calcolare caratteristiche aggregate a livello di incidente. |
| 3 | `AlertId`     | BIGINT | Raggruppa tutte le righe di prova che appartengono allo stesso avviso all'interno di un incidente. |

### 3.2 Temporali

| # | Colonna      | Tipo                     | Descrizione                                                                                                                                                                                                                            |
|---|--------------|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 4 | `Timestamp`  | TIMESTAMP WITH TIME ZONE | Data e ora in cui l'avviso è stato creato dal rilevatore XDR. Formato: ISO 8601 con offset del fuso orario (es. `2024-06-10 15:30:56+02:00`). Utilizzato per analisi di serie temporali e per estrarre caratteristiche temporali (ora del giorno, giorno della settimana). |

### 3.3 Metadati di Rilevamento

Queste colonne descrivono cosa ha rilevato il sistema automatizzato e come ha classificato la minaccia.

| # | Colonna            | Tipo    | Descrizione                                                                                                                                                                                                                                                                     |
|---|--------------------|---------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 5 | `DetectorId`       | BIGINT  | Identificatore codificato della regola di rilevamento o del modello ML all'interno di Defender XDR che ha attivato questo avviso. Diversi rilevatori hanno tassi di falsi positivi molto diversi.                                                                               |
| 6 | `AlertTitle`       | BIGINT  | Titolo codificato dell'avviso (es. "Esecuzione sospetta di PowerShell", "Documento macro ha avviato un processo figlio"). Altamente predittivo — descrive direttamente il pattern di minaccia rilevato.                                                                       |
| 7 | `Category`         | VARCHAR | Fase di attacco di alto livello dal framework MITRE ATT&CK. I valori includono: `InitialAccess`, `Execution`, `Persistence`, `PrivilegeEscalation`, `DefenseEvasion`, `CredentialAccess`, `Discovery`, `LateralMovement`, `Collection`, `Exfiltration`, `CommandAndControl`, `Impact`. |
| 8 | `MitreTechniques`  | VARCHAR | Tecnica/e MITRE ATT&CK specifica/e coinvolta/e, separate da punto e virgola (es. `T1078;T1078.004`). Più granulare di Category. Un singolo avviso può coinvolgere più tecniche.                                                                                               |

### 3.4 Variabili Target

Queste sono le etichette assegnate dagli analisti SOC umani. Sono gli **output** che i modelli imparano a predire.

| #  | Colonna           | Tipo    | Descrizione                                                                                                                                                                                                                                                                                           |
|----|-------------------|---------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 9  | `IncidentGrade`   | VARCHAR | **Variabile target primaria.** La decisione di triage presa dall'analista umano dopo aver investigato l'incidente. Tre valori possibili: `TruePositive` (minaccia reale confermata), `BenignPositive` (attività reale ma non malevola — informativa), `FalsePositive` (rilevamento errato — non una minaccia). |
| 10 | `ActionGrouped`   | VARCHAR | **Variabile target secondaria.** Azione di remediation di alto livello intrapresa dall'analista. I valori includono: `None`, `Block`, `Isolate`, `Quarantine`, `Terminate`. Disponibile solo per ~26.000 incidenti (sottoinsieme di quelli con etichette di triage).                                   |
| 11 | `ActionGranular`  | VARCHAR | **Variabile target secondaria (dettagliata).** Versione granulare di ActionGrouped. Descrive l'azione specifica eseguita (es. `BlockFile`, `IsolateDevice`, `QuarantineEmail`).                                                                                                                       |

### 3.5 Descrizione dell'Entità

Un'entità è l'oggetto specifico coinvolto nell'evento di sicurezza. `EntityType` definisce il tipo di oggetto, e `EvidenceRole` definisce il ruolo che ha svolto nell'avviso.

| #  | Colonna         | Tipo    | Descrizione                                                                                                                                                                                                                                                                                               |
|----|-----------------|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 12 | `EntityType`    | VARCHAR | Tipo di oggetto che è il soggetto di questa riga di prova. Uno di 33 possibili valori. Valori comuni: `Process`, `File`, `Ip`, `Url`, `User`, `Device`, `MailMessage`, `MailBox`, `MailCluster`, `RegistryKey`, `CloudLogonSession`, `CloudLogonRequest`, `CloudApplication`, `OAuthApplication`, `Account`. |
| 13 | `EvidenceRole`  | VARCHAR | Ruolo che questa entità ha svolto nell'avviso. Valori: `Attacker` (l'entità che compie l'azione malevola), `Victim` (l'entità presa di mira), `Related` (entità contestuale — né attaccante né vittima diretta), `Impacted` (colpita dall'attacco).                                                         |

### 3.6 Proprietà dell'Entità — Dispositivo e Endpoint

Queste colonne sono popolate quando `EntityType` è `Device`, `Process` o `File`. Sono `null` (codificate come 0 o NaN) per altri tipi di entità.

| #  | Colonna       | Tipo   | Descrizione                                                                                                                                                    |
|----|---------------|--------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 14 | `DeviceId`    | BIGINT | Identificatore codificato della macchina (endpoint) coinvolta.                                                                                                 |
| 15 | `Sha256`      | BIGINT | Hash crittografico SHA-256 codificato del file coinvolto. Utilizzato per identificare file malevoli rispetto ai database di intelligence sulle minacce noti.  |
| 32 | `FileName`    | BIGINT | Nome codificato del file coinvolto (es. `invoice.docm`, `payload.exe`).                                                                                        |
| 33 | `FolderPath`  | BIGINT | Percorso directory completo codificato del file (es. `C:\Users\jsmith\AppData\Temp\`). Percorsi sospetti come `Temp` o `AppData` sono indicatori comuni di compromissione. |
| 22 | `DeviceName`  | BIGINT | Nome host codificato della macchina (es. `DESKTOP-A4F2`).                                                                                                      |
| 37 | `OSFamily`    | BIGINT | Famiglia di sistema operativo codificata del dispositivo (es. Windows, Linux, macOS).                                                                          |
| 38 | `OSVersion`   | BIGINT | Versione del sistema operativo codificata. Versioni non aggiornate sono correlate a un rischio più elevato.                                                    |

### 3.7 Proprietà dell'Entità — Rete

Popolate quando `EntityType` è `Ip`, `Url` o `NetworkConnection`.

| #  | Colonna             | Tipo   | Descrizione                                                                                                                                                                         |
|----|---------------------|--------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 16 | `IpAddress`         | BIGINT | Indirizzo IP codificato coinvolto nell'evento (sorgente o destinazione).                                                                                                            |
| 17 | `Url`               | BIGINT | URL codificato contattato dal dispositivo. URL sospetti includono domini registrati di recente, domini typosquatted (es. `micosoft.com`) e indirizzi C2 (command-and-control) noti. |
| 23 | `NetworkMessageId`  | BIGINT | Identificatore codificato per un messaggio di rete — collega eventi di rete a eventi email che coinvolgono lo stesso messaggio.                                                     |
| 42 | `CountryCode`       | BIGINT | Paese di origine codificato dell'indirizzo IP. Anomalie geografiche (es. login da un paese inaspettato) sono segnali forti.                                                          |
| 43 | `State`             | BIGINT | Stato/regione di origine codificato.                                                                                                                                                 |
| 44 | `City`              | BIGINT | Città di origine codificata.                                                                                                                                                         |

### 3.8 Proprietà dell'Entità — Identità e Account

Popolate quando `EntityType` è `User`, `Account` o `CloudLogonSession`.

| #  | Colonna            | Tipo   | Descrizione                                                                                                      |
|----|--------------------|--------|------------------------------------------------------------------------------------------------------------------|
| 18 | `AccountSid`       | BIGINT | Security Identifier (SID) di Windows codificato — l'ID interno univoco per un account utente in Active Directory. |
| 19 | `AccountUpn`       | BIGINT | User Principal Name codificato — il formato email di login utilizzato in ambienti aziendali (es. `jsmith@contoso.com`). |
| 20 | `AccountObjectId`  | BIGINT | ID oggetto di Azure Active Directory codificato per l'account — utilizzato nei sistemi di identità cloud.         |
| 21 | `AccountName`      | BIGINT | Nome visualizzato codificato dell'account utente.                                                                |

### 3.9 Proprietà dell'Entità — Email

Popolate quando `EntityType` è `MailMessage`, `MailBox` o `MailCluster`.

| #  | Colonna              | Tipo    | Descrizione                                                                                                                                              |
|----|----------------------|---------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| 24 | `EmailClusterId`     | DOUBLE  | Identificatore per un cluster di email simili (una campagna di phishing che colpisce più destinatari). ~78% null — popolato solo per tipi di entità relativi alle email. |
| 39 | `AntispamDirection`  | VARCHAR | Direzione dell'email che ha attivato l'avviso. Valori: `Inbound` (ricevuta), `Outbound` (inviata), `Intraorg` (interna).                                 |

### 3.10 Proprietà dell'Entità — Registry

Popolate quando `EntityType` è `RegistryKey`. Le modifiche al registro sono una tecnica di persistenza classica — il malware si aggiunge alle chiavi di registro di avvio automatico per sopravvivere ai riavvii.

| #  | Colonna              | Tipo   | Descrizione                                                                                             |
|----|----------------------|--------|---------------------------------------------------------------------------------------------------------|
| 25 | `RegistryKey`        | BIGINT | Percorso della chiave di registro di Windows codificato modificato (es. `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run`). |
| 26 | `RegistryValueName`  | BIGINT | Nome codificato del valore di registro specifico che è stato creato o modificato.                       |
| 27 | `RegistryValueData`  | BIGINT | Dati codificati memorizzati nel valore di registro — spesso un percorso verso un eseguibile malevolo.   |

### 3.11 Proprietà dell'Entità — Cloud e Applicazioni

Popolate quando `EntityType` è `CloudApplication`, `OAuthApplication` o `CloudLogonRequest`.

| #  | Colonna               | Tipo    | Descrizione                                                                                                                                                                             |
|----|-----------------------|---------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 28 | `ApplicationId`       | BIGINT  | Identificatore codificato dell'applicazione cloud coinvolta.                                                                                                                            |
| 29 | `ApplicationName`     | BIGINT  | Nome codificato dell'applicazione cloud (es. SharePoint, Teams, un SaaS di terze parti).                                                                                                |
| 30 | `OAuthApplicationId`  | BIGINT  | Identificatore codificato di un'applicazione OAuth. Le app OAuth richiedono permessi per accedere ai dati degli utenti — le app malevole che chiedono permessi eccessivi sono un attacco comune (consent phishing). |
| 34 | `ResourceIdName`      | BIGINT  | Nome codificato della risorsa cloud a cui si è acceduto (es. un blob di storage, una VM, un database).                                                                                  |
| 35 | `ResourceType`        | VARCHAR | Tipo di risorsa cloud coinvolta (es. `VirtualMachine`, `StorageAccount`, `KeyVault`).                                                                                                   |
| 36 | `Roles`               | VARCHAR | Ruoli o permessi associati all'entità nell'ambiente cloud. Gli avvisi di escalation dei privilegi coinvolgono questo campo.                                                              |

### 3.12 Valutazione Automatica

Queste colonne rappresentano la pre-valutazione automatica di Defender XDR prima che l'analista umano esamini l'incidente. Sono caratteristiche (features), non target.

| #  | Colonna           | Tipo    | Descrizione                                                                                                                                                                |
|----|-------------------|---------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 31 | `ThreatFamily`    | VARCHAR | Nome di una famiglia di malware nota se la minaccia è stata identificata (es. `Emotet`, `Mimikatz`, `Cobalt Strike`). `None` se non corrisponde a una famiglia nota.       |
| 40 | `SuspicionLevel`  | VARCHAR | Valutazione automatica del sospetto di Defender XDR per questa entità. Codificata come livello categorico. Valori più alti indicano un sospetto più forte prima della revisione dell'analista umano. |
| 41 | `LastVerdict`     | VARCHAR | Verdetto automatico più recente assegnato dal rilevatore. Valori: `Malicious`, `Suspicious`, `Clean`, `Unknown`, `None`.                                                   |

### 3.13 Colonna Solo Test

| #  | Colonna  | Tipo    | Descrizione                                                                                                                                                                    |
|----|----------|---------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 45 | `Usage`  | VARCHAR | Presente solo nella suddivisione di test. Indica l'uso previsto della riga nella partizione originale del benchmark di Kaggle. Non disponibile al momento dell'inferenza in uno scenario di produzione. |

---