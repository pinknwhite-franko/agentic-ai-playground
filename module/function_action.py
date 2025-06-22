import json
from typing import List, Dict
def get_search_criteria() -> dict:
    """Prompt user for home search criteria and return them as a dictionary."""
    location = input("Enter the desired location (e.g., Sloan Lake, Denver): ").strip()
    
    try:
        num_of_bedrooms = int(input("Enter the number of bedrooms: "))
    except ValueError:
        num_of_bedrooms = None
    
    try:
        num_of_bathrooms = int(input("Enter the number of bathrooms: "))
    except ValueError:
        num_of_bathrooms = None

    has_garage_input = input("Do you want a garage? (yes/no): ").strip().lower()
    has_garage = True if has_garage_input in ['yes', 'y'] else False if has_garage_input in ['no', 'n'] else None

    try:
        year_built = int(input("Enter the minimum year built (e.g., 1970): "))
    except ValueError:
        year_built = None

    return {
        "search_criteria":{
            "location": location,
            "num_of_bedrooms": num_of_bedrooms,
            "num_of_bathrooms": num_of_bathrooms,
            "has_garage": has_garage,
            "year_built": year_built
        }
    }

def partial_search_property(prop, criteria):
    return all(prop.get(k) == v if k != "year_built" else prop.get(k) >= v for k, v in criteria.items())


def search_property(search_criteria: dict, partial_search=True) -> list[dict]:
    """search for property based on a set of criterias"""
    file_path = "./data/property_data.json"

    with open(file_path, "r") as f:
        properties = json.load(f)


    if partial_search:
        matches = [prop for prop in properties if partial_search_property(prop, search_criteria)]
    else :
        matches = []
        for prop in properties:
            if (
                prop["location"] == search_criteria["location"] and
                prop["num_of_bedrooms"] == search_criteria["num_of_bedrooms"] and
                prop["num_of_bathrooms"] == search_criteria["num_of_bathrooms"] and
                prop["has_garage"] == search_criteria["has_garage"] and
                prop["year_built"] > search_criteria["year_built"]
            ):
                matches.append(prop)
    matches[0] = "Could you write a summary of the following options?"
    return { "search_results " : matches} if matches else ["No properties found matching the criteria."]
    

def summarize_options(search_results: list[dict]) -> list[dict]:
    """summarize the matched properties based on the properties features"""
    if not search_results:
        return ["No properties found matching the criteria."]
    else:
        search_results[0] = "Here are the matched properties based on the criteria, could you provide a summary of these properties?"
    return search_results

# def search_in_file(file_name: str, search_term: str) -> list:
#     """Search for a term in a file and return matching lines."""
#     results = []
#     with open(file_name, 'r') as f:
#         for i, line in enumerate(f.readlines()):
#             if search_term in line:
#                 results.append((i+1, line.strip()))
#     return results