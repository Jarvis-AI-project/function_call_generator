"""
This file contains the prompts for the synthetic generation dataset.
"""

prompt = """

You are a agent who is helping to build datasets for a function calling model. This model will be used in smart home assistant devices. This model will be given a list of similar functions and a user query. Among theese functions there is a function that is the correct function to call for the given query. The model will be trained to predict the correct function and generate a function call for the given query.

Example:
TOPIC: coffee-shops
FUNCTIONS: [
    {
        "name": "coffee_shop.find_nearby",
        "description": "Find nearby coffee shops according to user's preferences",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The location to search for coffee shops. e.g. 'San Francisco, CA'"
                },
                "aminities": {
                    "type": "array",
                    "description": "The aminities that the coffee shop should have. e.g. ['wifi', 'outlets']",
                    "items": {
                        "type": "string",
                        "enum": ["wifi", "outlets", "food", "drinks", "seating"]
                    }
                }
            }
        },
        "required": ["location"],
    },
    {
        "name": "coffee_shop.find_best",
        "description": "Find the best coffee shop according to user's preferences",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The location to search for coffee shops. e.g. 'San Francisco, CA'"
                },
                "aminities": {
                    "type": "array",
                    "description": "The aminities that the coffee shop should have. e.g. ['wifi', 'outlets']",
                    "items": {
                        "type": "string",
                        "enum": ["wifi", "outlets", "food", "drinks", "seating"]
                    }
                },
                "rating": {
                    "type": "number",
                    "description": "The minimum rating of the coffee shop. e.g. 4.5"
                }
            }
        },
        "required": ["location"],
    },
    {
        "name": "coffee_shop.find_best_in_range",
        "description": "Find the best coffee shop within a given range according to user's preferences",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The location to search for coffee shops. e.g. 'San Francisco, CA'"
                },
                "aminities": {
                    "type": "array",
                    "description": "The aminities that the coffee shop should have. e.g. ['wifi', 'outlets']",
                    "items": {
                        "type": "string",
                        "enum": ["wifi", "outlets", "food", "drinks", "seating"]
                    }
                },
                "rating": {
                    "type": "number",
                    "description": "The minimum rating of the coffee shop. e.g. 4.5"
                },
                "range": {
                    "type": "number",
                    "description": "The range in miles from the given location. e.g. 5"
                }
            }
        },
        "required": ["location"],
    }
]
USER_QUERY: "Find a coffee shop in California that has wifi and outlets"
FUNCTION_CALL: {
    "name": "coffee_shop.find_nearby",
    "parameters": {
        "location": "California",
        "aminities": ["wifi", "outlets"]
    }
}

Note:
- functions should contain a variety of parameters (e.g. strings, numbers, arrays, objects, etc.).
- generated user queries should contain values for all the required parameters of the function.
- generate long descriptions for the functions and their parameters.
- generated user queries should be causal (assume they are normal day to day conversations).
- generated user queries should be according to the given topic. (e.g. if the topic is coffee shops, then the user queries should be about coffee shops).
- Be as creative as possible with the possible topics, functions, and user queries.

TOPIC: 
"""