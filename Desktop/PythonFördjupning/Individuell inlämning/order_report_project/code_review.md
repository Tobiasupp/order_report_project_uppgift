# Code Review: Order Report System

## 1. Avsaknad av modularisering och funktioner (Ansvarsfördelning)
 **Observation:**
 Hela skriptet körs som ett enda linjärt block i globalt scop. Filinläsning, datastädning, beräkningar och filskrivning är sammanflätade i ett `try-except`-block.
 **Konsekvens:** 
Koden är svår att läsa, återanvända och teststänga. Det går inte att enhetstesta datatransformationerna utan att läsa in en faktisk fil eller skriva till disken.
 **Förslag:** 
Dela upp skriptet i funktioner alternativt separata moduler

## 2. Kodduplicering i aggregeringar (`result1`, `result2` och `returns_by_category`)
 **Observation:** 
Beräkningarna för `result1` (per kategori) och `result2` (per region) är helt identiska förutom grupperingskolumnen. Dessutom skapar `returns_by_category` en delvis överflödig datamängd då samma returdata redan beräknats i `result1`.
 **Konsekvens:** 
Om beräkningslogiken för försäljning eller returer behöver ändras måste det göras på flera ställen, vilket ökar risken för buggar och felaktiga rapporter.
 **Förslag:**
  Skapa en generisk hjälpfunktion (t.ex. `aggregate_by_column(df, group_col)`) som tar emot den kolumn man vill gruppera på och returnerar den aggregerade datamängden.

## 3. Skör hantering av fil- och mappsökvägar
 **Observation:** 
 Fil- och mappsökvägar är definierade som hårdkodade relaterade strängar (`"data/orders.csv"` och `"output"`). Dessutom saknas kontroll för om mappen `output` faktiskt existerar innan filerna sparas.
 **Konsekvens:** 
 Om skriptet exekveras från en annan arbetsmapp kraschar det (vilket ger `FileNotFoundError`), och om mappen `output` saknas misslyckas skrivningen.
 **Förslag:**
  Använd Pythons `pathlib.Path` för att skapa dynamiska sökvägar baserade på skriptfilens placering (`Path(__file__).resolve().parent`). Skapa även mappen automatiskt med `output_dir.mkdir(parents=True, exist_ok=True)`.

## 4. Ospecifik felhantering och svag felrapportering
 **Observation:** 
 Skriptet fångar alla fel med `except Exception as error` och kastar ett ospecifikt `raise Exception("Fel data")` om obligatoriska kolumner saknas.
 **Konsekvens:** 
 Den ospecifika catch-blocket döljer värdefull traceback-information vid oväntade krascher (t.ex. vid saknade bibliotek eller minnesfel). Det gör det svårt att felsöka under utveckling och drift.
 **Förslag:** 
 Fånga specifika undantag (`FileNotFoundError`, `pd.errors.EmptyDataError`, `KeyError`) och ge tydliga felmeddelanden. Använd `ValueError` istället för den generella `Exception` för valideringsfel.

## 5. Brister i logging och användaråterkoppling
 **Observation:** 
 Programmet använder enkla `print()`-satser för att skriva ut statusmeddelanden direkt till konsolen.
 **Konsekvens:** 
 Det finns ingen möjlighet att styra loggnivåer (t.ex. `DEBUG`, `INFO`, `ERROR`) eller rikta utskrifterna till en loggfil vid automatiserad körning (t.ex. via cronjobs eller CI/CD pipelines).
 **Förslag:** 
 Ersätt `print()`-satserna med Pythons inbyggda `logging`-modul.

## 6. Otydlig och intetsägande namngivning
 **Observation:** 
 Variabelnamn som `result1`, `result2`, `required` och `data` är väldigt generella och förklarar inte vad de innehåller.
 **Konsekvens:** 
 Utomstående utvecklare (eller du själv om några månader) måste läsa hela kodblocket för att förstå vad innehållet i variablerna faktiskt representerar.
 **Förslag:** 
 Döper om till beskrivande namn, exempelvis `category_metrics_df`, `region_metrics_df`, `required_columns` och `orders_df`.