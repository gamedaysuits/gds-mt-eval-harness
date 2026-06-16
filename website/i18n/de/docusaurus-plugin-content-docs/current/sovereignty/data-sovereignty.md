---
sidebar_position: 7
title: "Datensouveränität"
description: "OCAP-, CARE- und Māori Data Sovereignty-Prinzipien für die Übersetzung indigener Sprachen. Warum die Zustimmung der Gemeinschaft vor der Bereitstellung steht."
related:
  - label: "Ownership Transfer"
    to: /docs/sovereignty/ownership-transfer
    kind: doc
    note: "How control of language data moves to communities"
  - label: "The Economic Model"
    to: /docs/sovereignty/economic-model
    kind: doc
  - label: "Reporting Errors and Owning Corrections"
    to: /docs/perspectives/reporting-errors-and-owning-corrections
    kind: position
  - label: "For Language Communities"
    to: /docs/community/for-language-communities
    kind: doc
---
# Datensouveränität

> **Zusammenfassung.** Diese Seite erläutert die Datensouveränitätsprinzipien OCAP®, CARE und Te Mana Raraunga sowie deren Bedeutung für Entwickler, die Übersetzungsmethoden für indigene Sprachen entwickeln. Sie behandelt, wann die Zustimmung der Gemeinschaft erforderlich ist, wie die `api`-Methodenarchitektur von champollion die Datensouveränität unterstützt und welche ethischen Verpflichtungen für alle gelten, die mit indigenen linguistischen Daten arbeiten.

Maschinelle Übersetzung für indigene Sprachen wirft Fragen auf, die für Französisch oder Japanisch nicht bestehen. Wem gehören die Trainingsdaten? Wer kontrolliert, wie ein Sprachmodell spricht? Wer entscheidet, ob eine Übersetzung gut genug für die Veröffentlichung ist?

**Die Antwort ist immer: die Gemeinschaft.**

champollion ist darauf ausgelegt, dies zu unterstützen. Die `api`-Methode hält alle linguistischen Ressourcen serverseitig unter der Kontrolle der Gemeinschaft. Das Plugin-System trennt die Methode vom Werkzeug. Doch das Werkzeug kann Ethik nicht erzwingen — diese Seite erläutert die Grundsätze, denen Sie folgen sollten.

---

## OCAP®-Prinzipien

