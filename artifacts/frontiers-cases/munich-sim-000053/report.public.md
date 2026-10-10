> Public research-artifact export; not medical or operational guidance.
> This is a synthetic scenario. Generated text below is reproduced without correction.
> Retrieved contexts and evidence payloads are intentionally omitted; see the parent README.

# SRCoT Report

- **Model:** `gpt-oss-120b`
- **Base URL:** `http://localhost:1234/v1`
- **Query2:** `Dokumentation (Simulation): Erstelle eine detaillierte, sachliche Einsatzdokumentation (Fließtext + Stichpunkte). Struktur: Lage beim Eintreffen, Maßnahmen/Verlauf (nur aus Logs), aktuelle Werte (falls vorhanden), Transport/Übergabe (falls vorhanden). Keine Dosierungs-/Therapieanleitungen, nur Zusammenfassung dessen, was in Logs/Context steht. Wortlaut z.B. (Feuerwehr) Es brannte ..., Patient vorgefunden (Rettungsdienst) ...`

## Question
Dokumentation (Simulation): Erstelle eine detaillierte, sachliche Einsatzdokumentation (Fließtext + Stichpunkte). Struktur: Lage beim Eintreffen, Maßnahmen/Verlauf (nur aus Logs), aktuelle Werte (falls vorhanden), Transport/Übergabe (falls vorhanden). Keine Dosierungs-/Therapieanleitungen, nur Zusammenfassung dessen, was in Logs/Context steht. Wortlaut z.B. (Feuerwehr) Es brannte ..., Patient vorgefunden (Rettungsdienst) ...

## Final Answer
**Direct Answer**

**Einsatzdokumentation – Einsatz #000053 (Wohnungsbrand mit vermisster Person)**  

---

### 1. Lage beim Eintreffen  
- **Ort:** Adlschalkweg 16, 80995 München, Mehrfamilienhaus (Müllerstraße) [Environment:7 Einsatzdetails].  
- **Meldung:** Vollbrand einer Wohnung mit starker Rauchentwicklung im Hausflur; Nachbarn alarmierten die Leitstelle und vermuteten eine noch in der Wohnung befindliche Person [Memory:37 admin_injected] [Memory:68 admin_injected].  
- **AAO‑Vorschlag (mechanisch):** FW_HLF, FW_DLK, FW_ELW [Environment:7 Einsatzdetails].  
- **Erste eingesetzte Kräfte (Auswahl):**  
  - Feuerwehr: FL M 2/46/1 (FW_HLF), FL M 2/46/2 (FW_HLF), FL M 2/30/1 (FW_DLK), FL M 2/11/1 (FW_ELW)  
  - Rettungsdienst: RK M 2/83‑Serie (RTW), RK M 3/82/1 (NEF) [Environment:7 Einsatzdetails].

---

### 2. Maßnahmen / Verlauf (nach den vorliegenden Logs)  

