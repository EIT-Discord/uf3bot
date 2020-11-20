import discord


def setup_start():
    embed = discord.Embed(description="Willkommen im Studenten-Setup zur automatischen \nRollenzuweisung "
                                      "unseres EIT-Servers! \n\nDas Setup ist dafür da, dass wir auch "
                                      "innerhalb \ndes Servers wissen, wer du bist und die __wichtigen "
                                      "\nInformationen auf deine Studiengruppe \nangepasst__ werden! "
                                      "\n\n*Deine Angaben werden __intern nicht gespeichert__, "
                                      "\nsondern direkt im EIT-Server geändert.* \n\n**Antworte jetzt bitte "
                                      "mit deinem vollständigen Namen (Vorname + Nachname)!**\n(Unten ist ein "
                                      "Eingabefeld, in dem du antworten kannst).",
                          colour=discord.Colour(0x2fb923),
                          title="Studenten-Setup")
    return add_quicklinks(embed)


def setup_name_error():
    embed = discord.Embed(description="Hoppla!\nDein eingegebener Name ist zu lang.\nGehe Sicher, "
                                      "dass deine Eingabe nicht länger als 32 Zeichen ist.",
                          colour=discord.Colour(0x2fb923),
                          title="Studenten-Setup")
    return add_quicklinks(embed)


def setup_group_select(name, eit):
    embed = discord.Embed(description=f'Hallo **{name}**, gib jetzt bitte noch deine Studiengruppe an, \ndamit '
                                      f'wir dich richtig zuordnen können.\nAnworte einfach mit einem der '
                                      f'untenstehenden Studiengruppen!\n\n__Folgende Studiengruppen stehen zur '
                                      f'Auswahl:__',
                          colour=discord.Colour(0x2fb923),
                          title="Studenten-Setup")

    # add embed_fields acording to study_groups in eitconfig
    for semester in eit.semester:
        group_string = ''
        for study_group in semester.study_groups:
            group_string += study_group.name + '\n'
        embed.add_field(name=semester.name, value=group_string, inline=True)
    return add_quicklinks(embed)


def setup_group_error():
    embed = discord.Embed(description='Hoppla!\nWie es scheint, ist {message} keine gültige Studiengruppe. \nProbiere '
                                      'es bitte nochmal mit einer Studiengruppe aus der Liste! \nIst deine '
                                      'Studiengruppe nicht dabei? \nDann kontaktiere bitte einen Admin (mit rotem '
                                      'Namen auf dem Server)!',
                          colour=discord.Colour(0x2fb923),
                          title="Studenten-Setup")
    return add_quicklinks(embed)


def setup_end(study_group):
    embed = discord.Embed(description=f'Vielen Dank für die Einschreibung in unseren EIT-Server. \nDu wurdest der '
                                      f'Studiengruppe **{study_group}** zugewiesen. \n\nHiermit hast du das Setup '
                                      f'abgeschlossen und deine Angaben \nwerden in den Server eingetragen. '
                                      f'\n\n__Falls etwas mit deiner Eingabe nicht stimmt, \nführe bitte einfach '
                                      f'nochmal das Setup aus und pass deine Eingabe an!__',
                          colour=discord.Colour(0x2fb923),
                          title="Studenten-Setup")
    return add_quicklinks(embed)


def add_quicklinks(embed):
    embed.add_field(name="__Quicklinks:__",
                    value="*[HM-Startseite](https://www.hm.edu/)*| "
                          "*[FK 04](https: // www.ee.hm.edu / aktuelles / stundenplaene / schwarzesbrett.de.html) *| "
                          "*[Moodle](https: // moodle.hm.edu / my) *| "
                          "*[Primuss](https: // www3.primuss.de / cgi - bin / login / index.pl?FH = fhm)*")
    return embed
