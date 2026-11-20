"""Recompute the GraSS numbers of the manuscript and its supplement from the files in this repository.

Usage:  python verify.py          (Python 3.8+, standard library only)

Every line prints the value recomputed from the files next to the value printed in the paper. A value
matches ("OK") when it lies within half a unit of the last printed digit. mAP and AP are percentages;
"s.d." is the sample standard deviation over seeds.
"""
import csv, glob, json, math, os, statistics as st

ROOT = os.path.dirname(os.path.abspath(__file__))
P = lambda *a: os.path.join(ROOT, *a)
pct = lambda x: 100.0 * x
results = []


def show(label, value, paper):
    good = abs(value - paper) <= 0.05 + 1e-9
    results.append(good)
    print(f"  {label:<64s} {value:9.4f}   paper: {paper:<6}  {'OK' if good else 'CHECK'}")


def rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def jl(path):
    with open(path) as f:
        return json.load(f)


def seed_dirs(pattern):
    return sorted(glob.glob(P(pattern)), key=lambda d: int(d.rsplit("seed", 1)[1]))


def msd(xs):
    return st.mean(xs), (st.stdev(xs) if len(xs) > 1 else 0.0)


def tertiles(classes, positives, ap):
    """Mean AP of head / medium / tail thirds: classes with at least one positive, ranked by their number
    of positives (descending; ties keep the class order), split into three near-equal groups."""
    order = sorted([c for c in classes if positives[c] > 0], key=lambda c: -positives[c])
    n = len(order); a, b = math.ceil(n / 3), math.ceil(2 * n / 3)
    return [pct(st.mean(ap[c] for c in part)) for part in (order[:a], order[a:b], order[b:])]


# =====================================================================================================
print("TACO, distributed test split (1,446 labelled clips of Town 10HD), final checkpoint")
taco = {m: [jl(os.path.join(d, "test_metrics.json")) for d in seed_dirs(f"taco/{m}/seed*")]
        for m in ("grass", "grass_no_distillation")}
G = ("C", "K", "P", "C+", "K+", "P+")

print(" Table I and Supplementary Table S7: GraSS")
g = taco["grass"]
for s, (r, paper) in enumerate(zip(g, (65.7, 66.6, 67.1))):
    show(f"seed {s}, centre clip", pct(r["map_centre_clip"]), paper)
m, sd = msd([pct(r["map_centre_clip"]) for r in g])
show("mean of 3 seeds (Table I)", m, 66.5); show("  s.d.", sd, 0.7)
for grp, paper in zip(G, (64.8, 57.6, 62.8, 77.7, 69.1, 65.1)):
    show(f"group {grp} (Table I)", st.mean(pct(r["map_centre_clip_per_group"][grp]) for r in g), paper)
show("5 clips (Table S7)", st.mean(pct(r["map_5_clips"]) for r in g), 67.8)
show("5 clips + mirror (Section IV-D1, Table S7)", st.mean(pct(r["map_5_clips_and_mirror"]) for r in g), 68.4)

print(" Supplementary Tables S7 and S9: GraSS without distillation (the three teachers)")
h = taco["grass_no_distillation"]
for s, (r, paper) in enumerate(zip(h, (63.4, 62.2, 64.7))):
    show(f"seed {s}, centre clip", pct(r["map_centre_clip"]), paper)
m, sd = msd([pct(r["map_centre_clip"]) for r in h])
show("mean of 3 seeds", m, 63.4); show("  s.d.", sd, 1.3)
show("5 clips", st.mean(pct(r["map_5_clips"]) for r in h), 64.7)
show("5 clips + mirror", st.mean(pct(r["map_5_clips_and_mirror"]) for r in h), 65.2)
for grp, paper in zip(G, (62.2, 53.7, 58.6, 75.4, 66.8, 62.0)):
    show(f"group {grp} (Table S9)", st.mean(pct(r["map_centre_clip_per_group"][grp]) for r in h), paper)

print(" Table VII and Supplementary Table S17: per-class AP of GraSS (mean of 3 seeds; class files write")
print(" the two-wheeler type K as 'b', as in the TACO annotation)")
pcs = [rows(os.path.join(d, "test_per_class_ap.csv")) for d in seed_dirs("taco/grass/seed*")]
classes = [r["class"] for r in pcs[0]]
positives = {r["class"]: int(r["test_positives"]) for r in pcs[0]}
ap = {c: st.mean(float(pc[i]["ap_centre_clip"]) for pc in pcs) for i, c in enumerate(classes)}
show("mean of per-class AP (= mAP)", pct(st.mean(ap[c] for c in classes if positives[c] > 0)), 66.5)
for name, v, paper in zip(("head", "medium", "tail"), tertiles(classes, positives, ap), (66.9, 70.2, 62.2)):
    show(f"{name} tertile (Table VII)", v, paper)