**OCAP** (Ownership, Control, Access, Possession) ist eine Reihe von Grundsätzen, die vom [First Nations Information Governance Centre](https://fnigc.ca/ocap-training/) (FNIGC) entwickelt wurden und festlegen, wie Daten der First Nations erhoben, geschützt, genutzt und geteilt werden sollten.

| Prinzip | Was es für die Übersetzung bedeutet |
|-----------|------------------------------|
| **Ownership** | Die Gemeinschaft besitzt ihre linguistischen Daten — Wörterbücher, Grammatiken, Paralleltexte, Coaching-Dateien und alle daraus erstellten Übersetzungen. |
| **Control** | Die Gemeinschaft kontrolliert, wie ihre Sprachdaten genutzt werden, wer Zugriff hat und welche Übersetzungsmethoden akzeptabel sind. |
| **Access** | Mitglieder der Gemeinschaft haben das Recht, auf ihre eigenen Sprachressourcen zuzugreifen und diese zu verwalten, unabhängig davon, wo sie gespeichert sind. |
| **Possession** | Die physischen Daten (Coaching-Dateien, Wörterbücher, Modellgewichte) müssen auf einer von der Gemeinschaft kontrollierten Infrastruktur liegen — nicht in einer Cloud von Drittanbietern. |

### Was OCAP in der Praxis bedeutet

- **Veröffentlichen Sie keine Übersetzungen** einer indigenen Sprache ohne ausdrückliche Genehmigung der Gemeinschaft.
- **Trainieren Sie keine Modelle** mit von der Gemeinschaft bereitgestellten linguistischen Daten ohne eine Vereinbarung zur Datennutzung.
- **Extrahieren Sie keine** Sprachressourcen der Gemeinschaft aus Websites, sozialen Medien oder Bildungsmaterialien.
- **Verwenden Sie die `api`-Methode**, damit Prompts, Coaching-Daten und Wörterbücher auf von der Gemeinschaft kontrollierten Servern verbleiben. Die `api`-Methode von champollion ist eine „dumme Leitung“ — sie sendet Schlüssel hinaus und erhält Übersetzungen zurück. Sämtliches linguistisches geistiges Eigentum bleibt serverseitig.
- **Dokumentieren Sie die Herkunft** — das Feld `provenance` im [Plugin-Manifest](https://champollion.dev/docs/reference/plugin-spec) sollte jede verwendete Ressource, ihre Lizenz und ihren Ursprung auflisten.

:::warning OCAP® ist eine eingetragene Marke
OCAP® ist eine eingetragene Marke des First Nations Information Governance Centre. Sie gilt speziell für die First Nations in Kanada. Die Grundsätze haben eine breitere Relevanz, doch die Markenrechte und die Governance-Autorität liegen beim FNIGC.
:::

---

## CARE-Prinzipien

Die **CARE-Prinzipien für indigene Datengovernance** wurden von der [Global Indigenous Data Alliance](https://www.gida-global.org/care) (GIDA) als Ergänzung zu den FAIR-Datenprinzipien entwickelt. FAIR besagt, dass Daten Findable, Accessible, Interoperable und Reusable sein sollten. CARE besagt, dass dies nicht ausreicht — die Datengovernance muss zudem indigene Rechte in den Mittelpunkt stellen.

| Prinzip | Anwendung |
|-----------|------------|
| **Collective Benefit** | Übersetzungswerkzeuge sollten zuallererst der Sprachgemeinschaft zugutekommen. Leaderboard-Ergebnisse sind ein Mittel zur Verbesserung von Methoden, nicht zur Gewinnung kommerziellen Werts aus den Sprachen der Gemeinschaften. |
| **Authority to Control** | Gemeinschaften haben die Autorität, darüber zu bestimmen, wie ihre Sprachdaten erhoben, genutzt und geteilt werden. Ein hohes Leaderboard-Ergebnis erteilt keine Erlaubnis zur Veröffentlichung von Übersetzungen. |
| **Responsibility** | Forscher und Entwickler, die mit indigenen Sprachdaten arbeiten, tragen die Verantwortung, Beziehungen aufzubauen, Zustimmung einzuholen und Nutzen zu teilen. |
| **Ethics** | Die Rechte und das Wohlergehen indigener Völker müssen das vorrangige Anliegen sein. Übersetzungsmethoden sollten *mit* Gemeinschaften entwickelt werden, nicht *über* sie. |

---

## Te Mana Raraunga — Māori-Datensouveränität

**Te Mana Raraunga** ist das [Māori Data Sovereignty Network](https://www.temanararaunga.maori.nz/). Es vertritt die Auffassung, dass Māori-Daten — einschließlich Sprachdaten — ein taonga (Schatz) sind, der den Grundsätzen des Vertrags von Waitangi und der tikanga Māori (Māori-Gewohnheitsrecht) unterliegt.

Zentrale Prinzipien:

| Prinzip | Bedeutung |
|-----------|---------|
| **Rangatiratanga** (Autorität) | Māori haben ein angestammtes Recht, Autorität über ihre Daten auszuüben, einschließlich Sprachdaten. |
| **Whakapapa** (Beziehungen) | Daten haben Ursprünge und Verbindungen. Sprachdaten tragen die Beziehungen und das Wissen der Menschen in sich, die sie geschaffen haben. |
| **Whanaungatanga** (Verpflichtungen) | Diejenigen, die Māori-Daten halten oder verarbeiten, haben wechselseitige Verpflichtungen gegenüber den Gemeinschaften, aus denen die Daten stammen. |
| **Kotahitanga** (Kollektiver Nutzen) | Māori-Daten sollten zum kollektiven Nutzen der Māori verwendet werden. |
| **Manaakitanga** (Reziprozität) | Die Nutzung von Māori-Daten sollte mit Fürsorge, Respekt und Reziprozität verbunden sein. |
| **Kaitiakitanga** (Hüterschaft) | Datenhüter haben die Pflicht, die Daten zu schützen und ihre angemessene Nutzung sicherzustellen. |

Diese Grundsätze gelten für te reo Māori (die Māori-Sprache) und für jede rechnergestützte Arbeit, die Māori-Sprachdaten betrifft.

---

## Was dies für champollion-Nutzer bedeutet

### Für gängige Sprachen (Französisch, Japanisch, Spanisch ...)

Verwenden Sie champollion ganz normal. Diese Sprachen verfügen über große, öffentlich verfügbare Korpora, etablierte Übersetzungs-APIs und keine Souveränitätsbedenken. Übersetzen, synchronisieren und veröffentlichen Sie nach Belieben.

### Für indigene und ressourcenarme Sprachen

Die Situation ist grundlegend anders:

1. **Holen Sie zuerst die Zustimmung ein.** Bevor Sie eine Übersetzungsmethode für eine indigene Sprache entwickeln, bauen Sie eine Beziehung zur Gemeinschaft auf. Eine ohne Beteiligung der Gemeinschaft entwickelte Methode — so technisch beeindruckend sie auch sein mag — sollte nicht veröffentlicht oder verbreitet werden.

2. **Verwenden Sie die `api`-Methode.** Hosten Sie die Übersetzungs-Pipeline auf einer von der Gemeinschaft kontrollierten Infrastruktur. Die `api`-Methode in champollion ist dafür konzipiert: Sie sendet Schlüssel und erhält Übersetzungen zurück, ohne die Prompts, Wörterbücher oder Coaching-Daten offenzulegen, die die Methode funktionieren lassen.

    ```json title="Community-controlled setup"
    {
      "pairs": {
        "en:crk": {
          "method": "api",
          "endpoint": "https://api.community-server.example/translate"
        }
      }
    }
    ```

3. **Dokumentieren Sie alles.** Verwenden Sie das Feld `provenance` in Ihrem Plugin-Manifest, um jede Ressource, ihre Lizenz und die Frage aufzulisten, ob sie mit Zustimmung der Gemeinschaft bereitgestellt wurde.

4. **Ergebnisse sind keine Lizenzen.** Ein hohes Ergebnis auf dem Leaderboard belegt, dass eine Methode technisch gut funktioniert. Es erteilt keine Erlaubnis, Übersetzungen zu veröffentlichen, das Plugin zu verbreiten oder die Methode zu kommerzialisieren. Die Gemeinschaft entscheidet.

5. **Teilen Sie die Methode, nicht die Daten.** Wenn Sie eine Technik entwickeln, die gut funktioniert (z. B. „FST-gated LLM mit gecoachten Prompts“), teilen Sie die *Architektur* und den *Ansatz* auf dem Leaderboard. Die Gemeinschaft behält die Kontrolle über die linguistischen Daten, die die Methode für ihre spezifische Sprache funktionieren lassen.

---

## Die `api`-Methode und Souveränität

Die `api`-[Übersetzungsmethode](https://champollion.dev/docs/guides/translation-methods) existiert speziell, um die Datensouveränität zu unterstützen. Hier ist der Grund:

| Aspekt | Andere Methoden | `api`-Methode |
|--------|--------------|-------------|
| **Wo Prompts liegen** | In den Konfigurationsdateien von champollion (für alle Entwickler sichtbar) | Auf dem Server der Gemeinschaft (privat) |
| **Wo Coaching-Daten liegen** | Im Verzeichnis `.champollion/coaching/` (in git eingecheckt) | Auf dem Server der Gemeinschaft (privat) |
| **Wo Wörterbücher liegen** | Im Plugin-Verzeichnis (mit dem Plugin verteilt) | Auf dem Server der Gemeinschaft (privat) |
| **Wer die Pipeline kontrolliert** | Wer auch immer `champollion sync` ausführt | Die Gemeinschaft, die die API betreibt |
| **Was champollion sieht** | Alles | Schlüssel hinein, Übersetzungen hinaus |

Die `api`-Methode ist eine bewusste architektonische Entscheidung. Sie ist eine „dumme Leitung“, weil das geistige Eigentum — das linguistische Wissen, die Grammatikregeln, die sorgfältig kuratierten Coaching-Beispiele — der Gemeinschaft gehört, nicht dem Werkzeug.

Siehe [Eine Methode über eine API bereitstellen](https://champollion.dev/docs/guides/serving-a-method) für Implementierungsdetails.

---

## Fallstudie: OMT-1600 und Datensouveränität

Metas OMT-1600 (März 2026) liefert ein konkretes Beispiel dafür, warum Datensouveränität für indigene Sprachen von Bedeutung ist. OMT-1600 trainierte Übersetzungsmodelle für 1.600 Sprachen unter Verwendung von:

- **CC-2000-Web**: Einsprachiger Text, der per Web-Scraping aus mehr als 2.000 Languoiden gesammelt wurde — erhoben ohne Zustimmung der Gemeinschaften
- **Bibelübersetzungen**: Religiöse Texte, die als parallele Trainings- und Evaluierungsdaten für die Sprachen mit den geringsten Ressourcen verwendet wurden
- **MeDLEy**: Manuell kuratierter Bitext — jedoch ohne dokumentierte OCAP®- oder CARE-Konformität
- **Rückübersetzte synthetische Daten**: ~270 Millionen synthetische parallele Sätze, die von den Modellen selbst erzeugt wurden

Für indigene Sprachen wie Plains Cree (CRK) bedeutet dies:

| Prinzip | OMT-1600-Praxis | Auswirkung |
|-----------|-------------------|--------|
| **Ownership** | Meta besitzt die Modelle und entscheidet, wie sie veröffentlicht werden | Die Gemeinschaft hat keinen Eigentumsanteil daran, wie ihre Sprache modelliert wird |
| **Control** | Meta kontrolliert die Auswahl der Trainingsdaten, die Modellarchitektur und den Veröffentlichungszeitplan | Die Gemeinschaft hat keinen Einfluss darauf, welche Daten verwendet werden oder wie die Sprache dargestellt wird |
| **Access** | Die Modellgewichte sind derzeit nicht verfügbar — „nicht veröffentlicht aufgrund von Faktoren außerhalb der Kontrolle der Autoren“ | Die Gemeinschaft kann das Modell, das ihre Sprache spricht, nicht abrufen, prüfen oder verändern |
| **Possession** | Alle Daten und Modelle liegen auf Metas Infrastruktur | Die Gemeinschaft kann die zum Trainieren des Modells verwendeten Daten nicht hosten, prüfen oder löschen |

OMT-1600 ist eine Forschungsleistung. Es ist zugleich ein Beispiel für extraktive Datenpraxis: Linguistische Daten wurden aus dem Web und aus religiösen Texten gesammelt, zu einem Modell verarbeitet und als wissenschaftliche Arbeit veröffentlicht — alles ohne Beteiligung, Zustimmung oder Nutzenbeteiligung der Gemeinschaft.

**Genau dieses Muster verhindert die Souveränitätsarchitektur von champollion.** Die `api`-Methode hält linguistisches geistiges Eigentum auf von der Gemeinschaft kontrollierten Servern. Evaluierungskorpora werden mit Zustimmung der Gemeinschaft bereitgestellt und unter der Schlüsselverwahrung der Gemeinschaft gespeichert. Preisgekrönte Methoden gehen in das Eigentum der Gemeinschaft über. Der Unterschied ist nicht technischer, sondern ethischer und struktureller Natur.

:::note OMT-1600 trägt nicht allein die Schuld
Dieses Muster — Web-Scraping mit anschließendem Modelltraining ohne Zustimmung der Gemeinschaft — ist gängige Praxis in der massiv mehrsprachigen NLP-Forschung. OMT-1600 ist eine Fallstudie wegen seines Umfangs (1.600 Sprachen) und seiner Aktualität (März 2026), nicht weil es in einzigartiger Weise extraktiv wäre. Dieselbe Kritik gilt für NLLB-200, Googles mehrsprachige Bemühungen und die meisten groß angelegten MT-Forschungsvorhaben.
:::

---

## Weiterführende Literatur

- [First Nations Information Governance Centre — OCAP®](https://fnigc.ca/ocap-training/)
- [Global Indigenous Data Alliance — CARE-Prinzipien](https://www.gida-global.org/care)
- [Te Mana Raraunga — Māori Data Sovereignty Network](https://www.temanararaunga.maori.nz/)
- [USIDSN — United States Indigenous Data Sovereignty Network](https://usindigenousdata.org/)

---

## Siehe auch

- [Eine ressourcenarme Sprache unterstützen](/docs/community/low-resource-languages) — der technische Leitfaden mit OCAP-Kontext
- [Übersetzungsmethoden](https://champollion.dev/docs/guides/translation-methods) — die `api`-Methode und wie sie geistiges Eigentum schützt
- [Eine Methode über eine API bereitstellen](https://champollion.dev/docs/guides/serving-a-method) — eine von der Gemeinschaft kontrollierte Pipeline hosten
- [Plugin-Spezifikation](https://champollion.dev/docs/reference/plugin-spec) — das Feld `provenance` für die Ressourcenangabe
- [Kochbuch: FST-Gated Pipeline](/docs/tutorials/fst-gated-pipeline) — den Aufbau einer Pipeline, die eine Gemeinschaft selbst hosten kann