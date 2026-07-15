# Configuration

Providers are configured in `~/.config/screen-sentry/providers.toml`. Every
provider requires a `type` field that selects the backend implementation.

## Provider Types

| Type            | Description                                       |
| --------------- | ------------------------------------------------- |
| `openai_compat` | Works with OpenAI-compatible chat completion APIs |
| `custom`        | Bring-your-own request format via placeholders    |

## OpenAI-Compatible Providers

For providers that expose an OpenAI-compatible endpoint (like LM Studio):

```toml
[providers.lmstudio]
type        = "openai_compat"
base_url    = "http://localhost:1234/v1"
model       = "your-local-model-name"
temperature = 0.2
# api_key is not required for local servers — omit or leave blank
```

## Custom Providers

Use `custom` when your endpoint doesn't match supported providers. You control
the exact request body and headers using placeholders that get substituted
before the request is sent.

**Available Placeholders:**

| Placeholder   | Description                         |
| ------------- | ----------------------------------- |
| `{{system}}`  | App's system prompt (required)      |
| `{{prompt}}`  | App's user prompt (required)        |
| `{{image}}`   | Base64-encoded image (required)     |
| `{{model}}`   | Value of `model` field (optional)   |
| `{{api_key}}` | Value of `api_key` field (optional) |

**Response Path:**

`response_path` is a dot-notation path used to extract the model's text reply
from the JSON response. For example, `choices.0.message.content` reaches
`response["choices"][0]["message"]["content"]`.

**Example Custom Provider:**

```toml
[providers.example]
type          = "custom"
url           = "https://api.example.com/v1/chat/completions"
model         = "example-vision-model"
api_key       = "your-api-key-here"
response_path = "choices.0.message.content"

headers = { Authorization = "Bearer {{api_key}}" }

body = '''
{
  "model": "{{model}}",
  "messages": [
    { "role": "system", "content": "{{system}}" },
    {
      "role": "user",
      "content": [
        { "type": "text", "text": "{{prompt}}" },
        {
          "type": "image_url",
          "image_url": { "url": "data:image/png;base64,{{image}}" }
        }
      ]
    }
  ]
}
'''
```

## Active Provider

Specify which provider to use in `~/.config/screen-sentry/config.toml`:

```toml
[app]
provider = "lmstudio"
```
