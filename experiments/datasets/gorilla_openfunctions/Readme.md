## All examples should be in the following format:

```json
{
  "user_query": "User query.",
  "functions": [  // At least one function. Preferably more. (Will use vectorDB to find similar functions)
    {
      "name": "Function name",
      "api_call": "api_call",
      "description": "Function description.",
      "parameters": {
        "param1": {
            "type": "string",
            "required": true,
            "description": "Param1 description."
          },
        "param2": {
            "type": "string",
            "required": true,
            "description": "Param2 description."
          },
          ...
      }
    }
  ],
  "model_answer": "api_call(param1='value1', param2='value2', ...)"
}
```

## Some Raw Examples


```json
{
  "user_query": "Convert 10 miles to kilometers.",
  "functions": [
    {
      "name": "Unit Converter",
      "api_call": "unit_conversion.convert",
      "description": "Convert a value from one unit to another.",
      "parameters": {
        "type": "object",
        "properties": {
          "value": {
            "type": "number",
            "description": "The value to be converted."
          },
          "from_unit": {
            "type": "string",
            "description": "The unit to convert from.",
            "enum": ["miles", "kilometers"]
          },
          "to_unit": {
            "type": "string",
            "description": "The unit to convert to.",
            "enum": ["miles", "kilometers"]
          }
        },
        "required": ["value", "from_unit", "to_unit"]
      }
    }
  ],
  "model_answer": "unit_conversion.convert(value=10, from_unit=\"miles\", to_unit=\"kilometers\")"
}
```

```json
{
  "user_query": "Reschedule the client meeting to next month on the 5th at 3 PM.",
  "functions": [
    {
      "name": "Client Meeting Rescheduler",
      "api_call": "client_meeting.reschedule",
      "description": "Reschedule a client meeting to a new date and time.",
      "parameters": {
        "type": "object",
        "properties": {
          "meeting_id": {
            "type": "string",
            "description": "Unique identifier of the client meeting."
          },
          "new_date": {
            "type": "string",
            "description": "New meeting date (e.g., YYYY-MM-DD)."
          },
          "new_time": {
            "type": "string",
            "description": "New meeting time (e.g., HH:MM AM/PM)."
          }
        },
        "required": ["meeting_id", "new_date", "new_time"]
      }
    }ṭ
  ],
  "model_answer": "client_meeting.reschedule(meeting_id='67890', new_date='2023-11-05', new_time='3:00 PM')"
}
```
