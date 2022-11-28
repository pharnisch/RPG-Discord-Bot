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

    def get_character_by_user_id(self, user_id: int):
        for c in self.characters:
            if c.user_id == user_id:
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
