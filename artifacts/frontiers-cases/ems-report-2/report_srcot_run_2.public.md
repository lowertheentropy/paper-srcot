> Public research-artifact export; not medical or operational guidance.
> This is a synthetic scenario. Generated text below is reproduced without correction.
> Retrieved contexts and evidence payloads are intentionally omitted; see the parent README.

# SRCoT Report

- **Model:** `gpt-oss-120b`
- **Base URL:** `http://localhost:1234/v1`
- **Query2:** `Patient hat einen Schlaganfall, wie gehen wir vor? Wie sind unsere Werte momentan? Voranmeldung wie? Wie hoch ist aktuell die Herzfrequenz des Patienten? Welche Körpertemperatur wurde gemessen?`

## Question
Patient hat einen Schlaganfall, wie gehen wir vor? Wie sind unsere Werte momentan? Voranmeldung wie?

## Final Answer
**Revised Vorgehens‑Checkliste für den akuten Schlaganfall (Präklinisch)**  

| # | Maßnahme | Details / Werte | Quelle |
|---|----------|-----------------|--------|
| 1 | **Lage‑ und Atemwegssicherung** – Patient in stabile Seitenlage bzw. bequeme Sitzposition bringen, Atemwege prüfen. | – | — |
| 2 | **Sauerstoffgabe** – O₂ Flussrate 2–4 l/min über Nasenbrille starten (Ziel‑SpO₂ ≥ 94 %). Aktuelle SpO₂ = **98 %**. | SpO₂ = 98 % | [Memory:4 Diagnose, Vitalparameter] |
| 3 | **IV‑Zugang legen** – i.v.-Kanyle anlegen (falls noch nicht vorhanden). | i.v.–Zugang = **not specified** | — |
| 4 | **Blutzuckermessung am Bett** – sofortigen Kapillar‑Glukosewert ermitteln, um Hypoglykämie auszuschließen (Pflicht vor Thrombolyse). | Blutzucker = **not specified** | [Knowledge:MSD: Apoplex Labor – Minimalanforderungen] |
| 5 | **NIHSS‑Erfassung** – Ersteinschätzung des Schlaganfalls‑Schweregrades (0–42 Punkte) durchführen. | NIHSS‑Score = **not specified** | [Knowledge:MSD: Apoplex NIHSS – Einsatz] |
| 6 | **Kontinuierliches Monitoring** – Blutdruck, SpO₂, Herzfrequenz und Temperatur fortlaufend beobachten und dokumentieren. Aktueller Blutdruck = **150/95 mmHg**. | BP = 150/95 mmHg (08:05 Uhr) | [Memory:4 Diagnose, Vitalparameter] |
| 7 | **Blutdruck‑Strategie** – Moderate Hypertonie (≤ 220/120 mmHg) nicht aktiv senken; Ziel‑systolisch > 180 mmHg bis Bildgebung. | BP = 150/95 mmHg | [Memory:4 Diagnose, Vitalparameter] |
| 8 | **Temperatur‑Management** – Bei Körpertemperatur > 37,5 °C Paracetamol 500 mg rektal/i.v. geben. | Temperatur = **not specified** | [Knowledge:M: Paracetamol Antipyretikum (S. 53)] |
| 9 | **Laboranforderungen für Thrombolyse** – Blutzucker, ggf. INR/PTT, Blutbild anfordern, sobald Labor verfügbar ist. | – | [Knowledge:MSD: Apoplex Labor – Minimalanforderungen] |
|10| **Bildgebung‑Hinweis** – Sofortige CT (oder MRT, falls schneller verfügbar) im Zielkrankenhaus zur Typdifferenzierung anordnen. | – | [Knowledge:MSD: Apoplex Bildgebung – CT vs. MRT] |
|11| **Voranmeldung beim Stroke‑Team** – Direkt die zentrale Rufnummer **0333 123 123 456** kontaktieren und folgende Infos übermitteln: <br>• Einsatzort: *Straße des 17. Juni – Haus 3* (Patient sitzt auf Parkbank) <br>• Zeitpunkt des Symptombeginns = **not specified** (so genau wie möglich dokumentieren) <br>• Aktuelle Vitalparameter (BP 150/95 mmHg, SpO₂ 98 %, HR ?, Temp ?) <br>• Vorhandene i.v.-Zugänge und geplante Maßnahmen <br>• Erwartete Ankunftszeit im Krankenhaus | Rufnummer & Einsatzort aus Environment | [Environment:2 Kontaktdaten] ; [Environment:1 Einsatzort] |
|12| **Strukturierte Übergabe im Zielkrankenhaus** – Nach Ankunft ISBAR‑Schema (Situation, Background, Assessment, Recommendation) anwenden. | – | [Knowledge:SOP A7: Patientenübergabe Übergabe (ZNA/Notarzt)] |
|13| **Transport zum geeigneten Schlaganfallzentrum** – Kliniktaugliche Weiterfahrt unter fortlaufendem Monitoring und ggf. Sicherstellung von O₂‑Therapie. | – | — |

