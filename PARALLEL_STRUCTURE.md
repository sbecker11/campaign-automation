# Parallel Directory Structure

## New Structure (Parallel inputs/outputs)
```
workspace-campaign-automation/
│
├── inputs/
│   └── campaigns/
│       ├── summer_2024.yaml
│       ├── fall_2024.yaml
│       └── holiday_2024.yaml
│
├── outputs/
│   └── campaigns/              # ← Parallel to inputs/campaigns
│       ├── summer_2024/
│       │   ├── products/
│       │   └── reports/
│       ├── fall_2024/
│       │   ├── products/
│       │   └── reports/
│       └── holiday_2024/
│           ├── products/
│           └── reports/
│
├── assets/
│   └── logo.png
│
├── src/
└── tests/
```

✅ **Clean parallel structure!**
