# Blur Container

Der Ordner `blur_container` enthält den Service, der hochgeladene Bilder auf Personen untersucht und erkannte Personenbereiche verpixelt.

## Aufgabe des Services

Der Blur-Service nimmt ein Bild als Upload entgegen, erkennt darauf Personen mit einem MediaPipe-Objektdetektor und gibt das bearbeitete Bild als JPEG zurück. Dabei wird nicht das komplette Bild verändert, sondern nur die Bounding Boxes der erkannten Kategorie `person`.

Typischer Ablauf:

1. Ein Bild wird per HTTP-Upload an den Service gesendet.
2. OpenCV liest die Bilddaten aus den empfangenen Bytes.
3. MediaPipe erkennt Personen im Bild.
4. Die erkannten Personenbereiche werden mit einem Gaussian Blur weichgezeichnet.
5. Das Ergebnis wird als `image/jpeg` zurückgegeben.

## Aufbau des Ordners

```text
blur_container/
├── README.txt
├── blur_app.py
├── blurring.py
├── blur_containerfile
└── models/
    └── efficientdet_lite2.tflite
```

### `blur_app.py`

`blur_app.py` ist der FastAPI-Einstiegspunkt des Services.

Wichtige Bestandteile:

- erstellt die FastAPI-App `person-blur-service`
- lädt den MediaPipe-Detektor beim Start der Anwendung
- schließt den Detektor beim Beenden wieder sauber
- stellt die API-Endpunkte bereit

Der Detektor wird einmal beim Start erzeugt und in `app.state.detector` gespeichert. Dadurch muss das Modell nicht bei jedem Request neu geladen werden.

### `blurring.py`

`blurring.py` enthält die eigentliche Bildverarbeitung.

Wichtige Funktionen:

- `create_detector()`: konfiguriert und erstellt den MediaPipe Object Detector
- `blur_people_in_image_bytes(image_bytes, detector)`: verarbeitet ein Bild aus Bytes und gibt das weichgezeichnete JPEG wieder als Bytes zurück

Der Detektor nutzt das Modell:

```text
models/efficientdet_lite2.tflite
```
https://ai.google.dev/edge/mediapipe/solutions/vision/object_detector?hl=de#efficientdet-lite2_model

Er ist auf folgende Erkennung eingeschränkt:

- Kategorie: `person`
- Mindest-Konfidenz: `0.2`
- Modus: Einzelbild-Verarbeitung (`IMAGE`)

### `blur_containerfile`

Das Containerfile beschreibt, wie der Blur-Service gebaut und gestartet wird.

Wichtige Punkte:

- Basisimage: `python:3.12-trixie`
- Arbeitsverzeichnis im Container: `/blur_container`
- installiert Systembibliotheken, die OpenCV und MediaPipe benötigen
- installiert Python-Abhängigkeiten aus der zentralen `requirements.txt` im Projektroot
- startet den Service mit Uvicorn auf Port `9001`

Startkommando im Container:

```bash
uvicorn blur_app:app --host 0.0.0.0 --port 9001
```

## API

### Health Check

```http
POST /api/blur/health
```

Antwort:

```json
{
  "status": "online"
}
```

Dieser Endpunkt wird von der Hauptanwendung über `/blur_status` abgefragt.

### Bild weichzeichnen

```http
POST /api/blur/blurring
```

Erwartet ein Multipart-Form-Upload-Feld mit dem Namen `file`.

Beispiel mit `curl`, wenn der Container lokal auf Port `9001` erreichbar ist:

```bash
curl -X POST \
  -F "file=@bild.jpg" \
  http://localhost:9001/api/blur/blurring \
  --output blurred.jpg
```

Antwort:

- Erfolgreich: JPEG-Bild (`image/jpeg`)
- Fehlerhaftes Bild: HTTP `400`
- Interner Verarbeitungsfehler: HTTP `500`

## Einbindung in das Gesamtprojekt

In `compose.yaml` ist der Service unter dem Namen `blurring` definiert:

```yaml
blurring:
  build:
    context: .
    dockerfile: blur_container/blur_containerfile
  volumes:
    - ./blur_container:/blur_container:z
  ports:
    - "9001:9001"
```

Die Hauptanwendung ruft den Service intern über diesen Compose-Namen auf:

```text
http://blurring:9001/api/blur/blurring
```

Nach außen ist der Blur-Service zusätzlich auf dem lokalen Port `9001` erreichbar. Die normale Bedienung läuft aber über die Hauptanwendung auf Port `9000`.

## Starten

Aus dem Projektroot:

```bash
docker compose up --build
```

oder mit Podman:

```bash
podman compose up --build
```

Danach:

- Hauptanwendung: `http://localhost:9000`
- Blur-Service direkt: `http://localhost:9001`

## Wichtige Abhängigkeiten

Die Python-Abhängigkeiten liegen aktuell in der zentralen Datei `requirements.txt` im Projektroot. Für diesen Service sind besonders relevant:

- `fastapi`
- `uvicorn`
- `python-multipart`
- `mediapipe`
- `opencv-python` / `opencv-contrib-python`
- `numpy`

Zusätzlich installiert das Containerfile Systembibliotheken wie `libgl1`, `libglib2.0-0` und weitere Pakete, die für OpenCV/MediaPipe im Container benötigt werden.

## Fehlerquellen

- Fehlt `models/efficientdet_lite2.tflite`, startet der Detektor nicht.
- Wird kein gültiges Bild hochgeladen, gibt der Service HTTP `400` zurück.
- Wenn keine Person erkannt wird, wird das Bild trotzdem als JPEG zurückgegeben, aber ohne sichtbare Weichzeichnung.
- Bei sehr großen Bildern kann die Verarbeitung länger dauern, da Erkennung und Blur auf dem kompletten Bild laufen.
- Der Service erwartet das Upload-Feld `file`. Ein anderer Feldname führt zu einem Request-Fehler.