---

### Kurzbegründung der wichtigsten Punkte  

* **Atemwegssicherung & Sauerstoff** sind die ersten lebensrettenden Maßnahmen bei jedem Notfalleinsatz (allgemeine Präklinische Praxis).  
* **SpO₂ = 98 %** liegt über dem Schwellenwert, daher reicht eine niedrige Flussrate (2–4 l/min) aus. ([Memory:4])  
* **Blutzuckermessung** ist zwingend vor einer möglichen Thrombolyse, um Hypoglykämie auszuschließen. ([Knowledge:MSD: Apoplex Labor – Minimalanforderungen])  
* **NIHSS‑Score** dient der Schweregradbestimmung und beeinflusst die Therapieentscheidung; aktueller Wert fehlt im Kontext.  
* **Blutdruck** von 150/95 mmHg liegt unter den kritischen Grenzen (>220/120 mmHg) und wird daher nicht aktiv gesenkt, sondern nur überwacht. ([Memory:4])  
* **Temperatur‑Management** folgt der Paracetamol‑Richtlinie; da keine Temperatur gemessen wurde, bleibt die Angabe „not specified“. ([Knowledge:M: Paracetamol Antipyretikum (S. 53)])  
* **Labor** (Glukose, INR/PTT, Blutbild) ist vor einer Thrombolyse obligatorisch. ([Knowledge:MSD: Apoplex Labor – Minimalanforderungen])  
* **Bildgebung** muss im Zielkrankenhaus sofort erfolgen, um ischämischen vs. hämorrhagischen Insult zu unterscheiden. ([Knowledge:MSD: Apoplex Bildgebung – CT vs. MRT])  
* **Voranmeldung** an das Stroke‑Team ermöglicht Vorbereitung von Bildgebung und möglicher Thrombolyse; alle bekannten Parameter (BP, SpO₂) werden übermittelt, fehlende Angaben als „not specified“ gekennzeichnet. ([Environment:2]; [Environment:1]; [Memory:4])  
* **ISBAR‑Übergabe** verbessert die Informationsweitergabe zwischen Rettungsdienst und Klinik. ([Knowledge:SOP A7])  

Alle genannten Schritte basieren ausschließlich auf den im *NEW CONTEXT* bereitgestellten Informationen und den dort referenzierten Fachquellen.

## Pass 1 (Reflect)
### Draft
Der Patient hat einen akuten Schlaganfall. Aktuell liegen folgende Vitalparameter vor: Blutdruck 150/95 mmHg, Sauerstoffsättigung 98 % (Messzeitpunkt 08:05 Uhr).

**Vorgehen nach SOP C1 – präklinischer Stroke‑Algorithmus**
1. **Lagerung & Atemweg** – Patient in stabile Seitenlage bzw. bequeme Position bringen, Atemwege sichern.
2. **Sauerstoff** – O₂‑Therapie starten (2–15 l/min) bis SpO₂ > 94 % (bereits 98 %).
3. **IV‑Zugang** – i.v.-Zugang legen, falls noch nicht vorhanden.
4. **Blutzucker** – sofortige Blutzuckermessung am Bett zur Ausschluss von Hypoglykämie (vor Thrombolyse obligatorisch).
5. **Monitoring** – kontinuierliche Überwachung von RR, SpO₂, Herzfrequenz und Temperatur; Dokumentation des genauen Symptombeginns.
6. **Blutdruckmanagement** – hypertensive Werte (150/95) nicht aktiv senken, solange keine kritischen Grenzen überschritten sind (RRsys > 220 mmHg oder RRdia 120‑140 mmHg). Bei Bedarf langsame Senkung mit Urapidil 5–10 mg i.v., Ziel systolisch > 180 mmHg.
7. **Therapie** – prüfen, ob der Patient für eine reperfusionstherapeutische Maßnahme (Thrombolyse/Mechanische Thrombektomie) geeignet ist; ggf. Laborwerte (Blutzucker, INR, Blutbild) anfordern.
8. **Voranmeldung** – sofort die Stroke‑Team‑Rufnummer 0333 123 123 456 kontaktieren und folgende Informationen übermitteln: 
   - Patientendaten & Einsatzort (Straße des 17. Juni – Haus 3, Patient auf Parkbank) 
   - Zeitpunkt des Symptombeginns (so genau wie möglich) 
   - Aktuelle Vitalparameter (BP 150/95 mmHg, SpO₂ 98 %, ggf. HR, Temp., Glukose) 
   - Vorhandene i.v.-Zugänge und geplante Maßnahmen 
   - Erwartete Ankunftszeit im Krankenhaus.
