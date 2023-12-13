---
license: apache-2.0
task_categories:
- text-generation
language:
- en
size_categories:
- 10K<n<100K
---

This dataset consists of 52k samples generated through [Glaive](https://glaive.ai) for the task of function calling, in the following format-

```
SYSTEM: You are an helpful assistant who has access to the following functions to help the user, you can use the functions if needed-
{
  JSON function definiton
}
USER: user message
ASSISTANT: assistant message

Function call invocations are formatted as-

ASSISTANT: <functioncall> {json function call}

Response to the function call is formatted as-
FUNCTION RESPONSE: {json function response}
```

There are also samples which do not have any function invocations, multiple invocations and samples with no functions presented and invoked to keep the data balanced.