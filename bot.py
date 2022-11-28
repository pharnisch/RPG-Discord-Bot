import hikari
import lightbulb
import json

# custom imports
from configuration.config import connection
from src.data.specs import Begabungen
from src.data.talents import Handeln, Kampf, Soziales, Wissen
from src.character import Character
from src.group import Group

grp = Group()

bot = lightbulb.BotApp(
    token=connection["token"],
    default_enabled_guilds=connection["default_enabled_guilds"]
)

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

@bot.listen(hikari.StartedEvent)
async def on_started(event):
    print("bot has started!")



@bot.command
@lightbulb.command("character", "Character command group.")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def character(ctx):
    pass

#@character.child
#@lightbulb.command("subcommand", "Group Subcommand")
#@lightbulb.implements(lightbulb.SlashSubCommand)



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

# @character.child
# @lightbulb.option("talent_points", "talent points you want to spend")
# @lightbulb.option("knowledge_name", "knowledge name")
# @lightbulb.option("character_name", "character name")
# @lightbulb.command("skill_knowledge", "skill knowledge")
# @lightbulb.implements(lightbulb.SlashSubCommand)
# async def skill_knowledge(ctx):
#     skill_success = False
#     for char in grp.get_characters():
#         if char.name == ctx.options.character_name:
#             enough_talent_points = char.skill_knowledge(ctx.options.knowledge_name, int(ctx.options.talent_points))
#             if not enough_talent_points:
#                 await ctx.respond("Not enough talent points")
#             else:
#                 skill_success = True
#                 await ctx.respond("Skilled successfully.")
#     if not skill_success:
#         await ctx.respond("Failed to skill knowledge.")
#
# @character.child
# @lightbulb.option("talent_points", "talent points you want to spend")
# @lightbulb.option("action_name", "action name")
# @lightbulb.option("character_name", "character name")
# @lightbulb.command("skill_action", "skill action")
# @lightbulb.implements(lightbulb.SlashSubCommand)
# async def skill_action(ctx):
#     skill_success = False
#     for char in grp.get_characters():
#         if char.name == ctx.options.character_name:
#             enough_talent_points = char.skill_action(ctx.options.action_name, int(ctx.options.talent_points))
#             if not enough_talent_points:
#                 await ctx.respond("Not enough talent points")
#             else:
#                 skill_success = True
#                 await ctx.respond("Skilled successfully.")
#     if not skill_success:
#         await ctx.respond("Failed to skill action.")
#
# @character.child
# @lightbulb.option("talent_points", "talent points you want to spend")
# @lightbulb.option("social_name", "social name")
# @lightbulb.option("character_name", "character name")
# @lightbulb.command("skill_social", "skill social")
# @lightbulb.implements(lightbulb.SlashSubCommand)
# async def skill_knowledge(ctx):
#     skill_success = False
#     for char in grp.get_characters():
#         if char.name == ctx.options.character_name:
#             enough_talent_points = char.skill_social(ctx.options.social_name, int(ctx.options.talent_points))
#             if not enough_talent_points:
#                 await ctx.respond("Not enough talent points")
#             else:
#                 skill_success = True
#                 await ctx.respond("Skilled successfully.")
#     if not skill_success:
#         await ctx.respond("Failed to skill knowledge.")


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

@character.child
@lightbulb.option("betrag", "Goldbetrag")
@lightbulb.option("character_name", "character name")
@lightbulb.command("gold", "Goldbetrag ändern")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def gold(ctx):
    for char in grp.get_characters():
        if char.name == ctx.options.character_name:
            answer = char.changeGold(int(ctx.options.betrag))
            await ctx.respond(answer)

@character.child
@lightbulb.option("betrag", "Expbetrag")
@lightbulb.option("character_name", "character name")
@lightbulb.command("exp", "Exp ändern")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def exp(ctx):
    for char in grp.get_characters():
        if char.name == ctx.options.character_name:
            answer = char.changeExp(int(ctx.options.betrag))
            await ctx.respond(answer)

@character.child
@lightbulb.option("betrag", "Lebenspunkte")
@lightbulb.option("character_name", "character name")
@lightbulb.command("leben", "Lebenspunkte anpassen")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def leben(ctx):
    for char in grp.get_characters():
        if char.name == ctx.options.character_name:
            answer = char.changeLife(int(ctx.options.betrag))
            await ctx.respond(answer)

@bot.command
@lightbulb.command("g", "group display")
@lightbulb.implements(lightbulb.SlashCommand)
async def g(ctx):
    await ctx.respond(str(grp))

# @bot.command
# @lightbulb.command("group", "Group command group.")
# @lightbulb.implements(lightbulb.SlashCommandGroup)
# async def group(ctx):
#     pass

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

# @group.child
# @lightbulb.command("save", "Alle Charaktere speichern.")
# @lightbulb.implements(lightbulb.SlashSubCommand)
# async def save(ctx):
#     import os.path
#     # delete old data
#     cwd = os.getcwd() + "/chars"
#     for f in os.listdir(cwd):
#         if not f.endswith(".json"):
#             continue
#         os.remove(os.path.join(cwd, f))
#     # save new data
#     current_id = 1
#     for c in grp.get_characters():
#         fname = f"chars/{current_id}.json"
#         while os.path.isfile(fname):
#             current_id += 1
#             fname = f"chars/{current_id}.json"
#         c.save_to_json(fname)
#     await ctx.respond("Characters saved successfully!")
#
#
# @group.child
# @lightbulb.command("load", "Alle Charaktere laden.")
# @lightbulb.implements(lightbulb.SlashSubCommand)
# async def load(ctx):
#     from os import listdir
#     from os.path import isfile, join
#     onlyfiles = [f for f in listdir("chars") if isfile(join("chars", f))]
#     chars = [Character(id=int(fname.split(".")[0])).load_from_json("chars/" + fname) for fname in onlyfiles]
#     grp.set_characters(chars)
#     for char in chars:
#         char.set_group(grp)
#     await ctx.respond("Characters loaded successfully!")

# @group.child
# @lightbulb.command("list", "prints the character list")
# @lightbulb.implements(lightbulb.SlashSubCommand)
# async def list(ctx):
#     await ctx.respond(str(grp))



@bot.command
@lightbulb.command("lol", "lllooollll.")
@lightbulb.implements(lightbulb.UserCommand)
async def lol(ctx):
    print(str(ctx.raw_options))
    ctx.respond("loli")

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







#@lightbulb.command("fight", "Initiativ-Werte berechnen.")
#@lightbulb.implements(lightbulb.SlashSubCommand)
#async def fight(ctx):

from os import listdir
from os.path import isfile, join
onlyfiles = [f for f in listdir("chars") if isfile(join("chars", f))]
chars = [Character(id=int(fname.split(".")[0])).load_from_json("chars/" + fname) for fname in onlyfiles]
grp.set_characters(chars)
for char in chars:
    char.set_group(grp)

bot.run()

