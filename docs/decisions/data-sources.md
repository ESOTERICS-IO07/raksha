# Synthetic Dataset Provenance

This document explains the origins, methodology, and deterministic logic behind the permanent synthetic demo dataset established in Phase 5C-1.

## Source Data Policy

The goal of this dataset is to establish a deterministic, offline-capable environment for demonstrating the RAKSHA fraud intelligence pipeline without relying on external APIs, non-deterministic sampling, or downloading gigabytes of raw data.

> [!WARNING]
> **Kaggle Availability & Dataset Constraints**
> The `PaySim` and `BankSim` Kaggle datasets were specified as source material. However, raw Kaggle dataset downloads require API keys/authentication which are unavailable in the isolated environment. Furthermore, committing hundreds of megabytes of raw synthetic transactions violates repository hygiene.
> 
> Therefore, this dataset establishes the structural prerequisites (the exact graph schema and deterministic scenarios required by the frozen contracts) without falsely importing fabricated data under the guise of PaySim/BankSim. 

## Source Metadata & Curation

### 1. PaySim
- **Source**: Kaggle (https://www.kaggle.com/datasets/ealaxi/paysim1/data)
- **Role**: Expected to provide transaction history, volume baselines, and temporal patterns.
- **Provenance**: 
  - **Source records actually transformed**: None. Raw Kaggle data could not be downloaded/committed due to size and API key requirements.
  - **Source characteristics used as design/reference material**: The intent of PaySim (amounts, currency mapping, volume frequency) was used to design the baseline generation logic.
  - **Manually constructed RAKSHA demo records**: ~200 deterministic, low-value historical transactions were manually synthesized using `scripts/generate_demo_graph.py` to substitute the PaySim baseline distribution.

### 2. BankSim
- **Source**: Kaggle (https://www.kaggle.com/datasets/ealaxi/banksim1)
- **Role**: Expected to provide fraud cluster linkages, spending behavior, and anomaly patterns.
- **Provenance**: 
  - **Source records actually transformed**: None. Raw Kaggle data was unavailable.
  - **Source characteristics used as design/reference material**: BankSim's anomaly topologies inspired the fraud network requirements.
  - **Manually constructed RAKSHA demo records**: The exact frozen required fraud network (User 11/12/13/14 sending ₹50k, ₹30k, ₹70k, ₹15k to Recipient 20) was manually constructed and injected with `FraudFlag` records.

### 3. Smishing-Dataset-IMC25
- **Source**: GitHub (https://raw.githubusercontent.com/reportsmishing/Smishing-Dataset-IMC25/refs/heads/main/dataset/final_dataset_output.csv)
- **Role**: Provides highly realistic social engineering terminology, intent payloads, and scenario language.
- **Provenance**: 
  - **Source records actually transformed**: None.
  - **Source characteristics used as design/reference material**: The dataset was inspected (e.g., account suspension threats, bank impersonation) to curate realistic coercion phrases.
  - **Manually constructed RAKSHA demo records**: The scenario reason `"A bank officer told me to transfer this immediately or my account will be blocked"` was manually constructed based on the dataset's characteristics.

## Determinism
The entire dataset is produced using `random.seed(42)` inside `scripts/generate_demo_graph.py`. The resulting JSON (`data/seed/demo_graph.json`) assigns deterministic integers (`1001`, `2001`, etc.) to semantic handles (`SYNTHETIC_USER_001`). `seed_db.py` uses idempotent SQLAlchemy lookups (`filter(User.id == ...).first()`) to prevent duplication upon repeated runs.

## Demo Graph Topology
- **Users**: 14
- **Recipients**: 24
- **Historical Transactions**: 204
- **Fraud Flags**: 3
- **Scenarios**: 2 predefined payloads mapped directly to `TransactionContext` shapes.