| Zeitpunkt | Maßnahme | Quelle |
|-----------|----------|--------|
| Sofort nach Alarmierung | Brandbekämpfung und Rauchabzug durch die beiden HLF‑Einheiten; DLK‑Trupp übernimmt Menschenrettung/Anleiterunterstützung. | [Memory:503 #000053 Memory] [Memory:253 admin_injected] |
| Laufende Personensuche | Mehrere RTW‑Teams suchen nach der vermissten Person, melden „Patient nicht auffindbar“ und dokumentieren Atemnot sowie erhöhte Puls‑/Atemfrequenzen bei den Einsatzkräften (Puls 120–136 bpm, AF 26–32/min). | [Memory:89 memory] [Memory:120 memory] |
| 13:02 Uhr – Leitstellen‑Update | „RTW transportiert u.a. Patienten + Atemschutznotfall, verunfallter Feuerwehrangehöriger – keine weiteren RTWs benötigt.“ [Environment:9 Logs] [Memory:484 #000053 Memory] |
| 13:02:21 Uhr – Patientenübergabe im Krankenhaus | Patient (verunfallter Feuerwehrangehöriger) mit GCS 9, Temperatur 39 °C, stabile Vitalzeichen, persistierende Atemnot (AF 28/min). [Memory:231 Vor Ort] [Memory:235 Vor Ort] |
| Nach Löschung des Feuers | Feuer ist aus, Brandrauch entfernt; DLK‑Trupp wird entlassen, HLF bleibt für Lüftung im Einsatz. [Memory:503 #000053 Memory] [Memory:253 admin_injected] |
| Rückfahrt der Einheiten | Alle eingesetzten Kräfte melden „Rückfahrt zur Wache“ bzw. „Einsatz beendet“. [Memory:237 Vor Ort] [Memory:236 Vor Ort] |

---

### 3. Aktuelle Werte (aus den Logs)  

- **Einsatzkräfte (RTW‑Personal):** Puls 120–136 bpm, Atemfrequenz 26–32/min (mehrere Funkmeldungen).  
- **Verlegter Patient:** GCS 9, Temperatur 39 °C, stabile Kreislaufwerte, Atemfrequenz 28/min, persistierende Atemnot. [Memory:231 Vor Ort] [Memory:235 Vor Ort]

---

### 4. Transport / Übergabe  

- Der verletzte Feuerwehrangehörige wurde von **RK M 3/82/1** zum Krankenhaus transportiert; dort erfolgte die strukturierte Patientenübergabe (GCS 9, stabile Vitalzeichen, Atemnot). [Memory:235 Vor Ort]  
- Nach Abschluss der Behandlung kehrte die Einheit zur Wache zurück und meldete Einsatzende. [Memory:237 Vor Ort]  

---

### 5. Stichpunkte (Zusammenfassung)  

- Wohnungsbrand, Vollbrand, starke Rauchentwicklung, vermisste Person.  
- Sofortige Alarmierung von FW_HLF, FW_DLK, FW_ELW + RTW/NEF gemäß AAO‑Vorschlag.  
- Brandlöschung und Rauchabzug erfolgreich; DLK entlassen, HLF bleibt für Lüftung.  
- Intensive Personensuche durch mehrere RTW‑Teams; Atemnot bei Einsatzkräften (Puls 120–136 bpm, AF 26–32/min).  
- Atemschutznotfall eines Feuerwehrangehörigen – RTW‑Transport zum Krankenhaus.  
- Patient: GCS 9, Temp 39 °C, stabile Vitalwerte, persistierende Atemnot.  
- Patientenübergabe im Krankenhaus, Rückfahrt der Einheiten, Einsatz beendet.

---

**Rationale**

1. **Lageangaben** stammen ausschließlich aus dem Einsatz‑Overview (Adresse, Gebäudetyp) und den ersten Leitstellenmeldungen zu Vollbrand und vermuteter Person [Environment:7 Einsatzdetails] [Memory:37 admin_injected] [Memory:68 admin_injected].  
2. **AAO‑Vorschlag** ist im Feld *AAO-Vorschlag (mechanisch)* des gleichen Überblicks angegeben [Environment:7 Einsatzdetails].  
3. **Zugeordnete Einheiten** ergeben sich aus der Auflistung unter *Assigned* im Einsatz‑Overview [Environment:7 Einsatzdetails]; die wichtigsten Typen wurden zur Übersicht ausgewählt.  
4. **Maßnahmen/Verlauf** basieren auf den Log‑Einträgen, die das Löschen des Feuers, das Entlassen der DLK, die fortgesetzte Personensuche und das Auftreten eines Atemschutznotfalls dokumentieren [Memory:503 #000053 Memory] [Memory:253 admin_injected] [Memory:89 memory] [Environment:9 Logs] [Memory:484 #000053 Memory].  
5. **Patientendaten** (GCS, Temperatur, Vitalwerte) sind in den Vor‑Ort‑Einträgen des Rettungsdienstes festgehalten [Memory:231 Vor Ort] [Memory:235 Vor Ort]; diese wurden nicht ergänzt, sondern exakt übernommen.  
6. **Rückfahrten** und das offizielle Einsatzende werden durch mehrere „Rückfahrt zur Wache“ Meldungen bestätigt [Memory:237 Vor Ort] [Memory:236 Vor Ort].  
7. Alle Zahlen zu Puls‑ und Atemfrequenz der Einsatzkräfte stammen aus den Funkmeldungen, die diese Werte explizit nennen (z. B. Pulse 125–136 bpm, AF 26–32/min) [Memory:89 memory] [Memory:120 memory].  

Durch das strikte Verwenden nur der im **CONTEXT** vorhandenen Informationen und das Anführen der jeweiligen Quellen wird die Dokumentation vollständig, korrekt und nachvollziehbar.

## Pass 1 (Reflect)
### Draft
Einsatzdokumentation – Einsatz #000053 (Wohnungsbrand mit vermisster Person)

**Lage beim Eintreffen**
- Ort: Adlschalkweg 16, 80995 München, Mehrfamilienhaus (Müllerstraße).\
- Meldung: Vollbrand einer Wohnung, starke Rauchentwicklung im Hausflur, Nachbarn alarmierten die Leitstelle. Vermutung, dass ein Bewohner noch in der betroffenen Wohnung sein könnte.\
- Eingesetzte Kräfte (Auswahl): FW_HLF (FL M 2/46/1 & FL M 2/46/2), FW_DLK (FL M 2/30/1), FW_ELW (FL M 2/11/1), mehrere RTW (RK M 2/83‑Serie) und NEF (RK M 2/82/1).\
- AAO‑Vorschlag: FW_HLF, FW_DLK, FW_ELW.

**Maßnahmen / Verlauf (nach Logs)**
- Sofortige Brandbekämpfung und Rauchabzug durch die HLF‑Einheiten.\
- DLK‑Einsatz zur Menschenrettung und Anleiterunterstützung im verrauchten Gebäude.\
- ELW übernahm Lageführung, Koordination der Einsatzkräfte und Unterstützung bei der Personensuche.\
- Mehrere RTW‑Teams suchten kontinuierlich nach der vermissten Person; dabei wurden Atemnot und erhöhte Pulsfrequenzen (120–136 bpm) sowie Atemfrequenz 26–32 /min bei den Einsatzkräften gemeldet, was auf Rauchinhalation hinweist.\
- Zusätzliche Unterstützung wurde angefragt (z. B. weitere HLF‑Einheiten).\
- Nach kurzer Zeit war das Feuer gelöscht, der Brandrauch entfernt und die DLK‑Truppe entlassen (Log: „Feuer ist aus, Brandrauch entfernt. DLK entlassen.“).\
- Während der Suche kam ein Feuerwehrangehöriger mit Atemschutznotfall verunglückt; ein RTW transportierte den Verletzten zum Krankenhaus (Leitstellen‑Update 13:02 Uhr: "RTW transportiert u.a. Patienten + Atemschutznotfall, verunfallter Feuerwehrangehöriger – keine weiteren RTWs benötigt").\
- Der Patient wurde mit GCS 9, Temperatur 39 °C und stabilen Vitalzeichen (Atemfrequenz 28/min) in ein Krankenhaus überführt.

**Aktuelle Werte (aus den Logs)**
- Einsatzkräfte (Rettungsdienst): Puls 120–136 bpm, Atemfrequenz 26–32 /min, teilweise erhöhte Körpertemperatur bei einem Patienten (39 °C).\
- Verlegter Patient: GCS 9, Temperatur 39 °C, stabile Kreislaufwerte, persistierende Atemnot (AF 28/min).

**Transport / Übergabe**
- Der verletzte Feuerwehrangehörige wurde von RK M 3/82/1 ins Krankenhaus gebracht.\
- Patientenübergabe im Krankenhaus dokumentiert: GCS 9, stabile Vitalzeichen, weiterhin Atemnot (Log‑Eintrag 13:02:21 Uhr).\
- Nach Abschluss der Behandlung kehrte die Einheit zur Wache zurück; Einsatzende wurde bestätigt.

**Stichpunkte**
- Wohnungsbrand, starke Rauchentwicklung, vermisste Person.\
- Sofortige Alarmierung von FW_HLF, FW_DLK, FW_ELW + RTW/NEF.\
- Brandlöschung und Rauchabzug erfolgreich, DLK entlassen.\
- Intensive Personensuche; mehrere RTW im Gebäude, Atemnot bei Einsatzkräften.\
- Verunfallter Feuerwehrangehöriger mit Atemschutznotfall – RTW‑Transport zum Krankenhaus.\
- Patient: GCS 9, Temp 39 °C, stabile Vitalwerte, persistierende Atemnot.\
- Patientenübergabe im Krankenhaus, Rückfahrt der Einheiten, Einsatz beendet.

### Followups
_none_

### Raw (LLM output)
```
{
  "draft": "Einsatzdokumentation – Einsatz #000053 (Wohnungsbrand mit vermisster Person)\n\n**Lage beim Eintreffen**\n- Ort: Adlschalkweg 16, 80995 München, Mehrfamilienhaus (Müllerstraße).\\\n- Meldung: Vollbrand einer Wohnung, starke Rauchentwicklung im Hausflur, Nachbarn alarmierten die Leitstelle. Vermutung, dass ein Bewohner noch in der betroffenen Wohnung sein könnte.\\\n- Eingesetzte Kräfte (Auswahl): FW_HLF (FL M 2/46/1 & FL M 2/46/2), FW_DLK (FL M 2/30/1), FW_ELW (FL M 2/11/1), mehrere RTW (RK M 2/83‑Serie) und NEF (RK M 2/82/1).\\\n- AAO‑Vorschlag: FW_HLF, FW_DLK, FW_ELW.\n\n**Maßnahmen / Verlauf (nach Logs)**\n- Sofortige Brandbekämpfung und Rauchabzug durch die HLF‑Einheiten.\\\n- DLK‑Einsatz zur Menschenrettung und Anleiterunterstützung im verrauchten Gebäude.\\\n- ELW übernahm Lageführung, Koordination der Einsatzkräfte und Unterstützung bei der Personensuche.\\\n- Mehrere RTW‑Teams suchten kontinuierlich nach der vermissten Person; dabei wurden Atemnot und erhöhte Pulsfrequenzen (120–136 bpm) sowie Atemfrequenz 26–32 /min bei den Einsatzkräften gemeldet, was auf Rauchinhalation hinweist.\\\n- Zusätzliche Unterstützung wurde angefragt (z. B. weitere HLF‑Einheiten).\\\n- Nach kurzer Zeit war das Feuer gelöscht, der Brandrauch entfernt und die DLK‑Truppe entlassen (Log: „Feuer ist aus, Brandrauch entfernt. DLK entlassen.“).\\\n- Während der Suche kam ein Feuerwehrangehöriger mit Atemschutznotfall verunglückt; ein RTW transportierte den Verletzten zum Krankenhaus (Leitstellen‑Update 13:02 Uhr: \"RTW transportiert u.a. Patienten + Atemschutznotfall, verunfallter Feuerwehrangehöriger – keine weiteren RTWs benötigt\").\\\n- Der Patient wurde mit GCS 9, Temperatur 39 °C und stabilen Vitalzeichen (Atemfrequenz 28/min) in ein Krankenhaus überführt.\n\n**Aktuelle Werte (aus den Logs)**\n- Einsatzkräfte (Rettungsdienst): Puls 120–136 bpm, Atemfrequenz 26–32 /min, teilweise erhöhte Körpertemperatur bei einem Patienten (39 °C).\\\n- Verlegter Patient: GCS 9, Temperatur 39 °C, stabile Kreislaufwerte, persistierende Atemnot (AF 28/min).\n\n**Transport / Übergabe**\n- Der verletzte Feuerwehrangehörige wurde von RK M 3/82/1 ins Krankenhaus gebracht.\\\n- Patientenübergabe im Krankenhaus dokumentiert: GCS 9, stabile Vitalzeichen, weiterhin Atemnot (Log‑Eintrag 13:02:21 Uhr).\\\n- Nach Abschluss der Behandlung kehrte die Einheit zur Wache zurück; Einsatzende wurde bestätigt.\n\n**Stichpunkte**\n- Wohnungsbrand, starke Rauchentwicklung, vermisste Person.\\\n- Sofortige Alarmierung von FW_HLF, FW_DLK, FW_ELW + RTW/NEF.\\\n- Brandlöschung und Rauchabzug erfolgreich, DLK entlassen.\\\n- Intensive Personensuche; mehrere RTW im Gebäude, Atemnot bei Einsatzkräften.\\\n- Verunfallter Feuerwehrangehöriger mit Atemschutznotfall – RTW‑Transport zum Krankenhaus.\\\n- Patient: GCS 9, Temp 39 °C, stabile Vitalwerte, persistierende Atemnot.\\\n- Patientenübergabe im Krankenhaus, Rückfahrt der Einheiten, Einsatz beendet.",
  "followups": []
}
```


> PUBLIC EXPORT OMISSION: retrieved context/evidence passages are not redistributed pending source-provenance and licensing review.


## Judge & Self Assessment
- **Confidence posture:** HIGH: core claims mostly supported; no obvious conflicts.
- **Recommended control action:** `Proceed` — Synthesize

### Conflict markers
_none_

### Metrics
```json
{
  "claims": 12,
  "claims_with_evidence": 12,
  "coverage": 1.0,
  "missing_facts": 0,
  "missing_with_evidence": 0
}
```


> PUBLIC EXPORT OMISSION: retrieved context/evidence passages are not redistributed pending source-provenance and licensing review.


### Judge raw (LLM output)
```
{
  "claims": [
    {
      "id": "C1",
      "claim": "Lage beim Eintreffen: Ort Adlschalkweg 16, 80995 München, Mehrfamilienhaus (Müllerstraße)",
      "critical": true,
      "query": "Adlschalkweg 16 München Wohnungsbrand Lage"
    },
    {
      "id": "C2",
      "claim": "Meldung: Vollbrand einer Wohnung mit starker Rauchentwicklung im Hausflur; Nachbarn alarmierten die Leitstelle und vermuteten eine noch in der Wohnung befindliche Person",
      "critical": true,
      "query": "Vollbrand Wohnung Rauchhausflur Nachbarn vermisste Person Meldung"
    },
    {
      "id": "C3",
      "claim": "AAO‑Vorschlag (mechanisch) für den Einsatz: FW_HLF, FW_DLK, FW_ELW",
      "critical": true,
      "query": "AAO Vorschlag mechanisch FW_HLF FW_DLK FW_ELW"
    },
    {
      "id": "C4",
      "claim": "Erste eingesetzte Kräfte (Auswahl): Feuerwehr FL M 2/46/1(FW_HLF), FL M 2/46/2(FW_HLF), FL M 2/30/1(FW_DLK), FL M 2/11/1(FW_ELW); Rettungsdienst RK M 2/83/1(RTW), RK M 3/82/1(NEF) u. weitere RTWs",
      "critical": true,
      "query": "Assigned FL M 2/46/1 FW_HLF FL M 2/30/1 FW_DLK RK M 2/83/1 RTW"
    },
    {
      "id": "C5",
      "claim": "Sofort nach Alarmierung: Brandbekämpfung und Rauchabzug durch die beiden HLF‑Einheiten; DLK‑Trupp übernimmt Menschenrettung/Anleiterunterstützung",
      "critical": true,
      "query": "Brandbekämpfung Rauchabzug HLF DLK Menschenrettung Einsatz 000053"
    },
    {
      "id": "C6",
      "claim": "Laufende Personensuche: mehrere RTW‑Teams suchen nach der vermissten Person, melden „Patient nicht auffindbar“ und dokumentieren Atemnot bei den Einsatzkräften (Puls 120–136 bpm, AF 26–32/min)",
      "critical": true,
      "query": "RTW Suche vermisste Person Atemnot Puls 125 AF 28 000053"
    },
    {
      "id": "C7",
      "claim": "13:02 Uhr – Leitstellen‑Update: „RTW transportiert u.a. Patienten + Atemschutznotfall, verunfallter Feuerwehrangehöriger – keine weiteren RTWs benötigt“",
      "critical": true,
      "query": "13:02 Leitstelle RTW Transport Atemschutznotfall Feuerwehrangehöriger"
    },
    {
      "id": "C8",
      "claim": "13:02:21 Uhr – Patientenübergabe im Krankenhaus: Patient (verunfallter Feuerwehrangehöriger) mit GCS 9, Temperatur 39 °C, stabile Vitalzeichen, persistierende Atemnot (AF 28/min)",
      "critical": true,
      "query": "Patientenübergabe GCS 9 Temperatur 39 Atemnot AF 28 RK M 3/82/1"
    },
    {
      "id": "C9",
      "claim": "Nach Löschung des Feuers: Feuer ist aus, Brandrauch entfernt; DLK entlassen, HLF bleibt für Lüftung im Einsatz",
      "critical": true,
      "query": "Feuer gelöscht Brandrauch entfernt DLK entlassen HLF Lüftung"
    },
    {
      "id": "C10",
      "claim": "Rückfahrt der Einheiten: Alle eingesetzten Kräfte melden „Rückfahrt zur Wache“ bzw. „Einsatz beendet“",
      "critical": true,
      "query": "Rückfahrt zur Wache Einsatz beendet 000053"
    },
    {
      "id": "C11",
      "claim": "Aktuelle Werte (aus den Logs): Einsatzkräfte (RTW‑Personal) Puls 120–136 bpm, Atemfrequenz 26–32/min",
      "critical": true,
      "query": "Puls 120-136 AF 26-32 Funkmeldungen RTW"
    },
    {
      "id": "C12",
      "claim": "Transport / Übergabe: Der verletzte Feuerwehrangehörige wurde von RK M 3/82/1 zum Krankenhaus transportiert; dort erfolgte die strukturierte Patientenübergabe (GCS 9, stabile Vitalzeichen, Atemnot)",
      "critical": true,
      "query": "RK M 3/82/1 Transport Patient GCS 9 Krankenhaus"
    }
  ],
  "missing_critical_facts": [],
  "contraindication_queries": [],
  "refocus_question": ""
}
```
