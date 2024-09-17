import json

with open("courses.json") as f:
    api_courses = json.load(f)

with open("total_courses.json") as f:
    parsed_courses = set(json.load(f))

api_courses_list = {course["name"].strip() for course in api_courses}

print(parsed_courses - api_courses_list)

with open("courses_diff.json", "w") as f:
    json.dump(list(parsed_courses - api_courses_list), f)
