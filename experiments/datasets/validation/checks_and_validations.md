# Checks and Validations

## 1. User Query

- **Existence Check:**
  - Ensures that the key `user_query` exists.
- **Type Check:**
  - Ensures that the value of `user_query` is a string.

## 2. Functions

- **Existence Check:**
  - Ensures that the key `functions` exists.
- **Type Check:**
  - Ensures that the value of `functions` is a list.
- **Function Definition Check:**
  - For each dictionary in the `functions` list:
    1. **Name Check:**
       - Ensures the presence of the key `name` (str).
    2. **API Call Check:**
       - Ensures the presence of the key `api_call` (str).
    3. **Description Check:**
       - Ensures the presence of the key `description` (str).
    4. **Parameters Check:**
       - Ensures the presence of the key `parameters` (dict).

## 3. Model Answer (OpenAI)

- **Existence Check:**
  - Ensures the presence of the key `model_answer_openai`.
- **Type Check:**
  - Validates that the value of `model_answer_openai` is a dictionary.
- **API Call Consistency:**
  - For function in the `functions` list if `function["api_call"]` is equal to `model_answer_openai["api_call"]`:
    - Validates parameters in `model_answer_openai["parameters"]`:
      - Ensures that they are sequential as per the order of `function["parameters"]["properties"]`.
        - Ensures the presence of all required parameters in `function["parameters"]["required"]`.
        - Validates data types for each parameter:
          - Possible datatypes: `string`, `integer`, `float`, `boolean`, `array`.
        - Validates against `enum` values if present in `function["parameters"]["properties"][parameter]`.
        - Ensures no extra parameters in `model_answer_openai["parameters"]`.