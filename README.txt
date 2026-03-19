RuuviTag-projektin verkkosivu

Käynnistys Visual Studio Codessa:
1. Avaa tämä kansio VS Codessa.
2. Avaa terminaali kansioon.
3. Luo virtuaaliympäristö:
   python -m venv .venv
4. Aktivoi ympäristö:
   Windows: .venv\Scripts\activate
   macOS/Linux: source .venv/bin/activate
5. Asenna riippuvuudet:
   pip install -r requirements.txt
6. Käynnistä sovellus:
   python app.py
7. Avaa selaimessa:
   http://127.0.0.1:5000

Missä muokataan sisältöä:
- Tiimin jäsenet: team.json
- Kuvien vaihto: static/images/
- Sivun rakenne: templates/index.html
- Tyylit: static/styles.css
- Dataa hakeva JavaScript: static/app.js
- Backend / SQLite API: app.py

Tietokanta:
- Sovellus käyttää tiedostoa ruuvi.sqlite3
- Jos tiedostoa ei ole tai se on tyhjä, sovellus luo demoarvot automaattisesti.
- Jos tuot oikean ruuvi.sqlite3-tiedoston tähän kansioon, sivu näyttää oikean mittausdatan.
