# GraSS: per-epoch logs, configurations and results

This repository accompanies the manuscript *GraSS: Graph-Guided Semantic Slot Attention for Efficient
Multi-Label Activity Recognition in Autonomous Driving* (IEEE Transactions on Intelligent Transportation
Systems, under review). It contains, for every GraSS run reported in Tables I, II and V–VII of the paper
and in the per-seed, per-group and per-class tables of its supplement:

- the complete configuration of the run (`config.json`);
- one row per training epoch (`training_log.csv` or `epoch_log.csv`);
- the test results (TACO) or the held-out results of the selected checkpoint (OATS), including the AP of
  every class.

The code will be released upon publication.

## Check the numbers

```bash
python verify.py
```

The script uses the Python standard library only. It recomputes 148 values of the paper from the files
below and prints each next to the printed value. A value matches when it lies within half a unit of the
last printed digit. The current files reproduce all 148.

## Contents

```
taco/
  summary.csv                        test mAP of every TACO run, one row per seed
  grass/seed{0,1,2}/                 the reported GraSS model (Table I)
  grass_no_distillation/seed{0,1,2}/ the three GraSS teachers of the reported model (Supp. Tables S7, S9)
oats/
  grass_kinetics400/S{1,2,3}/seed{0..3}/      GraSS, Kinetics-400 initialization (Table II)
  grass_taco_pretrained/S{1,2,3}/seed{0..2}/  GraSS, initialized from a TACO-trained GraSS (Table II)
  ablations_S1/<arm>/seed*/                   OATS S1 controls (Tables V, VI, VII; Supp. Fig. S1)
verify.py
```

`oats/ablations_S1/` holds one directory per arm:

| Directory | Arm | Seeds |
|---|---|---|
| `grass` | GraSS (reference of every paired difference) | 0–5 |
| `binding_free` | uniform binding map in training and inference (Table V) | 0–3 |
| `no_label_structure_graph` | no label-structure graph (Table VI) | 0–5 |
| `no_factored_label_code` | free per-class code instead of the factored code (Table VI) | 0–5 |
| `no_null_option` | no null option (Table VI) | 0–5 |
| `no_post_fusion_reattention` | no post-fusion re-attention (Table VI) | 0–5 |
| `lm_embeddings_and_annotation_order_graph` | language-model label embeddings with the annotation-order graph (Table VI) | 0–5 |

Seeds 0–3 of `oats/ablations_S1/grass` have the same configuration as `oats/grass_kinetics400/S1`. Training
is deterministic, and their logs are identical; seeds 4 and 5 extend the reference to the six paired seeds
of Table VI.

## Files of one run

**TACO** (`taco/<model>/seed<k>/`)

| File | Content |
|---|---|
| `config.json` | every option of the training script for this run |
| `training_log.csv` | per epoch: learning rate and training losses |
| `test_metrics.json` | test split: centre-clip mAP, per agent group (C car, K two-wheeler, P pedestrian; + group of agents), 5 clips, 5 clips + mirror, classes with ≥ 10 test positives |
| `test_per_class_ap.csv` | test split: number of positives and centre-clip AP of every class |

**OATS** (`oats/.../seed<k>/`)

| File | Content |
|---|---|
| `config.json` | every option of the training script for this run |
| `epoch_log.csv` | per epoch: learning rate, training losses, and the held-out fold's mAP (centre clip; selection score; 5 clips; classes with ≥ 10 positives; per agent group) |
| `summary.json` | the selected epoch, the selection rule, and the centre-clip mAP (all classes and ≥ 10 positives) at the selected and at the last epoch |
| `reported_checkpoint_per_class_ap.csv` | held-out fold, selected epoch: number of positives and centre-clip AP of every class |

All metrics are fractions in [0, 1]; the paper prints them as percentages.

## Protocols and definitions

- **Centre clip** (`*_centre_clip`): one 16-frame clip at the centre of the video, single view. This is
  the metric of every table of the paper unless stated otherwise.
- **5 clips** and **5 clips + mirror**: the mean of the scores of five clips; with mirror, the scores of
  the horizontally mirrored clips are mapped back through the reflection of the intersection and averaged in.
- **TACO**: the split distributed with the dataset. Training uses the training and validation towns
  (01, 02, 04, 05, 07 and 03); the test town (10HD) is unseen. The data loader skips clips with fewer than
  50 frames, as the Action-Slot loader does, so 3,629 of the 3,730 training and validation clips are used
  (`num_train_videos`); all 1,446 labelled test clips are scored. Every model is evaluated once, at the
  final epoch of a fixed schedule. Because the validation town is part of training, per-epoch validation
  metrics of these runs would be in-sample and are not included.
- **OATS**: the three official folds S1–S3; the training script evaluates the held-out fold after every
  epoch. Training stops after 24 epochs (`stop_epoch`). The **selected epoch** is the epoch with the highest
  `heldout_map_selection_score` (the 5-clip + mirror mAP), the checkpoint criterion of the training script;
  the paper reports the centre-clip mAP at that epoch. Because the held-out fold is also used for
  selection, the paper reports two further readings: the **last epoch**, and a **nested** score in which the
  epoch is chosen on the mean S1 curve and applied unchanged to S2 and S3 (mean of S2 and S3).
- **Tertiles** (Table VII): classes with at least one positive in the evaluated split, ranked by their
  number of positives (ties keep the class order), divided into three near-equal groups.
- **Classes with ≥ 10 positives** (`*_ge10`): the pre-registered metric of the OATS component ablations.

## Not included

- Model weights and code: released upon publication.
- Videos, annotations and per-video scores: OATS and TACO are distributed by their authors under their own
  terms.
- Runs of other methods (the re-trained Action-Slot and the video large multimodal models): this repository
  covers GraSS runs only.
