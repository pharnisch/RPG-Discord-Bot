import hikari
import lightbulb
import random
import json
import os


Begabungen = [
    "zäh",
    "stark",
    "agil",
    "besonnen",
    "arkan",
    "elementar",
    "distanziert",
]

Handeln = {
    #"Klettern": {},
    #"Schwimmen": {},
    #"Sprinten": {},
    "Athletik": {},
    "Verborgenheit": {},
    "Heben": {},
    "Überlebenskünstler": {},

    # Berufserweiterung
    #"Metallverarbeitung": {},
    #"Holzverarbeitung": {},
    #"Schneiderei": {},
    #"Kochen": {},
    #"Angeln": {},
}

Kampf = {
    "Nahkampf (Faust)": {},
    "Nahkampf (Leicht)": {},
    "Nahkampf (Schwer)": {"specs": ["stark"]},
    "Fernkampf (Spann)": {"specs": ["distanziert"]},
    "Fernkampf (Wurf)": {"specs": ["distanziert", "agil", "besonnen", "zäh", "stark"]},
    "Fernkampf (Schuss)": {"specs": ["distanziert", "agil", "besonnen"]},
    "Parieren": {},
    "Feuermagie": {"specs": ["elementar"]},
    "Erdmagie": {"specs": ["elementar"]},
    "Luftmagie": {"specs": ["elementar"]},
    "Wassermagie": {"specs": ["elementar"]},
    "Heilungsmagie": {"specs": ["besonnen"]},
    "Illusionen bannen": {"specs": ["besonnen", "arkan"]},
    "Flüche aufheben": {"specs": ["besonnen"]},
    "Entgiften": {"specs": ["besonnen", "agil"]},
    "Arkanmagie": {"specs": ["arkan"]},
    "Verspotten": {"specs": ["zäh"]},
    "Motivieren": {},
}

Soziales = {
    "Lügen": {},
    "Überzeugen": {},
    "Einschüchtern": {},
    "Beruhigen": {},
    "Charme": {},
    "Unterhalten": {},
}

Wissen = {
    "Menschenkenntnis": {},
    "Botanik": {},
    "Zoologie": {},
    "Spuren lesen": {},
    "Magie": {},
    #"Götter": {},
    "Völker": {},
}

class Group:
    def __init__(self):
        self.characters = []

    def get_characters(self):
        return self.characters

    def set_characters(self, new_chars):
        self.characters = new_chars

    def add_character(self, c):
        self.characters.append(c)

    def remove_character(self, id: int):
        deleted = False
        new_characters = []
        for c in self.characters:
            if c.get_id() != id:
                new_characters.append(c)
            else:
                deleted = True
        self.characters = new_characters
        return deleted

    def get_character_by_name(self, name: str):
        for c in self.characters:
            if c.name == name:
                return c

    def get_character_by_id(self, id: int):
        for c in self.characters:
            if c.get_id() == id:
                return c

    def save(self):
        import os.path
        # delete old data
        cwd = os.getcwd() + "/chars"
        for f in os.listdir(cwd):
            if not f.endswith(".json"):
                continue
            os.remove(os.path.join(cwd, f))
        # save new data
        current_id = 1
        for c in self.get_characters():
            fname = f"chars/{current_id}.json"
            while os.path.isfile(fname):
                current_id += 1
                fname = f"chars/{current_id}.json"
            c.save_to_json(fname)

    def __str__(self):
        ret_str = ""
        for c in self:
            ret_str += f"{str(c)}\n"
        if len(ret_str) == 0:
            return "There is no character in this group."
        return ret_str

    def __len__(self):
        return len(self.characters)

    def __iter__(self):
        self.iter_id = 0
        return self

    def __next__(self):
        if self.iter_id < len(self.characters):
            next_char = self.characters[self.iter_id]
            self.iter_id += 1
            return next_char
        else:
            raise StopIteration

