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
@lightbulb.option("mana", "Manapunkte")
@lightbulb.option("life", "Lebenspunkte")
@lightbulb.option("exp", "Exp")
@lightbulb.option("silber", "Silber")
@lightbulb.option("name", "Character name")
@lightbulb.command("loot", "Give loot to a character")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def loot(ctx):
    c = grp.get_character_by_name(ctx.options.name)
    gold_change = int(ctx.options.silber)
    c.changeGold(gold_change)
    exp_change = int(ctx.options.exp)
    c.changeExp(exp_change)
    life_change = int(ctx.options.life)
    c.changeLife(life_change)
    mana_change = int(ctx.options.mana)
    c.changeMana(mana_change)
    equip_item = json.loads(ctx.options.item)
    c.equipItem(equip_item)

    s = f"DM-Änderung bei {c.name}:\n"
    if gold_change != 0:
        s += f" * Silber: {gold_change}\n"
    if exp_change != 0:
        s += f" * Exp: {exp_change}\n"
    if life_change != 0:
        s += f" * Life: {life_change}\n"
    if mana_change != 0:
        s += f" * Mana: {mana_change}\n"
    if isinstance(equip_item, dict):
        s += f" * Item: {equip_item}\n"
    await ctx.respond(s)
    #await ctx.respond(f"Belohnung verteilt von DM für char {ctx.options.name}")


@dm.child
@lightbulb.option("bonus", "Bonusschaden")
@lightbulb.option("wuerfel", "Anzahl W20 Würfel")
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
@lightbulb.option("spec", "spec of the character")
@lightbulb.option("age", "age of the character")
@lightbulb.option("name", "name of the character")
@lightbulb.command("create", "creates a character")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def create(ctx):
    if ctx.options.spec not in Begabungen:
        await ctx.respond(f"{ctx.options.spec} is not a valid spec. All available specs are as follows: {str(Begabungen)}.")
        return
    new_character = Character(
        user_id=ctx.author.id,
        name=ctx.options.name,
        age=int(ctx.options.age),
        spec=ctx.options.spec,
        sex=ctx.options.sex,
        bio=ctx.options.bio,
        grp=grp,
    )
    grp.add_character(new_character)
    grp.save()
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

@bot.command
@lightbulb.option("bonus", "Bonusschaden")
@lightbulb.option("wuerfel", "Anzahl W20 Würfel")
@lightbulb.command("a", "attack")
@lightbulb.implements(lightbulb.SlashCommand)
async def a(ctx):
    c = grp.get_character_by_user_id(ctx.author.id)
    wuerfel, bonus = c.attack(int(ctx.options.wuerfel), int(ctx.options.bonus))
    await ctx.respond(f"Charakter {c.name} macht {wuerfel} + {bonus} = {sum(wuerfel)+bonus} Schaden.")

@bot.command
@lightbulb.option("bonus", "Bonusschaden")
@lightbulb.option("wuerfel", "Anzahl W20 Würfel")
@lightbulb.command("h", "heal")
@lightbulb.implements(lightbulb.SlashCommand)
async def h(ctx):
    c = grp.get_character_by_user_id(ctx.author.id)
    wuerfel, bonus = c.attack(int(ctx.options.wuerfel), int(ctx.options.bonus))
    await ctx.respond(f"Charakter {c.name} wirkt {wuerfel} + {bonus} = {sum(wuerfel)+bonus} Heilung.")

#################################################
# Proben würfeln
#################################################s

@bot.command
@lightbulb.option("bonus", "Bonus/Malus auf die Probe je nach Kontext.")
@lightbulb.option("talent_name", "talent name")
@lightbulb.command("p", "probe")
@lightbulb.implements(lightbulb.SlashCommand)
async def p(ctx):
    c = grp.get_character_by_user_id(ctx.author.id)
    answer = c.probe_allgemein(ctx.options.talent_name, int(ctx.options.bonus))
    await ctx.respond(answer)


@bot.command
@lightbulb.option("points", "points")
@lightbulb.option("talent", "Talent")
#@lightbulb.option("character", "character name or id")
@lightbulb.command("skill", "Skill")
@lightbulb.implements(lightbulb.SlashCommand)
async def skill(ctx):
    # try:
    #     c = grp.get_character_by_id(int(ctx.options.character))
    # except:
    #     c = grp.get_character_by_name(ctx.options.character)
    c = grp.get_character_by_user_id(ctx.author.id)

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


@bot.command
@lightbulb.command("mc", "my full character display")
@lightbulb.implements(lightbulb.SlashCommand)
async def mc(ctx):
    chara = grp.get_character_by_user_id(ctx.author.id)
    await ctx.respond(chara.full_str())

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

