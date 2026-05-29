"""
prepare_dataset.py — run once, offline, before sharing the tutorial.

Assumes:
  data_root/
    images/          1154 JPEG files
    original_labels/ original 7-class YOLO OBB labels (already renamed)

What it does:
  1. Reads original_labels/, writes labels/ keeping only class-0 (M2) lines.
  2. Splits images that have ≥1 class-0 annotation 80 / 10 / 10.
  3. Copies images + labels into dataset/train, dataset/val, dataset/test.
  4. Writes dataset/data.yaml ready for ultralytics YOLO training.

Usage:
  python prepare_dataset.py --data_root "/Users/msimard/data/hand xray-OBB-M2"
"""

import argparse
import random
import shutil
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data_root",
        default="/Users/msimard/data/hand xray-OBB-M2",
        help="Root folder containing images/ and original_labels/",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--val_frac", type=float, default=0.1)
    parser.add_argument("--test_frac", type=float, default=0.1)
    return parser.parse_args()


def make_class0_labels(data_root: Path) -> list[str]:
    """Create labels/ with class-0-only files. Returns stems with ≥1 class-0 box."""
    orig_dir = data_root / "original_labels"
    labels_dir = data_root / "labels"
    labels_dir.mkdir(exist_ok=True)

    valid_stems = []
    for txt in sorted(orig_dir.glob("*.txt")):
        lines = txt.read_text().splitlines()
        class0_lines = [l for l in lines if l.strip() and l.split()[0] == "0"]
        (labels_dir / txt.name).write_text("\n".join(class0_lines) + "\n" if class0_lines else "")
        if class0_lines:
            valid_stems.append(txt.stem)

    total = len(list(orig_dir.glob("*.txt")))
    print(f"Images with ≥1 class-0 annotation: {len(valid_stems)} / {total}")
    return valid_stems


def split_stems(stems: list[str], val_frac: float, test_frac: float, seed: int):
    rng = random.Random(seed)
    shuffled = stems[:]
    rng.shuffle(shuffled)
    n = len(shuffled)
    n_test = int(n * test_frac)
    n_val = int(n * val_frac)
    test = shuffled[:n_test]
    val = shuffled[n_test: n_test + n_val]
    train = shuffled[n_test + n_val:]
    return train, val, test


def copy_split(stems: list[str], split_name: str, data_root: Path, dataset_dir: Path):
    img_src = data_root / "images"
    lbl_src = data_root / "labels"
    img_dst = dataset_dir / split_name / "images"
    lbl_dst = dataset_dir / split_name / "labels"
    img_dst.mkdir(parents=True, exist_ok=True)
    lbl_dst.mkdir(parents=True, exist_ok=True)

    for stem in stems:
        matches = list(img_src.glob(f"{stem}.*"))
        if not matches:
            print(f"  WARNING: no image found for {stem}")
            continue
        shutil.copy2(matches[0], img_dst / matches[0].name)
        shutil.copy2(lbl_src / f"{stem}.txt", lbl_dst / f"{stem}.txt")

    print(f"  {split_name:5s}: {len(stems)} images")


def write_yaml(dataset_dir: Path):
    yaml_content = f"""path: {dataset_dir.resolve()}
train: train/images
val: val/images
test: test/images

nc: 1
names:
  0: M2
"""
    (dataset_dir / "data.yaml").write_text(yaml_content)
    print(f"Wrote {dataset_dir / 'data.yaml'}")


def main():
    args = parse_args()
    data_root = Path(args.data_root)
    dataset_dir = data_root / "SS-day4-hand-xray-m2-dataset"

    if dataset_dir.exists():
        print(f"dataset/ already exists at {dataset_dir}. Delete it to re-run.")
        return

    print("Step 1: Creating class-0-only labels/ …")
    valid_stems = make_class0_labels(data_root)

    print("Step 2: Splitting …")
    train, val, test = split_stems(valid_stems, args.val_frac, args.test_frac, args.seed)

    print("Step 3: Copying files …")
    copy_split(train, "train", data_root, dataset_dir)
    copy_split(val, "val", data_root, dataset_dir)
    copy_split(test, "test", data_root, dataset_dir)

    print("Step 4: Writing data.yaml …")
    write_yaml(dataset_dir)

    print(f"\nDone.  train={len(train)}  val={len(val)}  test={len(test)}  total={len(valid_stems)}")


if __name__ == "__main__":
    main()
