# 🔧 OpenRouter Configuration Checklist

## BELANGRIJKE VRAAG: Wat zijn JOUW OpenRouter instellingen?

### 1. Site Restrictions / Whitelisting
**Check**: https://openrouter.ai/settings

Kijk bij:
- [ ] **Site Verification / Allowed Origins**
- [ ] **HTTP-Referer Restrictions**

**Vraag**: Staan daar specifieke websites toegestaan?
- Bijv: `cursor.sh`, `cursor.com`, `localhost`, etc?
- Als JA → dat is waarschijnlijk het probleem!

### 2. API Key Permissions
**Check**: https://openrouter.ai/keys

Bij jouw key:
- [ ] **Scope/Permissions**: Welke zijn aangevinkt?
- [ ] **IP Restrictions**: Zijn specifieke IPs toegestaan?
- [ ] **Rate Limits**: Custom limits ingesteld?

### 3. Account Settings
**Check**: https://openrouter.ai/account

- [ ] **Credits Balance**: Hoeveel $ heb je?
- [ ] **Payment Method**: Ingesteld?
- [ ] **Account Status**: Active/Verified?

### 4. Cursor Configuratie
**Vraag**: Hoe heb je OpenRouter in Cursor ingesteld?

Optie A - Via Cursor Settings:
```
Cursor → Settings → Models → Add Custom Model Provider
  - Provider: OpenRouter
  - API Key: sk-or-v1-...
  - Base URL: ??? (welke URL staat hier?)
```

Optie B - Via Extension/Plugin:
```
Welke extension?
Welke settings?
```

### 5. Test in OpenRouter Playground
**Actie**: Ga naar https://openrouter.ai/playground

Test daar:
1. Selecteer model: `moonshotai/kimi-k2`
2. Type iets simpel: "hi"
3. Werkt het?

Als het daar NIET werkt → account probleem
Als het daar WEL werkt → configuratie verschil

---

## 🎯 Meest Waarschijnlijke Oorzaak

Als het werkt in Cursor maar niet in onze code, is het waarschijnlijk:

### Scenario 1: Site Whitelisting ⭐ MEEST WAARSCHIJNLIJK
```
In OpenRouter Dashboard → Settings → Allowed Origins
Staat daar: "cursor.sh" of "*.cursor.sh"?

FIX: Voeg toe:
- "localhost"
- "moon.dev"
- Of verwijder alle restricties (maak het open)
```

### Scenario 2: Cursor gebruikt andere endpoint
```
Cursor gebruikt misschien:
- https://openrouter.ai/api/v1 (standaard) ✓
- Of een proxy: https://cursor.openrouter.ai/api/v1 ?
```

### Scenario 3: Cursor voegt speciale headers toe
```
Mogelijk:
- X-OpenRouter-Site: "cursor.sh"
- Origin: "https://cursor.sh"
- Custom User-Agent
```

---

## 📋 Wat ik nu nodig heb van jou:

1. **Screenshot of tekst van OpenRouter Settings**
   - Vooral "Site Verification" sectie
   - Allowed Origins

2. **Cursor Settings screenshot**
   - Hoe OpenRouter is geconfigureerd
   - Welke Base URL gebruikt het?

3. **OpenRouter Playground test**
   - Werkt `moonshotai/kimi-k2` daar?

---

## 🚀 Snelle Test

Als je wil, kun je ook:

1. **Tijdelijk alle restricties uitschakelen** in OpenRouter dashboard
2. **Opnieuw testen** met onze code
3. Als het dan werkt → we weten dat het site restrictions zijn!

Laat me weten wat je vindt in de OpenRouter dashboard! 🔍
