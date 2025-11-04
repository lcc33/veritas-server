backend/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       ├── analyze.py
│   │       └── health.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── claim_extractor.py
│   │   ├── evidence_retriever.py
│   │   ├── analyzer.py
│   │   ├── cache.py
│   │   └── llm/
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── gemini.py
│   │       └── factory.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   └── utils/
│       ├── __init__.py
│       └── content_parser.py