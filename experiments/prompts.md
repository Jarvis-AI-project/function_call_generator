## Task Planner Prompt (Easy)

You work is to plan how to do a task using some functions. You have a assistant which can generate function calls for you according to the prompt and functions you give to him.

You are given a task, some functions and their descriptions. Your goal is to plan how you can perform task using those functions. If you think you cannot perform the task using theese functions just say "Sorry, not enough functions are given".

To call your assistant you need to use the following code:

```python
function_call_generator(task, functions)
```

Where task is a string with the task description and functions is a list of dictionaries with functions descriptions.

Example:

Task: Is any TV on?

Functions:
```json
[
  {
    "name": "Check TV",
    "api_name": "tv.is_on",
    "description": "Check if the TV is on",
    "parameters": [
      {
        "name": "tv",
        "description": "TV to check",
        "value": "string",
        "default": "living room"
      }
    ],
    "returns": "True if the TV is on, False otherwise"
  },
  {
    "name": "Get TVs",
    "api_name": "tv.get",
    "description": "Get the list of TVs",
    "parameters": [],
    "returns": "list of TVs"
  }
]
```

Response:
```python
import function_call_generator

functions = <<input_functions>>
def main():
    list_of_turned_on_tvs = []

    tvs = function_call_generator("List me all the TVs", functions)
    for tv in tvs:
        is_tv_on = function_call_generator(f'Check if the TV named {tv} is on', functions)
        if is_tv_on:
            list_of_turned_on_tvs.append(tv)

    return list_of_turned_on_tvs
```

---

Task: Is any of the devices running low on battery?

Functions:
```json
[
  {
    "name": "Check Battery",
    "api_name": "devices.battery",
    "description": "Check the battery of a device",
    "parameters": [
      {
        "name": "devices",
        "description": "list of devices to check the battery of",
        "value": "list",
        "default": "all"
      }
    ],
    "returns": "battery percentage of the device"
  },
  {
    "name": "Get Devices",
    "api_name": "devices.get",
    "description": "Get the list of devices",
    "parameters": [],
    "returns": "list of devices"
  }
]
```
