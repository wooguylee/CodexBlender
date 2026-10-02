"""OpenAI Responses transport using the standard library, shared by CLI hosts."""
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


class ModelCallError(RuntimeError):
    def __init__(self, kind, message):
        super().__init__(message)
        self.kind = kind


class ResponsesClient:
    """One request per call. Retry/fallback policy belongs exclusively to the router."""
    def __init__(self, config, api_key=None):
        self.config = config
        self.key = api_key or os.environ.get(config['api']['key_env'])
        if not self.key:
            raise ModelCallError('fatal', f"Set {config['api']['key_env']} before run; route is available without a key")
        base = config['api']['base_url'].rstrip('/')
        parsed = urlsplit(base)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError('API base_url must be an HTTPS URL without credentials/query/fragment')
        self.url = base + '/responses'

    def complete(self, *, model, effort, history, tools, instructions):
        payload = {'model': model, 'instructions': instructions, 'input': history,
                   'tools': tools, 'parallel_tool_calls': False, 'store': False,
                   'max_output_tokens': self.config['limits']['max_output_tokens']}
        if effort is not None:
            payload['reasoning'] = {'effort': effort}
        request = Request(self.url, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                          headers={'Authorization': 'Bearer ' + self.key, 'Content-Type': 'application/json'}, method='POST')
        try:
            with urlopen(request, timeout=self.config['api']['timeout_seconds']) as response:
                result = json.loads(response.read().decode('utf-8'))
        except HTTPError as error:
            try:
                code = json.loads(error.read().decode('utf-8')).get('error', {}).get('code')
            except (ValueError, AttributeError):
                code = None
            if code in ('model_not_found', 'model_not_available'):
                kind = 'unavailable'
            elif code in ('insufficient_quota', 'billing_hard_limit_reached'):
                kind = 'fatal'
            elif error.code in (408, 429) or error.code >= 500:
                kind = 'transient'
            else:
                kind = 'fatal'
            # Do not echo API bodies; they may contain credentials or user content.
            raise ModelCallError(kind, f'OpenAI HTTP {error.code} ({kind})') from None
        except (URLError, TimeoutError, OSError):
            raise ModelCallError('transient', 'OpenAI temporary network/timeout error') from None
        except (ValueError, UnicodeError):
            raise ModelCallError('fatal', 'OpenAI returned malformed JSON') from None
        if not isinstance(result, dict) or not isinstance(result.get('output'), list):
            raise ModelCallError('fatal', 'OpenAI response has no valid output array')
        for item in result['output']:
            if not isinstance(item, dict) or not isinstance(item.get('type'), str):
                raise ModelCallError('fatal', 'OpenAI returned an invalid output item')
            if item['type'] == 'function_call' and any(not isinstance(item.get(key), str) or not item[key]
                                                      for key in ('name', 'arguments', 'call_id')):
                raise ModelCallError('fatal', 'OpenAI returned an incomplete function call')
            if item['type'] == 'message':
                content = item.get('content')
                if (not isinstance(content, list) or any(not isinstance(part, dict) for part in content)
                        or any(part.get('type') == 'output_text' and not isinstance(part.get('text'), str) for part in content)):
                    raise ModelCallError('fatal', 'OpenAI returned an invalid message')
        usage = result.get('usage') or {}
        if not isinstance(usage, dict):
            raise ModelCallError('fatal', 'OpenAI returned invalid usage')
        for key in ('input_tokens', 'output_tokens'):
            if key in usage and (type(usage[key]) is not int or usage[key] < 0):
                raise ModelCallError('fatal', 'OpenAI returned invalid token counts')
        return result
