# neknihy
Neknihy is an application for managing rented books.
It works with some libraries in the Czech republic
so the rest is in Czech language only.

## Motivace

Některé knihovny v ČR půjčují i e-knihy, což je skvělé. Bohužel
mobilní aplikce pro čtení nemá moc dobré hodnocení a na velkém
množství čteček nefunguje dobře nebo vůbec.

Proto jsem vytvořil tuto aplikaci, která umožňuje pracovat
s výpujčkami na desktopu. Knihy je možné stáhnout do vybrané
složky odkud je snadno dostanete do čtečky tak, jak jste zvyklí.

Knihy lze po uplynutí výpůjční doby snadno vrátit (smazat z počítače)
přímo tlačítkem v aplikaci. Nezapomeňte knihu smazat také ze čtečky.

Účelem aplikace není nekalé kopírování, ale umožnit
lidem plnohodnotný čtenářský zážitek a komfort.

## Instalace

Aplikace nemá žádný instalační balíček. Funguje na Linuxu, Windows a
nejspíš i na Macu.

### Linux

Ze sekce ["Releases"](https://github.com/thalman/neknihy/releases)
si stáhnete balíček s aplikací na disk a nainstalujte ho

	sudo dnf install ./neknihy*.rpm

### Windows binární soubory

Ze sekce ["Releases"](https://github.com/thalman/neknihy/releases)
si stáhnete balíček (zip) pro windows na disk. Rozbalte ho a spusťte
aplikaci neknihy.exe

Některé antiviry mohou považovat stažené soubory za podezřelé.
V takovém případě buď nastavte vyjímku v antivirovém programu a nebo
nainstalujte aplikaci ze zdrojových kódů.

### Windows ze zdrojových kódů

Aplikace pro svůj běh potřebuje Python, stáhněte si a nainstaluje
[Python z oficiálního zdroje](https://www.python.org/downloads/windows/).
Při instalaci vyberte volbu "add python.exe to PATH".

Spusťe si příkazový řádek (cmd) a přesvěčte se, že Python je správně
nainstalován a je možné ho spustit

    c:\...> python --version
    Python 3.11.6

Stáhněte si [zdrojové kódy](https://github.com/thalman/neknihy/releases)
aplikace neknihy (Source code) a rozbalte je na disk. V příkazovém
řádku doinstalujte potřebné závislosti. Volitelně můžete změnit příponu
souboru z .py na .pyw:

    c:\...> cd .....\neknihy\src
    c:\...> python -m pip install -r REQUIREMENTS.txt
    c:\...> copy neknihy.py neknihy.pyw

Aplikace připravena k použití, spustíte ji poklikáním na soubor neknihy.py nebo
neknihy.pyw

### Ze zdrojového kódu

    git clone git@github.com:thalman/neknihy.git
    cd neknihy/src
    ./neknihy.py

## Podpora mobi a kindle

Pokud máte nainstalovanou aplikaci [Calibre](https://calibre-ebook.com/),
mohou Neknihy převést vypůjčenou publikaci do formátu `mobi` automaticky.
V záložce `Nastavení` zatrhněte volbu `Převádět na .mobi` a vyplňte cestu
k programu `ebook-convert` (součást Calibre).

## Screenshot

![mainwindow](contrib/screenshot.png "Screenshot")