class Character:
    def __init__(self, name: str = "", age: int = None, spec: str = "", sex: str = "", bio: str = "", id: int = None, grp: Group = None):
        self.id = id
        self.grp = grp

        self.pre_title = ""
        self.after_title = ""

        self.name = name
        self.age = age
        self.spec = spec
        self.sex = sex
        self.bio = bio

        self.talent_points = 0
        self.knowledge = {}
        self.action = {}
        self.fight = {}
        self.social = {}
        self.refresh_stats()

        self.exp = 500
        self.gold = 0

        self.life = 100
        self.mana = 100
        self.armor = {}
        self.mainhand = {}
        self.offhand = {}
        self.jewelery = []
        self.initiative_roll = 0

        self.refresh_stats()  # calculates self.action_points, self.action_gbp, ...
        self.save()

    def item_stats(self):
        stat_dict = {}
        items = self.jewelery + [self.armor, self.mainhand, self.offhand]
        stats = ["life", "mana", "initiative", "armor", "damage", "heal"]
        for stat in stats:
            stat_dict[stat] = 0
        for item in items:
            for stat in stats:
                if stat in item:
                    stat_dict[stat] += item[stat]
        return stat_dict

    def save(self):
        if self.grp is not None:
            self.grp.save()

    def set_group(self, grp: Group):
        self.grp = grp

    def skill_one_point(self, dict_name: str, skill_name: str):
        skill_cost = {
            97: 16,
            92: 14,
            87: 12,
            81: 10,
            77: 9,
            73: 8,
            68: 7,
            63: 6,
            57: 5,
            49: 4,
            39: 3,
            25: 2,
            0: 1,
        }
        d = getattr(self, dict_name)
        if skill_name not in d:
            d[skill_name] = 0
        if d[skill_name] == 99:
            return 0
        relevant_cost = None
        for certain_start, certain_cost in skill_cost.items():
            if certain_start <= d[skill_name]:
                relevant_cost = certain_cost
                break
        if relevant_cost is None:
            return 0
        elif self.exp >= relevant_cost:
            self.exp -= relevant_cost
            d[skill_name] += 1
            return relevant_cost
        else:
            return 0

    def skill(self, skill_name: str, talent_points: int):
        possible, dict_name = self.talent_possible(skill_name)
        if not possible:
            return f"The talent {skill_name} is not possible for {self.name}. Please type \\tg to see all available talents."

        success = 0
        cost_sum = 0
        for _ in range(talent_points):
            r = self.skill_one_point(dict_name, skill_name)
            success += 1 if r != 0 else 0
            cost_sum += r
        self.save()
        self.refresh_stats()
        return f"{self.name} successfully skilled {success}/{talent_points} talent points into {skill_name} ({dict_name}). You have spent for this {cost_sum} exp ({self.exp} exp remaining). Your new skill level for {skill_name} is {getattr(self, dict_name)[skill_name]}."


    def get_id(self):
        return self.id

    def get_member_variables_to_save(self):
        return ["pre_title", "after_title", "name", "age", "spec", "sex", "bio", "talent_points", "knowledge", "fight", "action", "social", "exp", "gold", "life", "armor", "mainhand", "offhand", "jewelery"]

    def save_to_json(self, path):
        # data_dict = {
        #     pre_title: self.pre_title,
        #     after_title: self.after_title,
        #     name: self.name,
        #     age: self.age,
        #     spec: self.spec,
        #     sex: self.sex,
        #     bio: self.bio,
        #     talent_points: self.talent_points,
        #     knowledge: self.knowledge,
        #     action: self.action,
        #     social: self.social,
        #     exp: self.exp,
        #     gold: self.gold,
        #     life: self.life,  # refresh when?
        #     armor: self.armor,
        #     mainhand: self.mainhand,
        #     offhand: self.offhand,
        #     jewelery: self.jewelery,
        # }
        data_dict = {var_name: getattr(self, var_name) for var_name in self.get_member_variables_to_save()}
        with open(path, 'w') as f:
            json.dump(data_dict, f)

    def load_from_json(self, path):
        with open(path, 'r') as f:
            data_dict = json.load(f)
        # self.pre_title = data_dict.pre_title
        # self.after_title = data_dict.after_title
        # self.name = data_dict.name
        # self.age = data_dict.age
        # self.spec = data_dict.spec
        # self.sex = data_dict.sex
        # self.bio = data_dict.bio
        # self.talent_points = data_dict.talent_points
        # self.knowledge = data_dict.knowledge
        # self.action = data_dict.action
        # self.social = data_dict.social
        # self.exp = data_dict.exp
        # self.gold = data_dict.gold
        # self.life = data_dict.life
        # self.armor = data_dict.armor
        # self.mainhand = data_dict.mainhand
        # self.offhand = data_dict.offhand
        # self.jewelery = data_dict.jewelery
        for var_name in self.get_member_variables_to_save():
            setattr(self, var_name, data_dict[var_name])
        self.refresh_stats()
        return self


    def get_name(self):
        return self.name + f" (ID={self.id})"

    def get_name_full(self):
        return self.pre_title + self.name + self.after_title + f" (ID={self.id})"

    def roll_initiative(self):
        wuerfelwurf = random.randint(1, 20)
        self.initiative_roll = wuerfelwurf

    def get_initiative(self):
        return self.initiative_roll + self.fight_points + self.item_stats()["initiative"]

    def get_max_life(self):
        max_life = 100 + self.item_stats()["life"]
        return max_life

    def get_max_mana(self):
        max_mana = 100 + self.item_stats()["mana"]
        return max_mana

    def get_armor(self):
        return self.item_stats()["armor"]

    def get_heal_bonus(self):
        return self.item_stats()["heal"]

    def get_damage_bonus(self):
        return self.item_stats()["damage"]

    def changeExp(self, amount: int):
        self.exp += amount
        self.save()
        return f"{self.name} hat nun {self.exp} Erfahrungspunkte!"

    def changeLife(self, amount: int):
        self.life += amount

        if self.life > self.get_max_life():
            self.life = self.get_max_life()
        self.save()
        if self.life <= 0:
            return f"{self.name} ist tot!"
        elif amount <= -60 or self.life <= 10:
            return f"{self.name} hat nur {self.life} Lebenspunkte und wurde bewusstlos."
        else:
            return f"{self.name} hat jetzt {self.life} Lebenspunkte."

    def changeGold(self, amount: int):
        self.gold += amount
        self.save()
        return f"{self.name} hat nun {self.moneyStr()}!"

    def moneyStr(self):
        g = int(self.gold / 10)
        s = self.gold % 10
        return f"{g} Gold, {s} Silber"

    def equipItem(self, item: str):
        if isinstance(item, dict):
            if item["type"] == "armor":
                self.armor = item
            elif item["type"] == "mainhand":
                self.mainhand = item
            elif item["type"] == "offhand":
                self.offhand = item
            elif item["type"] == "jewelery":
                self.jewelery.append(item)
            if "mana" in item:
                self.mana += item["mana"]
            if "life" in item:
                self.life += item["life"]
        self.save()

    def beingAttacked(self, wuerfel: int, bonus: int):
        wuerfe = [random.randint(1, 20) for i in range(wuerfel)]
        block = 0
        if "armor" in self.armor:
            block = sum([wurf for wurf in wuerfe if wurf <= self.armor["armor"]])
            wuerfe = [wurf for wurf in wuerfe if wurf > self.armor["armor"]]
        dmg = sum(wuerfe) + bonus
        self.changeLife(-dmg)
        self.save()
        return dmg, block

    def talent_possible(self, skill_name: str, dict_name: str = None):
        exists = False
        trees = [Handeln, Kampf, Soziales, Wissen]
        dict_names = ["action", "fight", "social", "knowledge"]
        if dict_name is not None:
            for i, dict_n in enumerate(dict_names):
                if dict_name == dict_n:
                    trees = [trees[i]]

        dict_name = None
        for i, tree in enumerate(trees):
            for key, val in tree.items():
                if skill_name == key:
                    if not val or "specs" in val and self.spec in val["specs"]:
                        exists = True
                        dict_name = dict_names[i]
        return exists, dict_name


    def probe(self, relevanter_wert: int, probe_name: str):
        add_str = f" (Probe auf {relevanter_wert})"
        gegenwert = 100 - relevanter_wert
        # Probe ausführen
        wuerfelwurf = random.randint(1, 100)
        # a. krit. Erfolg
        if wuerfelwurf == 1 or wuerfelwurf <= relevanter_wert / 10:
            #self.changeExp(3)
            return f"KRITISCHER Erfolg ({wuerfelwurf}) von {self.name} auf die Probe {probe_name}! :)" + add_str
        # b. norm. Erfolg
        elif wuerfelwurf <= relevanter_wert:
            return f"Erfolg ({wuerfelwurf}) von {self.name} auf die Probe {probe_name}! :)" + add_str
        # d. krit. Misserfolg
        elif wuerfelwurf >= (100 - gegenwert/10):
            return f"KRITISCHER Misserfolg ({wuerfelwurf}) von {self.name} auf die Probe {probe_name}! :(" + add_str
        # c. norm. Misserfolg
        elif wuerfelwurf > relevanter_wert:
            return f"Misserfolg ({wuerfelwurf}) von {self.name} auf die Probe {probe_name}! :(" + add_str

    def probe_fight(self, name: str, erschwert: int = 0):
        possible, _ = self.talent_possible(name, "fight")
        if not possible:
            return f"Talent {name} is not available in group fight or possible for {self.name}."
        # Probe auf allgemeinen Wert oder konkreten Skill?
        relevanter_wert = self.fight_points + erschwert
        if name in self.fight:
            _relevanter_wert = self.fight[name] + erschwert
            relevanter_wert = max(_relevanter_wert, relevanter_wert)

        return self.probe(relevanter_wert, name)

    def probe_knowledge(self, name: str, erschwert: int = 0):
        possible, _ = self.talent_possible(name, "knowledge")
        if not possible:
            return f"Talent {name} is not available in group knowledge or possible for {self.name}."
        # Probe auf allgemeinen Wert oder konkreten Skill?
        relevanter_wert = self.knowledge_points + erschwert
        if name in self.knowledge:
            _relevanter_wert = self.knowledge[name] + erschwert
            relevanter_wert = max(_relevanter_wert, relevanter_wert)
        return self.probe(relevanter_wert, name)

    def probe_action(self, name: str, erschwert: int = 0):
        possible, _ = self.talent_possible(name, "action")
        if not possible:
            return f"Talent {name} is not available in group action or possible for {self.name}."
        # Probe auf allgemeinen Wert oder konkreten Skill?
        relevanter_wert = self.action_points + erschwert
        if name in self.action:
            _relevanter_wert = self.action[name] + erschwert
            relevanter_wert = max(_relevanter_wert, relevanter_wert)
        return self.probe(relevanter_wert, name)

    def probe_social(self, name: str, erschwert: int = 0):
        possible, _ = self.talent_possible(name, "social")
        if not possible:
            return f"Talent {name} is not available in group social or possible for {self.name}."
        # Probe auf allgemeinen Wert oder konkreten Skill?
        relevanter_wert = self.social_points + erschwert
        if name in self.social:
            _relevanter_wert = self.social[name] + erschwert
            relevanter_wert = max(_relevanter_wert, relevanter_wert)
        return self.probe(relevanter_wert, name)

    def skill_knowledge(self, name: str, talent_points: int):
        current_points = self.knowledge[name] if name in self.knowledge else 0
        if current_points + talent_points > 70:
            talent_points = 70 - current_points
        if self.talent_points >= talent_points:
            self.talent_points -= talent_points
            if name in self.knowledge:
                self.knowledge[name] += talent_points
            else:
                self.knowledge[name] = talent_points
            self.refresh_stats()
            self.save()
            return True
        else:
            return False


    def skill_action(self, name: str, talent_points: int):
        current_points = self.action[name] if name in self.action else 0
        if current_points + talent_points > 70:
            talent_points = 70 - current_points
        if self.talent_points >= talent_points:
            self.talent_points -= talent_points
            if name in self.action:
                self.action[name] += talent_points
            else:
                self.action[name] = talent_points
            self.refresh_stats()
            self.save()
            return True
        else:
            return False

    def skill_social(self, name: str, talent_points: int):
        current_points = self.social[name] if name in self.social else 0
        if current_points + talent_points > 70:
            talent_points = 70 - current_points
        if self.talent_points >= talent_points:
            self.talent_points -= talent_points
            if name in self.social:
                self.social[name] += talent_points
            else:
                self.social[name] = talent_points
            self.refresh_stats()
            self.save()
            return True
        else:
            return False

    def refresh_stats(self):
        knowledge_sum = 0 if not self.knowledge else sum([val for _, val in self.knowledge.items()])
        fight_sum = 0 if not self.fight else sum([val for _, val in self.fight.items()])
        action_sum = 0 if not self.action else sum([val for _, val in self.action.items()])
        social_sum = 0 if not self.social else sum([val for _, val in self.social.items()])
        self.knowledge_points = round(knowledge_sum/10 + 0.001)
        self.fight_points = round(fight_sum / 10 + 0.001)
        self.action_points = round(action_sum/10 + 0.001)
        self.social_points = round(social_sum/10 + 0.001)
        self.knowledge_gbp = round(self.knowledge_points/10 + 0.001)
        self.fight_gbp = round(self.fight_points/10 + 0.001)
        self.action_gbp = round(self.action_points / 10 + 0.001)
        self.social_gbp = round(self.social_points/10 + 0.001)

    def __str__(self):
        to_str = f"Name: {self.get_name_full()}, Age: {self.age}, Spec: {self.spec}, Sex: {self.sex}\n"
        to_str += f"Leben: {self.life}/{self.get_max_life()}, Mana: {self.mana}/{self.get_max_mana()}, Exp: {self.exp}, {self.moneyStr()} \n"
        to_str += f"Rüstung: {self.get_armor()}, Bonusschaden: {self.get_damage_bonus()}, Bonusheilung: {self.get_heal_bonus()}, Initiative: {self.get_initiative()-self.initiative_roll} (+W20)\n"

        to_str += f"Knowledge ({self.knowledge_points}, GBP: {self.knowledge_gbp}): {str(self.knowledge)} \n"
        to_str += f"Fight ({self.fight_points}, GBP: {self.fight_gbp}): {str(self.fight)} \n"
        to_str += f"Action ({self.action_points}, GBP: {self.action_gbp}): {str(self.action)} \n"
        to_str += f"Social ({self.social_points}, GBP: {self.social_gbp}): {str(self.social)} \n"
        return to_str


grp = Group()
# grp.set_characters([Character(name="Zauberer Philipp", age=26, spec="Mage", sex="Male", bio="...")])


bot = lightbulb.BotApp(
    token="MTA0MTc5OTI5MjgxNTQxNzM1NA.GczkM1.YRLnIdbmw1g7dEb2Epra1zwY2epwgD6Q_TqMDY",
    default_enabled_guilds=1041002619394592768
)

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
@lightbulb.command("dm", "Dungeon Master command group.")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def dm(ctx):
    pass

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

