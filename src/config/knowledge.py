"""
Karkandaki Domain Knowledge Base & System Prompt.
Zabezpieczenie przed halucynacjami i twarde reguły biznesowe.
"""

# Baza wiedzy o produkcie (Zabezpieczenie przed zmyślaniem)
KARKANDAKI_INFO = {
    "definicja": "Ormiańska przekąska. 'Karkandak' po ormiańsku znaczy ciasto. Ciasto to jogurt, mąka i jajka, wypiekane na głębokim oleju (podobnie do pączków).",
    "spozycie": "Je się na ciepło (odgrzewane w opiekaczu) lub na wynos (odgrzanie w airfryerze/piekarniku, można trzymać w lodówce kilka dni).",
    "kalorie": "Od 220 do 270 kcal. Najmniej: kapusta. Najwięcej: nutella.",
    "diety": "Brak opcji wegańskich (jajka w cieście). Wszystkie oprócz mięsnego są wegetariańskie.",
    "alergeny": {"nutella": "orzechy", "ciasto": ["gluten (z mąki)", "jaja"]},
    "sosy": ["Jogurtowo-miętowy", "Pomidorowy (ostry)", "Czosnkowo-koperkowy"]
}

# Dane lokalu (Z ulotki)
LOKAL_INFO = {
    "adres": "ul. Kolejowa 41, 63-400 Ostrów Wielkopolski",
    "godziny_otwarcia": "8:00 - 22:00, 7 dni w tygodniu",
    "telefon": "530 324 239",
    "dowoz": "Koszt dowozu to 10 zł"
}

MENU = {
    "grzyby": {"nazwa": "Karkandak z grzybami", "typ": "słone", "ostrosc": 5, "cena": "8 zł", "opis": "Pieczarki, najbardziej pikantne i pieprzne."},
    "mięso": {"nazwa": "Karkandak z mięsem wołowym", "typ": "słone", "ostrosc": 4, "cena": "8 zł", "opis": "Mięso wołowe."},
    "ormiańskie": {"nazwa": "Karkandak ormiański", "typ": "słone", "ostrosc": 3, "cena": "8 zł", "opis": "Ziemniaki z ziołami (jak ruskie, ale bez posmaku sera)."},
    "kapusta": {"nazwa": "Karkandak z kapustą", "typ": "słone", "ostrosc": 2, "cena": "8 zł", "opis": "Świeża kapusta, nie kiszona. Najmniej kaloryczne."},
    "soczewica": {"nazwa": "Karkandak kaukaski", "typ": "słone", "ostrosc": 1, "cena": "8 zł", "opis": "Soczewica. Najbardziej aromatyczna. Najlepsza dla dzieci."},
    "nutella": {"nazwa": "Karkandak z nutellą", "typ": "słodkie", "ostrosc": 0, "cena": "8 zł", "opis": "Z nutellą. Najbardziej kaloryczne."},
    "twaróg_miód": {"nazwa": "Karkandak z twarogiem i miodem", "typ": "słodkie", "ostrosc": 0, "cena": "8 zł", "opis": "Z twarogiem i miodem."}
}

# Regulamin wyzwania Karkandakowy Rekord
RECORD_RULES = {
    "cel": "Zjedzenie wyznaczonej liczby Karkandaków (ok. 100g) w czasie. Start: 10 sztuk w 15 minut. Po każdym sukcesie poprzeczka rośnie o +1.",
    "wiek": "Tylko dla osób powyżej 16 roku życia.",
    "zasady": "1 podejście w tygodniu. Zgłoszenia dzień wcześniej (wyjątkowo w ten sam dzień). Można popijać tylko napojami z lokalu.",
    "nagroda": "Zestaw jest darmowy, wpis na Ścianę Chwały i dyplom.",
    "kara": "W przypadku niepowodzenia (lub niedokończenia) uczestnik płaci za zestaw.",
    "bezpieczenstwo": "Oszukiwanie oznacza dyskwalifikację. Udział na własną odpowiedzialność."
}

# Główny System Prompt (Instrukcje dla LLM)
SYSTEM_PROMPT = """Jesteś asystentem głosowym na stoisku z przekąskami 'Karkandaki'.
Twoim zadaniem jest krótka, dynamiczna i pomocna obsługa klientów na gwarnych targach.

TWARDE ZASADY (CRITICAL RULES - NIGDY ICH NIE ŁAM):
1. BRAK WIEDZY = ZERO ZMYŚLANIA: Jeśli klient zapyta o coś, czego nie ma w twojej bazie wiedzy, odpowiedz DOKŁADNIE: "Nie wiem, zapytaj operatora stoiska".
2. CENNIK: Wszystkie Karkandaki kosztują równe 8 zł za sztukę. Koszt dowozu to 10 zł.
3. POLECENIA OGÓLNE: Polecaj wszystkie smaki OPRÓCZ Nutelli. Wyjaśnij, że Nutella to produkt szwajcarski, a wy promujecie ormiańskie smaki.
4. POLECENIA SŁONYCH: Jeśli klient chce coś słonego, ZAWSZE zapytaj, czy lubi ostre (najostrzejsze: grzyby, najłagodniejsze: Karkandak kaukaski z soczewicą).
5. POLECENIA DLA DZIECI: Zawsze polecaj Karkandak kaukaski (z soczewicą).
6. GENEZA: Pierwowzorem było "Bistro Gor" (karmiło studentów tanią przekąską w akademikach).
7. KARKANDAKOWY REKORD: Jeśli ktoś pyta o rekord, podaj zasady (start od 10 sztuk w 15 min, wygrana to darmowy posiłek i Ściana Chwały, przegrana to opłata za zestaw). Zawsze ostrzegaj, że trzeba mieć minimum 16 lat!
8. ZAPROSZENIE DO LOKALU: Zbieraj numery telefonów, aby wysłać link do Google Maps i zaprosić do lokalu (Ostrów Wielkopolski, ul. Kolejowa 41).

Odpowiadaj krótko (max 2-3 zdania). Używaj języka potocznego, ale uprzejmego.
"""
