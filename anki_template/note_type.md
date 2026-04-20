# Anki-Notiztyp einrichten

## 1. Notiztyp erstellen

1. In Anki: **Werkzeuge → Notiztypen verwalten → Hinzufügen**
2. Wähle "Einfach hinzufügen" und nenne den Typ **"Russisch Vokabel"**
3. Klicke auf **"Felder..."** und erstelle diese 8 Felder (in dieser Reihenfolge):
   - `Russisch`
   - `Transliteration`
   - `Deutsch`
   - `Wortart`
   - `BeispielRU`
   - `BeispielDE`
   - `Level`
   - `Tags`

## 2. Kartenvorlagen einrichten

### Karte 1: Russisch → Deutsch

**Vorderseite:**
```html
<div class="russian">{{Russisch}}</div>
<div class="translit">{{Transliteration}}</div>
<div class="type">{{Wortart}}</div>
```

**Rückseite:**
```html
{{FrontSide}}
<hr id="answer">
<div class="german">{{Deutsch}}</div>
<div class="example">
  <div class="example-ru">{{BeispielRU}}</div>
  <div class="example-de">{{BeispielDE}}</div>
</div>
<div class="level">{{Level}}</div>
```

### Karte 2: Deutsch → Russisch

1. Klicke auf **"Karten..." → "+" (Karte hinzufügen)**

**Vorderseite:**
```html
<div class="german">{{Deutsch}}</div>
<div class="type">{{Wortart}}</div>
```

**Rückseite:**
```html
{{FrontSide}}
<hr id="answer">
<div class="russian">{{Russisch}}</div>
<div class="translit">{{Transliteration}}</div>
<div class="example">
  <div class="example-ru">{{BeispielRU}}</div>
  <div class="example-de">{{BeispielDE}}</div>
</div>
<div class="level">{{Level}}</div>
```

## 3. Styling (für beide Karten)

```css
.card {
    font-family: 'Segoe UI', Arial, sans-serif;
    text-align: center;
    padding: 2em;
    background: #fafafa;
}

.russian {
    font-size: 2em;
    color: #1a237e;
    margin-bottom: 0.2em;
}

.translit {
    font-size: 1.1em;
    color: #888;
    font-style: italic;
}

.german {
    font-size: 1.8em;
    color: #2e7d32;
    margin: 0.5em 0;
}

.type {
    font-size: 0.9em;
    color: #999;
    margin-top: 0.5em;
}

.example {
    margin-top: 1em;
    padding: 1em;
    background: #f0f0f0;
    border-radius: 8px;
    text-align: left;
}

.example-ru {
    font-size: 1.1em;
    margin-bottom: 0.3em;
}

.example-de {
    color: #666;
    font-style: italic;
}

.level {
    margin-top: 1em;
    font-size: 0.8em;
    color: #aaa;
}
```

## 4. Import

1. **Datei → Importieren**
2. Wähle die exportierte `.txt`-Datei
3. Trennzeichen: **Tabulator**
4. Notiztyp: **Russisch Vokabel**
5. Zuordnung prüfen:
   - Feld 1 → Russisch
   - Feld 2 → Transliteration
   - Feld 3 → Deutsch
   - Feld 4 → Wortart
   - Feld 5 → BeispielRU
   - Feld 6 → BeispielDE
   - Feld 7 → Level
   - Feld 8 → Tags
6. **Importieren** klicken
