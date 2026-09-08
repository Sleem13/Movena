# External Capstone Model Inventory

Source reviewed locally: `C:/Users/NewAdmin/Desktop/Physiology-LLM-Capstone-main/models/`

This inventory records the files that were inspected. No model binary has been
copied into Movena. Every entry remains disabled and blocked from production or
public distribution pending license, dataset-derivative, and provenance review.

| File | Movena exercise | Bytes | Input | Normalizer | Output | SHA-256 |
| --- | --- | ---: | --- | --- | --- | --- |
| `deep_squat_robust.keras` | `bodyweight_squat` | 1,389,935 | `(1,81,66)` | spine length | sigmoid quality | `8a59860291d98ac5bef91de4855c6560c1db3b8ce1783e64ce23b30e407aaba9` |
| `sit_to_stand_robust.keras` | `sit_to_stand` | 4,483,442 | `(1,88,66)` | pelvis width | sigmoid quality | `99b18cf621a3fa4d113fbe557f9998fba5e501e5bde67f635b0d8dd92d6b6f00` |
| `pushup_robust.keras` | `push_up` | 602,065 | `(1,60,66)` | shoulder width | sigmoid quality | `3329b1f6519026a548f5d8bd4409dc7a12a228ed4fc484a6f96bb3bde5c50ad5` |
| `bicep_curl_robust.keras` | `bicep_curl` | 707,300 | `(1,40,99)` | 33-joint torso length | five-class label | `da74cc6c72b01b72bafe8defe90b0ac551025143097ab0782779aa42e57e9a07` |
| `lateral_raise.keras` | `shoulder_abduction` | 4,483,442 | `(1,74,66)` | pending source verification | sigmoid quality | `82f7ebc50213c87cc871f83721a11b192dbde2578d3ab5b702c77aa6388b5248` |
| `w_raise_robust.keras` | unresolved W/lateral raise | 4,483,452 | pending verification | pending verification | sigmoid quality | `73d9b185b30696bddde0c8c2fba17c8995a1c2f26e58709d1027c084116d8a07` |
| `knee_extension_robust.keras` | `knee_extension` | 4,483,442 | `(1,63,66)` | pelvis width | sigmoid quality | `f13684b9d4d6b2f2eb842f49ce5c154fa5be0d0373abeb4b7bc2660c624e5750` |
| `wall_pushup_robust.keras` | future `wall_pushup` | 4,483,452 | `(1,77,66)` | pelvis width | sigmoid quality | `b6b2be3c577af06e910cd6581c268c7d8c3ecbac418d93804478b66812906d31` |
| `hip_march_robust.keras` | future `hip_march` | 4,483,452 | `(1,69,66)` | pelvis width | sigmoid quality | `d13340b8c0827f73a1a7be7a464ab36954a2a6540b9d86bce9faff7c322d608d` |
| `shoulder_extension_robust.keras` | future `shoulder_extension` | 4,483,442 | `(1,67,66)` | pelvis width | sigmoid quality | `75103d84e3835dc7b3846028503f42b2b2fe05410af23ebfcd837fcce19af008` |
| `shoulder_scaption_robust.keras` | future `shoulder_scaption` | 4,483,452 | `(1,66,66)` | pelvis width | sigmoid quality | `76590ccdfbdbc841edc675af1c3c46c5b06f36baec781e7398b72ded48d1f6fe` |

## Clearance State

- Source README claims MIT, but the reviewed source folder has no `LICENSE` file.
- Model cards, training-data lineage, and redistribution terms are absent.
- Reported evaluation has model-selection leakage caveats and is not independent
  validation for Movena.
- Hashes identify the reviewed local files only; they do not establish ownership,
  safety, efficacy, or permission to redistribute.
