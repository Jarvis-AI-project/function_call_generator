# Function Call Generator (submodule of JARVIS)

## Example Input

```json
{
  "user_query": "Find a coffee shop near me with free Wi-Fi in San Francisco.",
  "functions" : [
    {
      "name": "Coffee Shop Locator",
      "function": "coffee_shop.find_nearby",
      "description": "Locate nearby coffee shops based on specific criteria like Wi-Fi availability.",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "required": true,
            "items": {},
            "description": "The city and state, e.g. San Francisco, CA"
          },
          "amenities": {
            "type": "array",
            "required": false,
            "items": {
              "type": "string",
              "enum": ["Wi-Fi", "Outdoor Seating", "Bakery", "Vegetarian Options"]
            },
            "description": "Preferred amenities."
          }
        }
      }
    }
  ],
  "model_answer": (according to the model)
}
```

## Response Format-1 (OPEN-AI) (`Recommended`)

```json
{
  "model_answer": {
    "function": "coffee_shop.find_nearby",
    "parameters": {
      "location": "San Francisco",
      "amenities": ["Wi-Fi"]
    }
  }
}
```

## Response Format-2 (HuggingFace)

```json
{
  "model_answer": "coffee_shop.find_nearby(location=\"San Francisco\", amenities=[\"Wi-Fi\"])"
}
```

## [Function Calling Leaderboard](https://huggingface.co/spaces/Nexusflow/Nexus_Function_Calling_Leaderboard)

## Some Organization working on this problem

- [Nexusflow](https://huggingface.co/Nexusflow)
- [Glaive](https://huggingface.co/glaveai)
- [Issak Carter](https://huggingface.co/Isaak-Carter)

<!-- ## Citation

```text
@article{patil2023gorilla,
  title={Gorilla: Large Language Model Connected with Massive APIs},
  author={Shishir G. Patil and Tianjun Zhang and Xin Wang and Joseph E. Gonzalez},
  year={2023},
  journal={arXiv preprint arXiv:2305.15334},
}
``` -->
