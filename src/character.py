import random
import json

from src.data.specs import Begabungen
from src.data.talents import Handeln, Kampf, Soziales, Wissen


class Character:
    def __init__(self, name: str = "", age: int = None, spec: str = "", sex: str = "", bio: str = "", id: int = None, grp = None):
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

    def set_group(self, grp):
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

    def probe_allgemein(self, name: str, erschwert: int = 0):
        # Talentgruppe herausfinden
        possible, dict_name = self.talent_possible(name)
        if not possible:
            return f"Talent {name} is not available in group {dict_name} or possible for {self.name}."
        # Probe auf allgemeinen Wert oder konkreten Skill?
        relevanter_wert = getattr(self, f"{dict_name}_points") + erschwert
        if name in getattr(self, dict_name):
            _relevanter_wert = getattr(self, dict_name)[name] + erschwert
            relevanter_wert = max(_relevanter_wert, relevanter_wert)

        return self.probe(relevanter_wert, name)

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