Installation:

Gehe auf Discord und suche unter Einstellungen den Reiter Advanced.
Dort klickst du auf Developer Mode und DiscordAPI, nun öffnet sich eine Internetseite.
Hier suchst du nun den Button CreateApplication. Du musst dich mit deinem Discord Account anmelden.

Auf der Internetseite registrierst du nun eine eigene Anwendung und lässt dir für diese ein
Eigenes Token geben. Diesen Token bitte nicht weitergeben und immer als Schlüssel für deinen Quellcode verwenden. 

in der Datei bot.py findest du folgenden Abschnitt auf Zeile 4:

bot = lightbulb.BotApp(
    token="******************************************************************",#             Hier kommt dein Token rein welcher als Schlüssel dient.
    default_enabled_guilds=(*********************)                             #             Hier kommt die ID des Servers rein auf dem der Bot laufen soll.

Die Server ID findest du indem du in Discord auf deinen Testserver rechtsklickst und "Copy ID" auswählst.

Auf diese Weise kannst du dir einen eigenen Testserver einrichten auf dem deine Entwicklungsversion läuft. 
So verhindern wir dass sich Fehler über mehrere Testserver verbreiten und halten die Reaktionszeit des Bots gering.

Nun unter dem Reiter "Bot" den Bot einrichten und ihm über den Reiter "Oauth2" den Haken bei
"Bot" und "Administrator" geben. Zu guter Letzt den Reiter "Generate URL" auswählen und den Bot über
die generierte URL auf deinen Server einladen.


Entwicklung der Software:

Binde diesen Ordner in deine IDE ein. 
Ich nutze Visual Studio Code, andere IDE mit integriertem Terminal sind ebenfalls nützlich.

Als nächstes richtest du den Ordner "pap" als Virtuelle Umgebung ein.
py -m venv pap

Das tun wir um zu verhindern dass die importierten Bibliotheken in die Standardintialisierung von Python geladen werden.
So müssen wir nicht gleich ganz Python neu installeren wenn mal ein fehlerhaftes Update einer Bibliothek rein kommt.

Als nächstes Aktivierst du die Nutzung von Skripts in diesem und allen Unterordnern.
/pap/Scripts/activate.bat (Windows: pap\Scripts\activate.bat)

Um den Quellcode zu bearbeiten öffne bot.py in deiner IDE.

Um den Bot zu starten gehe ins Terminal deiner IDE und nutze diesen Befehl im cmd Terminal:
py bot.py

Nun friert dein Terminal ein und sollte dir eine Meldung ausspucken was bedeutet dass dein Bot nun online ist.
Jetzt kannst du in Discord die Programmierten Befehle austesten. 
Nach dem Testen das Terminal wieder schließen um weiter zu coden.
Um Code zu testen Terminal wieder starten und warten bis der Bot läuft.