TAIL = [("b+:z1-z4", 1, 0.7), ("b+:z4-z3", 10, 64.5), ("c+:z1-z4", 10, 46.0), ("b+:z3-z2", 13, 76.9),
        ("b+:z2-z1", 15, 66.3), ("b:z3-z4", 33, 33.9), ("b+:z2-z4", 34, 79.2), ("b:z3-z2", 35, 59.2),
        ("b:z4-z2", 35, 59.7), ("b:z2-z1", 36, 60.7), ("b+:z4-z2", 37, 94.6), ("b:z1-z4", 37, 80.2),
        ("c+:z3-z2", 37, 85.1), ("b+:z4-z1", 38, 81.3), ("p+:c4-c3", 38, 42.9), ("b+:z1-z3", 39, 64.3),
        ("b:z4-z1", 39, 44.6), ("b:z2-z4", 40, 55.2), ("b:z2-z3", 41, 44.6), ("c+:z4-z3", 44, 70.8),
        ("p+:c4-c1", 44, 96.2)]
pos_ok = all(positives[c] == n for c, n, _ in TAIL)
print(f"  test positives of the 21 tail classes as printed in Table S17: {'OK' if pos_ok else 'CHECK'}")
results.append(pos_ok)
for c, n, paper in TAIL:
    show(f"{c.upper().replace('B', 'K')} ({n} test positives)", pct(ap[c]), paper)
show("tail mean (Table S17)", pct(st.mean(ap[c] for c, _, _ in TAIL)), 62.2)


# =====================================================================================================
def oats_runs(pattern):
    out = []
    for d in seed_dirs(pattern):
        summ = jl(os.path.join(d, "summary.json"))
        log = rows(os.path.join(d, "epoch_log.csv"))
        sel = next(r for r in log if int(r["epoch"]) == summ["selected_epoch"])
        out.append({"seed": int(d.rsplit("seed", 1)[1]), "dir": d, "log": log, "sum": summ, "sel": sel})
    return out


print("\nOATS (Table II, Supplementary Tables S8 and S9): checkpoint selected by the training script")
print(" (epoch with the highest heldout_map_selection_score); centre-clip mAP reported at that epoch")
OATS = {
    "grass_kinetics400": {"seeds": {1: (57.9, 57.0, 57.3, 59.2), 2: (60.0, 62.3, 59.7, 62.2), 3: (60.8, 61.6, 60.3, 63.5)},
                          "split": {1: (57.8, 1.0), 2: (61.0, 1.4), 3: (61.5, 1.4)},
                          "mean": 60.1, "last": 58.6, "nested": 61.0, "five_mirror": 63.1,
                          "groups": {1: (78.9, 25.5, 58.8, 35.8, 48.5), 2: (82.9, 36.0, 61.6, 20.5, 57.2),
                                     3: (79.8, 26.0, 66.7, 24.5, 60.8)}},
    "grass_taco_pretrained": {"seeds": {1: (60.9, 61.9, 64.2), 2: (65.1, 65.2, 65.6), 3: (62.2, 60.2, 65.7)},
                              "split": {1: (62.3, 1.7), 2: (65.3, 0.2), 3: (62.7, 2.8)},
                              "mean": 63.4, "last": 60.5, "nested": 63.9, "five_mirror": None, "groups": None},
}
for name, ref in OATS.items():
    print(f" {name}")
    best, last, curves, five_mirror = [], [], {}, []
    for k in (1, 2, 3):
        R = oats_runs(f"oats/{name}/S{k}/seed*")
        v = [pct(r["sum"]["map_centre_clip_at_selected_epoch"]) for r in R]
        for r, x, paper in zip(R, v, ref["seeds"][k]):
            show(f"S{k}, seed {r['seed']} (Table S8)", x, paper)
        m, sd = msd(v)
        show(f"S{k}, mean of {len(R)} seeds (Table II)", m, ref["split"][k][0]); show(f"S{k}, s.d. (Table S8)", sd, ref["split"][k][1])
        if ref["groups"]:
            for grp, paper in zip(("C", "K", "P", "C+", "P+"), ref["groups"][k]):
                show(f"S{k}, group {grp} (Table S9)", st.mean(pct(float(r["sel"][f"heldout_map_centre_clip_{grp}"])) for r in R), paper)
        best.append(m)
        last.append(st.mean(pct(r["sum"]["map_centre_clip_last_epoch"]) for r in R))
        five_mirror += [pct(float(r["sel"]["heldout_map_selection_score"])) for r in R]
        curves[k] = [{int(x["epoch"]): pct(float(x["heldout_map_centre_clip"])) for x in r["log"]} for r in R]
    show("S1-S3 mean (Table II)", st.mean(best), ref["mean"])
    show("S1-S3 mean, last epoch, no selection", st.mean(last), ref["last"])
    epochs = sorted(set.intersection(*[set(c) for c in curves[1]]))
    e_star = max(epochs, key=lambda e: st.mean(c[e] for c in curves[1]))
    nested = st.mean(st.mean(c[e_star] for c in curves[k]) for k in (2, 3))
    show(f"nested: epoch {e_star} chosen on S1 (mean curve), mean of S2 and S3", nested, ref["nested"])
    if ref["five_mirror"]:
        show("S1-S3, 5 clips + mirror at the selected epoch (Table S8)", st.mean(five_mirror), ref["five_mirror"])

