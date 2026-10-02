"""Append-only request logs and per-model usage, with opt-in payload logging."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from .types import MODEL_TIERS


class AuditLog:
    def __init__(self, root, debug=False):
        self.root = Path(root)
        self.debug = debug

    def emit(self, task_id, event, **data):
        folder = self.root / task_id
        folder.mkdir(parents=True, exist_ok=True)
        if not self.debug:
            data = {key: value for key, value in data.items() if key not in ('task', 'arguments', 'result', 'message')}
        record = {'time': datetime.now(timezone.utc).isoformat(), 'event': event, **data}
        with (folder / 'events.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + '\n')


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


class Statistics:
    def __init__(self, config):
        self.config = config
        self.data = {tier: {'calls': 0, 'attempts': 0, 'successful_attempts': 0, 'failed_attempts': 0,
                           'tool_calls': 0, 'input_tokens': 0, 'cached_input_tokens': 0,
                           'output_tokens': 0, 'reasoning_tokens': 0, 'escalations': 0,
                           'estimated_cost': 0.0 if config['models'][tier]['pricing_per_million'] else None}
                     for tier in MODEL_TIERS}

    def usage(self, tier, usage):
        row = self.data[tier]
        inputs = usage.get('input_tokens', 0) or 0
        cached = (usage.get('input_tokens_details') or {}).get('cached_tokens', 0) or 0
        outputs = usage.get('output_tokens', 0) or 0
        row['input_tokens'] += inputs
        row['cached_input_tokens'] += cached
        row['output_tokens'] += outputs
        row['reasoning_tokens'] += (usage.get('output_tokens_details') or {}).get('reasoning_tokens', 0) or 0
        rates = self.config['models'][tier]['pricing_per_million']
        if rates:
            row['estimated_cost'] += (max(0, inputs - cached) * rates['input'] + cached * rates['cached_input'] + outputs * rates['output']) / 1_000_000

    def snapshot(self):
        result = {}
        for tier, row in self.data.items():
            attempts = row['successful_attempts'] + row['failed_attempts']
            result[tier] = {**row,
                           'success_rate': row['successful_attempts'] / attempts if attempts else None,
                           'failure_rate': row['failed_attempts'] / attempts if attempts else None,
                           'average_tool_calls': row['tool_calls'] / row['attempts'] if row['attempts'] else None}
        return result
