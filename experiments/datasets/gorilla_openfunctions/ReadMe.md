# 1. Dump dataset existing datasets to MongoDB.

### 1.1 Dump  `gorilla_openfunctions` (`test.jsonl` and `train.jsonl`) [12,237].

Collection Name: `function_calling/gorilla_openfunctions`

Format:

```json
{
    "split": "train", // ['train', 'test']
    "line": 1, // 1 to n
    "data": {}
}
```

### 1.2 Extract raw functions from `function_calling/gorilla_openfunctions` [42,893].

Collection Name: `function_calling/raw_functions`

Format:

```json
(
    "origin_dataset" : "gorilla_openfunctions", // dataset name
    "split" : "train", // ['train', 'test']
    "line" : 1, // 1 to n
    "data": {},
    "embeding": []
)
```
