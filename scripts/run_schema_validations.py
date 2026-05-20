#!/usr/bin/env python3
"""Run KG validation rules stored in SurrealDB.

Expected environment variables:
- SURREAL_URL
- SURREAL_NAMESPACE
- SURREAL_DATABASE
- SURREAL_USERNAME
- SURREAL_PASSWORD
"""

from __future__ import annotations

import asyncio
import json
import os
import sys

from surrealdb import AsyncSurreal


async def main() -> int:
    url = os.getenv('SURREAL_URL', 'ws://localhost:8000/rpc')
    namespace = os.getenv('SURREAL_NAMESPACE', 'agent_commerce')
    database = os.getenv('SURREAL_DATABASE', 'main')
    username = os.getenv('SURREAL_USERNAME', 'root')
    password = os.getenv('SURREAL_PASSWORD', 'root')

    db = AsyncSurreal(url)
    await db.connect()
    await db.signin({'username': username, 'password': password})
    await db.use(namespace, database)

    rules = await db.query('SELECT * FROM kg_validation_rules ORDER BY severity, name;')
    rows = rules[0]['result'] if rules else []

    failures = []

    for rule in rows:
        name = rule['name']
        severity = rule.get('severity', 'error')
        query = rule['query']

        result = await db.query(query)
        violations = result[0]['result'] if result else []

        count = len(violations)
        print(f'[{severity.upper()}] {name}: {count} violation(s)')

        if count > 0:
            failures.append({
                'rule': name,
                'severity': severity,
                'count': count,
                'sample': violations[:5],
            })

    await db.close()

    if failures:
        print('\nValidation failures detected:')
        print(json.dumps(failures, indent=2, default=str))
        return 1

    print('\nAll schema validation rules passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