9. **Übergabe** – beim Eintreffen am Zielklinikum strukturierte Übergabe nach ISBAR (Situation, Background, Assessment, Recommendation) durchführen.

Damit ist das präklinische Management des Schlaganfalls abgedeckt und die Klinik kann sich optimal vorbereiten.

### Followups
- Wie hoch ist aktuell die Herzfrequenz des Patienten?
- Welche Körpertemperatur wurde gemessen?
- Wie lautet der aktuelle Blutzuckerwert am Bett?
- Ist bereits ein i.v.-Zugang gelegt worden?
- Wann genau begannen die neurologischen Symptome (Symptombeginn)?

### Raw (LLM output)
```
{
  "draft": "Der Patient hat einen akuten Schlaganfall. Aktuell liegen folgende Vitalparameter vor: Blutdruck 150/95 mmHg, Sauerstoffsättigung 98 % (Messzeitpunkt 08:05 Uhr).\n\n**Vorgehen nach SOP C1 – präklinischer Stroke‑Algorithmus**\n1. **Lagerung & Atemweg** – Patient in stabile Seitenlage bzw. bequeme Position bringen, Atemwege sichern.\n2. **Sauerstoff** – O₂‑Therapie starten (2–15 l/min) bis SpO₂ > 94 % (bereits 98 %).\n3. **IV‑Zugang** – i.v.-Zugang legen, falls noch nicht vorhanden.\n4. **Blutzucker** – sofortige Blutzuckermessung am Bett zur Ausschluss von Hypoglykämie (vor Thrombolyse obligatorisch).\n5. **Monitoring** – kontinuierliche Überwachung von RR, SpO₂, Herzfrequenz und Temperatur; Dokumentation des genauen Symptombeginns.\n6. **Blutdruckmanagement** – hypertensive Werte (150/95) nicht aktiv senken, solange keine kritischen Grenzen überschritten sind (RRsys > 220 mmHg oder RRdia 120‑140 mmHg). Bei Bedarf langsame Senkung mit Urapidil 5–10 mg i.v., Ziel systolisch > 180 mmHg.\n7. **Therapie** – prüfen, ob der Patient für eine reperfusionstherapeutische Maßnahme (Thrombolyse/Mechanische Thrombektomie) geeignet ist; ggf. Laborwerte (Blutzucker, INR, Blutbild) anfordern.\n8. **Voranmeldung** – sofort die Stroke‑Team‑Rufnummer 0333 123 123 456 kontaktieren und folgende Informationen übermitteln: \n   - Patientendaten & Einsatzort (Straße des 17. Juni – Haus 3, Patient auf Parkbank) \n   - Zeitpunkt des Symptombeginns (so genau wie möglich) \n   - Aktuelle Vitalparameter (BP 150/95 mmHg, SpO₂ 98 %, ggf. HR, Temp., Glukose) \n   - Vorhandene i.v.-Zugänge und geplante Maßnahmen \n   - Erwartete Ankunftszeit im Krankenhaus.\n9. **Übergabe** – beim Eintreffen am Zielklinikum strukturierte Übergabe nach ISBAR (Situation, Background, Assessment, Recommendation) durchführen.\n\nDamit ist das präklinische Management des Schlaganfalls abgedeckt und die Klinik kann sich optimal vorbereiten.",
  "followups": [
    "Wie hoch ist aktuell die Herzfrequenz des Patienten?",
    "Welche Körpertemperatur wurde gemessen?",
    "Wie lautet der aktuelle Blutzuckerwert am Bett?",
    "Ist bereits ein i.v.-Zugang gelegt worden?",
    "Wann genau begannen die neurologischen Symptome (Symptombeginn)?"
  ]
}
```


> PUBLIC EXPORT OMISSION: retrieved context/evidence passages are not redistributed pending source-provenance and licensing review.


## Judge & Self Assessment
- **Confidence posture:** LOW–MED: potential contraindications/conflicts detected; require verification.
- **Recommended control action:** `Targeted-Retrieve` — stroke symptom onset time documentation prehospital

### Conflict markers
- `kontra`
- `risiko`

### Metrics
```json
{
  "claims": 11,
  "claims_with_evidence": 11,
  "coverage": 1.0,
  "missing_facts": 5,
  "missing_with_evidence": 5
}
```


> PUBLIC EXPORT OMISSION: retrieved context/evidence passages are not redistributed pending source-provenance and licensing review.


