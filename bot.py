import hikari
import lightbulb
import json

# custom imports
from configuration.config import connection
from src.data.specs import Begabungen
from src.data.talents import Handeln, Kampf, Soziales, Wissen
from src.character import Character
from src.group import Group

bot = lightbulb.BotApp(
    token=connection["token"],
    default_enabled_guilds=connection["default_enabled_guilds"]
)

#################################################
# Dungeon Master
#################################################

@bot.command
@lightbulb.command("dm", "Dungeon Master command group.")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def dm(ctx):
    pass

@dm.child
@lightbulb.option("item", "Item")
@lightbulb.option("life", "Lebenspunkte")
@lightbulb.option("exp", "Exp")
@lightbulb.option("gold", "Gold")
@lightbulb.option("name", "Character name")
@lightbulb.command("loot", "Give loot to a character")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def loot(ctx):
    c = grp.get_character_by_name(ctx.options.name)
    c.changeGold(int(ctx.options.gold))
    c.changeExp(int(ctx.options.exp))
    c.changeLife(int(ctx.options.life))
    c.equipItem(json.loads(ctx.options.item))
    await ctx.respond(f"Belohnung verteilt von DM für char {ctx.options.name}")


@dm.child
@lightbulb.option("bonus", "Bonusschaden")
@lightbulb.option("wuerfel", "Anzahl W10 Würfel")
@lightbulb.option("name", "Character name")
@lightbulb.command("attack", "Attacks a character")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def attack(ctx):
    c = grp.get_character_by_name(ctx.options.name)
    dmg, block = c.beingAttacked(int(ctx.options.wuerfel), int(ctx.options.bonus))
    await ctx.respond(f"Charakter {ctx.options.name} bekommt {dmg} Schaden ({block} geblockt).")

#################################################
# Character Creation/Deletion
#################################################


@bot.command
@lightbulb.command("character", "Character command group.")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def character(ctx):
    pass


@character.child
@lightbulb.option("bio", "biography of the character, can be a longer description")
@lightbulb.option("sex", "gender of the character")
@lightbulb.option("role", "class of the character")
@lightbulb.option("age", "age of the character")
@lightbulb.option("name", "name of the character")
@lightbulb.command("create", "creates a character")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def create(ctx):
    if ctx.options.role not in Begabungen:
        await ctx.respond(f"{ctx.options.role} is not a valid spec. All available specs are as follows: {str(Begabungen)}.")
    new_character = Character(
        name=ctx.options.name,
        age=int(ctx.options.age),
        spec=ctx.options.role,
        sex=ctx.options.sex,
        bio=ctx.options.bio,
        grp=grp,
    )
    grp.add_character(new_character)
    new_character.set_group(grp)
    await ctx.respond("Character has been created successfully!")


@character.child
@lightbulb.option("id", "ID of the character")
@lightbulb.option("confirm", "please type 'CONFIRM'")
@lightbulb.command("delete", "deletes a character")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def delete(ctx):
    if ctx.options.confirm == "CONFIRM":
        deleted = grp.remove_character(int(ctx.options.id))
        if deleted:
            await ctx.respond(f"Character(s) with id {ctx.options.id} deleted successfully.")
        else:
            await ctx.respond(f"No character with the id {ctx.options.id}")
    else:
        await ctx.respond("you did not type 'CONFIRM' correctly.")

#################################################
# Schaden/Heilung würfeln
#################################################



#################################################
# Proben würfeln
#################################################s

@character.child
@lightbulb.option("bonus", "Bonus/Malus auf die Probe je nach Kontext.")
@lightbulb.option("knowledge_name", "knowledge name")
@lightbulb.option("character_name", "character name")
@lightbulb.command("probe_knowledge", "probe knowledge")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def probe_knowledge(ctx):
    for char in grp.get_characters():
        if char.name == ctx.options.character_name:
            answer = char.probe_knowledge(ctx.options.knowledge_name, int(ctx.options.bonus))
            await ctx.respond(answer)

@character.child
@lightbulb.option("bonus", "Bonus/Malus auf die Probe je nach Kontext.")
@lightbulb.option("action_name", "action name")
@lightbulb.option("character_name", "character name")
@lightbulb.command("probe_action", "probe action")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def probe_action(ctx):
    for char in grp.get_characters():
        if char.name == ctx.options.character_name:
            answer = char.probe_action(ctx.options.action_name, int(ctx.options.bonus))
            await ctx.respond(answer)


@character.child
@lightbulb.option("bonus", "Bonus/Malus auf die Probe je nach Kontext.")
@lightbulb.option("fight_name", "fight name")
@lightbulb.option("character_name", "character name")
@lightbulb.command("probe_fight", "probe fight")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def probe_action(ctx):
    for char in grp.get_characters():
        if char.name == ctx.options.character_name:
            answer = char.probe_fight(ctx.options.fight_name, int(ctx.options.bonus))
            await ctx.respond(answer)

@character.child
@lightbulb.option("bonus", "Bonus/Malus auf die Probe je nach Kontext.")
@lightbulb.option("social_name", "social name")
@lightbulb.option("character_name", "character name")
@lightbulb.command("probe_social", "probe social")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def probe_social(ctx):
    for char in grp.get_characters():
        if char.name == ctx.options.character_name:
            answer = char.probe_social(ctx.options.social_name, int(ctx.options.bonus))
            await ctx.respond(answer)

