from mmai.scrape.load import load_fighters_wikipedia
import pprint

fighters = load_fighters_wikipedia()


# pprint.pprint(fighters)
# print(type(fighters))



fighter_names = []
for f in fighters:
    if f["info"] is not None:
        full_name = f["info"]["Full name"]
        fighter_names.append(full_name)
    else:
        print(f)

print(len(fighter_names))
print(len(set(fighter_names)))


# def tabulate_fighter(fighter):
