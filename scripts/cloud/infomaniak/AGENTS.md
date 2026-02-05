# Infomaniak Examples - AI Agent Guide

## Active Components

| Script | Entry Point | Purpose |
|--------|-------------|---------|
| `compute_examples.py` | `main()` | Compute instance management |
| `block_storage_examples.py` | `main()` | Volume/snapshot operations |
| `network_examples.py` | `main()` | Network infrastructure |
| `object_storage_examples.py` | `main()` | Swift and S3 storage |
| `identity_examples.py` | `main()` | Identity/credentials |
| `dns_examples.py` | `main()` | DNS zone/record management |
| `orchestration_examples.py` | `main()` | Heat stack orchestration |
| `metering_examples.py` | `main()` | Usage and quota metrics |
| `newsletter_examples.py` | `main()` | Newsletter campaign and contact management |
| `full_workflow.py` | `main()` | Complete deployment |

## Operating Contract

**Input**: CLI arguments + environment variable credentials  
**Output**: Console output with status icons and resource details  
**Side Effects**: Creates/modifies Infomaniak cloud resources

## Common Patterns

```bash
# List resources
python compute_examples.py --list-instances

# Get details
python compute_examples.py --get-instance INSTANCE_ID

# Create resource
python compute_examples.py --create-instance --name my-vm --flavor a1-ram2-disk20-perf1

# Newsletter operations
python newsletter_examples.py --list-campaigns
python newsletter_examples.py --create-campaign --subject "Test" --sender "news@test.com" --list-id 123
python newsletter_examples.py --schedule CAMPAIGN_ID --schedule-at "2026-03-01T10:00:00Z"

# Full workflow
python full_workflow.py --deploy --name my-project
```

---

**Navigation**: [README](README.md) | [SPEC](SPEC.md)
