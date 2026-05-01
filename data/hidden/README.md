# Hidden Official Split

Do not commit the official hidden split to this repository.

Expected private file shape:

```text
persian_eval_v1.hidden.jsonl
```

The JSONL schema is identical to the public files:

- `id`
- `track`
- `prompt`
- `choices`
- `answer`
- `metadata`
- `source`
- `split`

Use `split: "hidden"` and run official evaluations with sample targets omitted:

```bash
persian-eval run --data /secure/path/persian_eval_v1.hidden.jsonl --no-samples --output results/model_official.json
```
