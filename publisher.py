class Publisher:
    def __init__(self, name: str, tags: [], dob: str = None):
        self.pub_data = {
            "name": name,
            "tags": tags
        }
        if dob:
            self.pub_data["dob"] = dob

    def __repr__(self):
        name = '\n' + self["name"].title() + '\n'
        tags = ",\n".join(self.pub_data["tags"])
        dob = ""
        if dob:
            dob = f"born {self.pub_data['dob']} \n"

        output_string = name + dob + 'has these tags:\n' + tags + '\n'
        return output_string

    def __getitem__(self, item):
        return self.pub_data[item]