print("\nOATS S1 ablations")
ARMS = ["grass", "binding_free", "no_label_structure_graph", "no_factored_label_code", "no_null_option",
        "no_post_fusion_reattention", "lm_embeddings_and_annotation_order_graph"]
A = {n: {r["seed"]: r for r in oats_runs(f"oats/ablations_S1/{n}/seed*")} for n in ARMS}
print(" Table V (centre clip, paired seeds 0-3)")
ss = sorted(A["binding_free"])
for key, when, pg, pb, pd in [("map_centre_clip_at_selected_epoch", "best epoch", 57.8, 52.5, -5.3),
                              ("map_centre_clip_last_epoch", "last epoch", 56.3, 51.3, -5.0)]:
    vg = st.mean(pct(A["grass"][s]["sum"][key]) for s in ss)
    vb = st.mean(pct(A["binding_free"][s]["sum"][key]) for s in ss)
    show(f"GraSS, {when}", vg, pg); show(f"binding-free, {when}", vb, pb); show(f"  difference, {when}", vb - vg, pd)
print(" Table VI (classes with >= 10 positives; six paired seeds; difference to GraSS, mean and s.d.)")
base = A["grass"]
show("GraSS, best epoch", st.mean(pct(base[s]["sum"]["map_centre_clip_classes_ge10_at_selected_epoch"]) for s in base), 64.2)
show("GraSS, last epoch", st.mean(pct(base[s]["sum"]["map_centre_clip_classes_ge10_last_epoch"]) for s in base), 61.1)
TABLE_VI = [("no_label_structure_graph", (-0.2, 1.5), (0.4, 1.5)), ("no_factored_label_code", (-0.5, 0.8), (1.0, 1.1)),
            ("no_null_option", (-0.3, 1.2), (0.1, 1.1)), ("no_post_fusion_reattention", (-0.6, 1.2), (-0.4, 1.7)),
            ("lm_embeddings_and_annotation_order_graph", (-0.4, 0.8), (0.3, 1.2))]
for n, pbest, plast in TABLE_VI:
    for key, (pm, ps), when in [("map_centre_clip_classes_ge10_at_selected_epoch", pbest, "best"),
                                ("map_centre_clip_classes_ge10_last_epoch", plast, "last")]:
        d = [pct(A[n][s]["sum"][key] - base[s]["sum"][key]) for s in sorted(A[n]) if s in base]
        m, sd = msd(d)
        show(f"{n}, {when} (n={len(d)})", m, pm); show("  s.d.", sd, ps)


def oats_tertiles(run_list):
    pcs = [rows(os.path.join(r["dir"], "reported_checkpoint_per_class_ap.csv")) for r in run_list]
    cls = [x["class"] for x in pcs[0] if x["ap_centre_clip"] != ""]
    pos = {x["class"]: int(x["heldout_positives"]) for x in pcs[0]}
    apm = {c: st.mean(float(next(x for x in pc if x["class"] == c)["ap_centre_clip"]) for pc in pcs) for c in cls}
    return tertiles(cls, pos, apm)


print(" Table VII (classes ranked by held-out positives; AP at the selected epoch, mean over seeds)")
tg = oats_tertiles([A["grass"][s] for s in ss])
tb = oats_tertiles([A["binding_free"][s] for s in ss])
for lab, x, y, px, py, pdiff in zip(("head", "medium", "tail"), tg, tb, (66.3, 64.8, 40.5), (64.3, 61.8, 29.5), (2.1, 3.0, 11.0)):
    show(f"S1 GraSS, {lab}", x, px); show(f"S1 binding-free, {lab}", y, py); show(f"  difference (Section IV-G), {lab}", x - y, pdiff)
t = [oats_tertiles(oats_runs(f"oats/grass_kinetics400/S{k}/seed*")) for k in (1, 2, 3)]
for i, (lab, p) in enumerate(zip(("head", "medium", "tail"), (71.4, 66.6, 40.5))):
    show(f"S1-S3 GraSS, {lab}", st.mean(x[i] for x in t), p)

print(f"\n{sum(results)} of {len(results)} values match the paper to the printed precision.")