@character.child
@lightbulb.option("points", "points")
@lightbulb.option("talent", "Talent")
@lightbulb.option("character", "character name or id")
@lightbulb.command("skill", "Skill")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def skill(ctx):
    try:
        c = grp.get_character_by_id(int(ctx.options.character))
    except:
        c = grp.get_character_by_name(ctx.options.character)

    r = c.skill(ctx.options.talent, int(ctx.options.points))
    await ctx.respond(r)


#################################################
# Gruppen und Charakteranzeige
#################################################

@bot.command
@lightbulb.command("g", "group display")
@lightbulb.implements(lightbulb.SlashCommand)
async def g(ctx):
    await ctx.respond(str(grp))


@character.child
@lightbulb.option("name", "name of character to show")
@lightbulb.command("show", "prints the character list")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def list(ctx):
    not_found = True
    for c in grp.get_characters():
        if c.name == ctx.options.name:
            not_found = False
            await ctx.respond(str(c))
    if not_found:
        await ctx.respond("No such character found to show!")

#################################################
# Kampf
#################################################

@bot.command
@lightbulb.command("fight", "Initiativ-Werte berechnen.")
@lightbulb.implements(lightbulb.SlashCommand)
async def fight(ctx):
    for c in grp.get_characters():
        c.roll_initiative()  # neuer initiative wurf
    print_str = "Neue Initiative-Werte der Gruppe:"
    name_init_tuples = [(c.get_name_full(), c.get_initiative()) for c in grp.get_characters()]
    def tuple_sort_func(e):
        return -e[1]
    name_init_tuples.sort(key=tuple_sort_func)
    for i, t in enumerate(name_init_tuples):
        print_str += f"\n{i+1}. {t[0]} ({t[1]})"
    await ctx.respond(print_str)

#################################################
# Anzeige der möglichen Talentgruppen
#################################################

@bot.command
@lightbulb.command("tg", "Talentgruppen.")
@lightbulb.implements(lightbulb.SlashCommand)
async def tg(ctx):
    out = ""
    vars = [Handeln, Kampf, Soziales, Wissen]
    var_names = ["Handeln", "Kampf", "Soziales", "Wissen"]

    for idx, var in enumerate(vars):
        out += f"{var_names[idx]}\n"
        for key, val in var.items():
            out += f" - {key} "
            if "specs" in val:
                out += "["
                for spec_idx, spec in enumerate(val["specs"]):
                    out += f"{spec}"
                    if spec_idx != len(val["specs"]) - 1:
                        out += f", "
                out += "]"
            out += f"\n"
        out += "\n"
    await ctx.respond(out)

def helper_tg_spec(spec: str):
    out = ""
    vars = [Handeln, Kampf, Soziales, Wissen]
    var_names = ["Handeln", "Kampf", "Soziales", "Wissen"]

    for idx, var in enumerate(vars):
        out += f"{var_names[idx]}\n"
        for key, val in var.items():
            if not "specs" in val or spec in val["specs"]:
                out += f" - {key} "
                out += f"\n"
        out += "\n"
    return out


@bot.command
@lightbulb.command("tg_stark", "Talentgruppen.")
@lightbulb.implements(lightbulb.SlashCommand)
async def tg_stark(ctx):
    await ctx.respond(helper_tg_spec("stark"))

@bot.command
@lightbulb.command("tg_zäh", "Talentgruppen.")
@lightbulb.implements(lightbulb.SlashCommand)
async def tg_zäh(ctx):
    await ctx.respond(helper_tg_spec("zäh"))

@bot.command
@lightbulb.command("tg_distanziert", "Talentgruppen.")
@lightbulb.implements(lightbulb.SlashCommand)
async def tg_distanziert(ctx):
    await ctx.respond(helper_tg_spec("distanziert"))

@bot.command
@lightbulb.command("tg_agil", "Talentgruppen.")
@lightbulb.implements(lightbulb.SlashCommand)
async def tg_agil(ctx):
    await ctx.respond(helper_tg_spec("agil"))

@bot.command
@lightbulb.command("tg_elementar", "Talentgruppen.")
@lightbulb.implements(lightbulb.SlashCommand)
async def tg_elementar(ctx):
    await ctx.respond(helper_tg_spec("elementar"))

@bot.command
@lightbulb.command("tg_arkan", "Talentgruppen.")
@lightbulb.implements(lightbulb.SlashCommand)
async def tg_arkan(ctx):
    await ctx.respond(helper_tg_spec("arkan"))

@bot.command
@lightbulb.command("tg_besonnen", "Talentgruppen.")
@lightbulb.implements(lightbulb.SlashCommand)
async def tg_besonnen(ctx):
    await ctx.respond(helper_tg_spec("besonnen"))


# Initialisiere Gruppe mit gesicherten Daten
from os import listdir
from os.path import isfile, join

grp = Group()

onlyfiles = [f for f in listdir("chars") if isfile(join("chars", f))]
chars = [Character(id=int(fname.split(".")[0])).load_from_json("chars/" + fname) for fname in onlyfiles]
grp.set_characters(chars)
for char in chars:
    char.set_group(grp)

bot.run()

