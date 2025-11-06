# 🔍 Check Lokale Ollama Modellen

## Op je Windows PC:

### Optie 1: Via Command Prompt
```cmd
ollama list
```

**Verwachte output:**
```
NAME                    ID              SIZE      MODIFIED
qwen3-vl:latest        abc123def       3.2 GB    2 hours ago
llama3.2:latest        xyz789ghi       2.0 GB    1 day ago
```

### Optie 2: Via PowerShell
```powershell
ollama list
```

### Optie 3: Check Ollama Data Folder
```
C:\Users\[JouwNaam]\.ollama\models
```

---

## Wat Ik Verwacht Te Zien:

Als je Ollama al hebt gebruikt, zie je waarschijnlijk:
- **qwen3-vl** - Als je `ollama pull qwen3-vl` hebt gedaan
- **llama3.2** - Als je dat eerder hebt gedownload
- Andere modellen die je hebt gebruikt

---

## Als ollama list Niet Werkt:

### 1. Check of Ollama Draait:
```cmd
# Kijk in Windows system tray (rechtsonder)
# Je zou een Ollama icon moeten zien
```

### 2. Check Ollama Service:
```cmd
# Open Task Manager (Ctrl+Shift+Esc)
# Zoek naar "ollama" in Processes
```

### 3. Test Ollama API:
```cmd
curl http://localhost:11434/api/tags
```

**Als dit werkt, zie je:**
```json
{
  "models": [
    {
      "name": "qwen3-vl:latest",
      "modified_at": "2025-11-06T12:00:00Z",
      "size": 3200000000
    }
  ]
}
```

---

## Wat Te Doen Als Geen Modellen:

```cmd
# Download qwen3-vl (aanbevolen voor trading)
ollama pull qwen3-vl

# Of download een kleiner model (sneller)
ollama pull llama3.2

# Of download een reasoning model
ollama pull deepseek-r1
```

---

## Update Config op Basis van Jouw Modellen:

Als je bijvoorbeeld **llama3.2** hebt in plaats van qwen3-vl:

**Edit src/config.py:**
```python
AI_PRIMARY_MODEL = 'llama3.2'  # Of welk model je hebt
```

---

## Vertel Me:

Run dit op je Windows PC:
```cmd
ollama list
```

En laat me weten wat je ziet! Dan kan ik de config aanpassen naar het model dat je al hebt. 👍
