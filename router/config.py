"""JSON configuration with explicit capability boundaries and no secret persistence."""
import copy
import json
import math
import os
from pathlib import Path

from .types import MODEL_TIERS


def _merge(base, changes):
    if not isinstance(changes, dict):
        raise ValueError('Configuration sections must be JSON objects')
    for key, value in changes.items():
        if key not in base:
            raise ValueError(f'Unknown configuration key: {key}')
        if isinstance(base[key], dict):
            _merge(base[key], value)
        else:
            base[key] = copy.deepcopy(value)


def validate_config(config):
    if config['model_mode'] not in ('auto', *MODEL_TIERS):
        raise ValueError('model_mode must be auto, luna, sol or astra')
    for group in ('limits', 'thresholds', 'weights'):
        for key, value in config[group].items():
            minimum = 0 if group == 'weights' or key in ('max_retries_per_model', 'max_escalations') else 1
            if type(value) is not int or value < minimum:
                raise ValueError(f'{group}.{key} must be an integer >= {minimum}')
    if config['thresholds']['astra'] <= config['thresholds']['sol']:
        raise ValueError('astra threshold must exceed sol threshold')
    for tier in MODEL_TIERS:
        model = config['models'][tier]
        if not isinstance(model['id'], str) or not model['id'].strip():
            raise ValueError(f'Missing model ID for {tier}')
        supported = model['supported_efforts']
        if not isinstance(supported, list) or any(not isinstance(x, str) for x in supported):
            raise ValueError(f'Invalid supported_efforts for {tier}')
        for effort in model['efforts'].values():
            if effort is not None and effort not in supported:
                raise ValueError(f'Unsupported reasoning effort for {tier}: {effort}')
        pricing = model['pricing_per_million']
        if pricing is not None:
            for name in ('input', 'cached_input', 'output'):
                rate = pricing.get(name)
                if type(rate) not in (int, float) or not math.isfinite(rate) or rate < 0:
                    raise ValueError(f'Invalid {tier} pricing: {name}')
    for group, names in (('api', ('timeout_seconds',)),
                         ('bridge', ('timeout_seconds', 'max_script_bytes', 'max_image_bytes'))):
        for key in names:
            value = config[group][key]
            if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
                raise ValueError(f'{group}.{key} must be positive and finite')
    for name in ('luna_failures', 'sol_substantive_failures'):
        if type(config['escalation'][name]) is not int or config['escalation'][name] < 1:
            raise ValueError(f'escalation.{name} must be a positive integer')
    order = config['escalation']['fallback_order']
    if not isinstance(order, list) or any(t not in MODEL_TIERS for t in order) or len(order) != len(set(order)):
        raise ValueError('Invalid fallback_order')
    if type(config['escalation']['allow_model_fallback']) is not bool or type(config['logging']['debug']) is not bool:
        raise ValueError('Fallback and debug flags must be booleans')
    for name in ('base_url', 'key_env'):
        if not isinstance(config['api'][name], str) or not config['api'][name].strip():
            raise ValueError(f'api.{name} must be a non-empty string')
    return config


def load_config(path=None):
    config = json.loads(Path(__file__).with_name('config.json').read_text(encoding='utf-8'))
    original = copy.deepcopy(config['models'])
    changes = {}
    if path:
        changes = json.loads(Path(path).read_text(encoding='utf-8-sig'))
        _merge(config, changes)
    for tier in MODEL_TIERS:
        model = config['models'][tier]
        model['id'] = os.environ.get(f'{tier.upper()}_MODEL', model['id'])
        capability_env = os.environ.get(f'{tier.upper()}_MODEL_EFFORTS')
        declared = changes.get('models', {}).get(tier, {})
        if model['id'] != original[tier]['id'] and not capability_env:
            # Unknown IDs must not silently inherit the old model's API capabilities.
            if declared.get('id') != model['id'] or 'supported_efforts' not in declared:
                model['supported_efforts'] = []
                model['efforts'] = dict.fromkeys(model['efforts'])
        if capability_env is not None:
            model['supported_efforts'] = json.loads(capability_env)
            model['efforts'] = {k: v if v in model['supported_efforts'] else None
                                for k, v in model['efforts'].items()}
    return validate_config(config)