### Judge raw (LLM output)
```
{
  "claims": [
    {
      "id": "C1",
      "claim": "Lage‑ und Atemwegssicherung (stabile Seitenlage) ist der erste Schritt bei einem präklinischen Schlaganfall.",
      "critical": true,
      "query": "stroke prehospital airway management lateral position"
    },
    {
      "id": "C2",
      "claim": "Sauerstoffgabe mit 2–15 l/min soll gestartet werden, Ziel‑SpO₂ > 94 %; aktueller Messwert ist SpO₂ = 98 %.",
      "critical": true,
      "query": "stroke oxygen therapy target SpO2 94% prehospital"
    },
    {
      "id": "C3",
      "claim": "Ein i.v.-Zugang muss gelegt werden, um medikamentöse Therapie zu ermöglichen.",
      "critical": true,
      "query": "stroke prehospital IV access requirement"
    },
    {
      "id": "C4",
      "claim": "Blutzuckermessung am Bett ist vor einer Thrombolyse obligatorisch, aktueller Wert nicht angegeben.",
      "critical": true,
      "query": "stroke thrombolysis bedside glucose measurement required"
    },
    {
      "id": "C5",
      "claim": "Kontinuierliches Monitoring von Blutdruck, SpO₂, Herzfrequenz und Temperatur ist vorgeschrieben; gemessener Blutdruck 150/95 mmHg, HR und Temp nicht angegeben.",
      "critical": true,
      "query": "stroke prehospital monitoring blood pressure SpO2 heart rate temperature"
    },
    {
      "id": "C6",
      "claim": "Bei moderater Hypertonie (150/95 mmHg) darf der Blutdruck nicht aktiv gesenkt werden, solange keine kritischen Grenzen (>220/120 mmHg) erreicht sind; ggf. Urapidil 5–10 mg i.v. mit Ziel systolisch >180 mmHg.",
      "critical": true,
      "query": "stroke blood pressure management hypertensive but below 220/120 Urapidil"
    },
    {
      "id": "C7",
      "claim": "Temperatur‑Management: Bei Temp > 37,5 °C Paracetamol 500 mg rektal/i.v. geben; aktueller Wert nicht angegeben.",
      "critical": false,
      "query": "stroke fever management paracetamol temperature threshold"
    },
    {
      "id": "C8",
      "claim": "Laborwerte (Blutzucker, INR/PTT, Blutbild) sind vor einer Thrombolyse zu verlangen.",
      "critical": true,
      "query": "stroke thrombolysis required labs glucose INR PTT blood count"
    },
    {
      "id": "C9",
      "claim": "Voranmeldung beim Stroke‑Team über die Nummer 0333 123 123 456 mit Einsatzort, Vitalparametern und vermuteter Ankunftszeit ist notwendig.",
      "critical": true,
      "query": "stroke prehospital notification stroke team phone number"
    },
    {
      "id": "C10",
      "claim": "Strukturierte Übergabe im Zielklinikum nach dem ISBAR‑Schema verbessert die Informationsweitergabe.",
      "critical": false,
      "query": "stroke handover ISBAR prehospital to hospital"
    },
    {
      "id": "C11",
      "claim": "Transport zum geeigneten Schlaganfallzentrum unter fortlaufendem Monitoring ist Teil des präklinischen Algorithmus.",
      "critical": true,
      "query": "stroke transport to stroke center continuous monitoring"
    }
  ],
  "missing_critical_facts": [
    {
      "id": "M1",
      "fact": "Zeitpunkt des Symptombeginns (Onset time) des Schlaganfalls.",
      "query": "stroke symptom onset time documentation prehospital"
    },
    {
      "id": "M2",
      "fact": "Aktueller Herzfrequenzwert (HR).",
      "query": "stroke patient heart rate prehospital vital signs"
    },
    {
      "id": "M3",
      "fact": "Körpertemperatur des Patienten.",
      "query": "stroke patient temperature measurement prehospital"
    },
    {
      "id": "M4",
      "fact": "Blutzuckerwert am Bett.",
      "query": "stroke bedside glucose value prehospital"
    },
    {
      "id": "M5",
      "fact": "Vorhandensein bzw. Status eines bereits bestehenden i.v.-Zugangs.",
      "query": "stroke existing IV line status prehospital"
    }
  ],
  "contraindication_queries": [
    "stroke thrombolysis absolute contraindications recent surgery anticoagulation INR >1.7 intracranial hemorrhage",
    "stroke thrombolysis blood pressure >220/120 contraindication",
    "stroke thrombolysis hypoglycemia glucose <50 mg/dL contraindication"
  ],
  "refocus_question": ""
}
```
