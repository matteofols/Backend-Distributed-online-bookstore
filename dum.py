import json

with open("/Users/tejasds/Downloads/data.json", 'r') as f:
    database = json.load(f)

if "mytbis" in database:
    # print(database["mytbis"]["file_loc"])
    database["mytbis"]["num_req"] = database["mytbis"]["num_req"] + 1
    print(database["mytbis"]["num_req"])

# print(database)
