# Demo Commands

1) Generate latest (most recent YAML, timestamped):
```
./generate_campaign.sh
```

2) Generate for a specific output directory (reads YAML inside, writes status.json there):
```
./generate_campaign.sh --output-dir outputs/campaigns/<campaign_id_or_run>
```

Refine latest campaign:
```
./refine_campaign.sh
```

Refine with filters (campaign/product/aspect/status):
```
./refine_campaigns.sh
```

