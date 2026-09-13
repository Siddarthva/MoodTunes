import os
import sys
import json
import pickle
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from scipy.signal import resample_poly
except ImportError:
    print("ERROR: scipy is missing.")
    print("Run:")
    print("python -m pip install numpy pandas scipy")
    sys.exit(1)


# ============================================================
# CONFIG
# ============================================================

PROJECT_ROOT = Path(r"D:\Major Project\Fall_Research")

DATASET_ROOT = PROJECT_ROOT / "Dataset"
RAW_ROOT = DATASET_ROOT / "Replay_Raw"

SENS_ROOT = RAW_ROOT / "SensSmartTech"
SENS_CSV_ROOT = SENS_ROOT / "CSV"

OUTPUT_ROOT = DATASET_ROOT / "Replay"

SISFALL_PARSED = (
    DATASET_ROOT
    / "Processed"
    / "SisFall_parsed_6channel.pkl"
)

# ------------------------------------------------------------
# DEMO
# ------------------------------------------------------------

DURATION_SEC = 300

# ECG
ECG_SOURCE_FS = 500
ECG_TARGET_FS = 250
ECG_WINDOW = 250
ECG_STEP = 125

# PPG
PPG_SOURCE_FS = 100
PPG_TARGET_FS = 64
PPG_WINDOW = 512
PPG_STEP = 256

# IMU
IMU_FS = 200
IMU_WINDOW = 256
IMU_STEP = 128


# ============================================================
# PHYSIONET
# ============================================================

PHYSIONET_BASE = (
    "https://physionet.org/files/"
    "senssmarttech/1.0.0/CSV/"
)

# These are real files visible in the PhysioNet CSV directory.
# Each recording is approximately 30 seconds.
#
# We download enough recordings to construct 5 minutes.

RECORDINGS = [
    "10_18-12-33",
    "10_18-13-23",
    "10_18-14-33",

    "17_08-34-00",
    "17_08-35-27",
    "17_08-37-09",
    "17_08-37-55",
    "17_08-45-39",
    "17_08-46-25",
    "17_08-47-13",
    "17_08-48-47",

    "20_15-41-04",
    "20_15-42-15",
    "20_15-43-30",
    "20_15-45-51",
    "20_15-49-37",
]


# ============================================================
# HELPERS
# ============================================================

def banner(text):
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


def download(url, destination):

    destination = Path(destination)

    if destination.exists() and destination.stat().st_size > 0:
        print(f"[SKIP] {destination.name}")
        return

    print(f"[DOWNLOAD] {url}")

    try:

        urllib.request.urlretrieve(
            url,
            destination
        )

        print(
            f"[OK] {destination.name} "
            f"({destination.stat().st_size / 1024:.1f} KB)"
        )

    except Exception as e:

        if destination.exists():
            destination.unlink()

        print(
            f"[ERROR] Could not download "
            f"{destination.name}"
        )

        raise e


def read_csv(path):

    try:
        df = pd.read_csv(path)

    except Exception:

        df = pd.read_csv(
            path,
            header=None
        )

    # Convert possible numerical columns
    for col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df = df.dropna(
        axis=1,
        how="all"
    )

    return df


def choose_column(df, keywords):

    # First try column names
    for col in df.columns:

        name = str(col).lower()

        for keyword in keywords:

            if keyword in name:

                values = pd.to_numeric(
                    df[col],
                    errors="coerce"
                ).dropna()

                if len(values) > 100:

                    return values.to_numpy(
                        dtype=np.float64
                    )

    # Fallback:
    # choose longest numerical column
    best = None
    best_length = 0

    for col in df.columns:

        values = pd.to_numeric(
            df[col],
            errors="coerce"
        ).dropna()

        if len(values) > best_length:

            best_length = len(values)

            best = values.to_numpy(
                dtype=np.float64
            )

    return best


def resample(signal, source_fs, target_fs):

    signal = np.asarray(
        signal,
        dtype=np.float64
    )

    signal = np.nan_to_num(
        signal
    )

    if source_fs == target_fs:
        return signal.astype(np.float32)

    from math import gcd

    g = gcd(
        int(source_fs),
        int(target_fs)
    )

    up = target_fs // g
    down = source_fs // g

    result = resample_poly(
        signal,
        up,
        down
    )

    return result.astype(
        np.float32
    )


# ============================================================
# STEP 1
# DOWNLOAD ONLY REQUIRED ECG/PPG FILES
# ============================================================

def download_senssmarttech():

    banner(
        "STEP 1 - DOWNLOAD ECG + PPG"
    )

    SENS_CSV_ROOT.mkdir(
        parents=True,
        exist_ok=True
    )

    for recording in RECORDINGS:

        for sensor in ["ecg", "ppg"]:

            filename = (
                f"{recording}_{sensor}.csv"
            )

            url = (
                PHYSIONET_BASE
                + filename
            )

            destination = (
                SENS_CSV_ROOT
                / filename
            )

            download(
                url,
                destination
            )

    print(
        "\n[OK] ECG + PPG download complete."
    )


# ============================================================
# STEP 2
# BUILD ECG
# ============================================================

def build_ecg():

    banner(
        "STEP 2 - BUILD 5 MINUTE ECG"
    )

    pieces = []

    required = (
        DURATION_SEC
        * ECG_TARGET_FS
    )

    collected = 0

    for recording in RECORDINGS:

        path = (
            SENS_CSV_ROOT
            / f"{recording}_ecg.csv"
        )

        df = read_csv(path)

        signal = choose_column(
            df,
            [
                "ecg",
                "lead ii",
                "lead i"
            ]
        )

        if signal is None:
            continue

        signal = resample(
            signal,
            ECG_SOURCE_FS,
            ECG_TARGET_FS
        )

        pieces.append(signal)

        collected += len(signal)

        print(
            f"{recording}: "
            f"{len(signal):,} samples"
        )

        if collected >= required:
            break

    if not pieces:

        raise RuntimeError(
            "No ECG data found."
        )

    signal = np.concatenate(
        pieces
    )

    # Ensure exactly 5 minutes
    if len(signal) < required:

        repeats = int(
            np.ceil(
                required / len(signal)
            )
        )

        signal = np.tile(
            signal,
            repeats
        )

    signal = signal[:required]

    output = pd.DataFrame({
        "timestamp_sec":
            np.arange(required)
            / ECG_TARGET_FS,

        "ecg": signal
    })

    path = (
        OUTPUT_ROOT
        / "demo_ecg_5min.csv"
    )

    output.to_csv(
        path,
        index=False
    )

    print(
        f"\n[OK] {path}"
    )

    print(
        f"Samples: {len(signal):,}"
    )

    return signal


# ============================================================
# STEP 3
# BUILD PPG
# ============================================================

def build_ppg():

    banner(
        "STEP 3 - BUILD 5 MINUTE PPG"
    )

    pieces = []

    required = (
        DURATION_SEC
        * PPG_TARGET_FS
    )

    collected = 0

    for recording in RECORDINGS:

        path = (
            SENS_CSV_ROOT
            / f"{recording}_ppg.csv"
        )

        df = read_csv(path)

        signal = choose_column(
            df,
            [
                "ppg",
                "pleth",
                "bvp"
            ]
        )

        if signal is None:
            continue

        signal = resample(
            signal,
            PPG_SOURCE_FS,
            PPG_TARGET_FS
        )

        pieces.append(signal)

        collected += len(signal)

        print(
            f"{recording}: "
            f"{len(signal):,} samples"
        )

        if collected >= required:
            break

    if not pieces:

        raise RuntimeError(
            "No PPG data found."
        )

    signal = np.concatenate(
        pieces
    )

    if len(signal) < required:

        repeats = int(
            np.ceil(
                required / len(signal)
            )
        )

        signal = np.tile(
            signal,
            repeats
        )

    signal = signal[:required]

    output = pd.DataFrame({
        "timestamp_sec":
            np.arange(required)
            / PPG_TARGET_FS,

        "ppg": signal
    })

    path = (
        OUTPUT_ROOT
        / "demo_ppg_5min.csv"
    )

    output.to_csv(
        path,
        index=False
    )

    print(
        f"\n[OK] {path}"
    )

    print(
        f"Samples: {len(signal):,}"
    )

    return signal


# ============================================================
# STEP 4
# LOAD YOUR EXISTING SISFALL PARSED DATA
# ============================================================

def load_imu():

    banner(
        "STEP 4 - BUILD 5 MINUTE IMU"
    )

    if not SISFALL_PARSED.exists():

        raise FileNotFoundError(
            "\nYour parsed SisFall file was not found:\n"
            f"{SISFALL_PARSED}\n\n"
            "You already created this file earlier, "
            "so please verify that it still exists."
        )

    print(
        f"[LOAD] {SISFALL_PARSED}"
    )

    with open(
        SISFALL_PARSED,
        "rb"
    ) as f:

        data = pickle.load(f)

    pieces = []

    # Handle dictionary
    if isinstance(data, dict):

        iterable = data.values()

    else:

        iterable = data

    for item in iterable:

        try:

            if isinstance(item, dict):

                arr = None

                for key in [
                    "data",
                    "signal",
                    "samples",
                    "array"
                ]:

                    if key in item:

                        arr = np.asarray(
                            item[key]
                        )

                        break

                if arr is None:
                    continue

            else:

                arr = np.asarray(
                    item
                )

            if (
                arr.ndim == 2
                and arr.shape[1] >= 6
            ):

                pieces.append(
                    arr[:, :6]
                )

        except Exception:
            continue

    if not pieces:

        raise RuntimeError(
            "Could not read 6-channel "
            "IMU data from SisFall pickle."
        )

    imu = np.concatenate(
        pieces,
        axis=0
    )

    required = (
        DURATION_SEC
        * IMU_FS
    )

    if len(imu) < required:

        repeats = int(
            np.ceil(
                required / len(imu)
            )
        )

        imu = np.tile(
            imu,
            (repeats, 1)
        )

    imu = imu[
        :required,
        :6
    ]

    output = pd.DataFrame({

        "timestamp_sec":
            np.arange(required)
            / IMU_FS,

        "acc_x": imu[:, 0],
        "acc_y": imu[:, 1],
        "acc_z": imu[:, 2],

        "gyro_x": imu[:, 3],
        "gyro_y": imu[:, 4],
        "gyro_z": imu[:, 5]
    })

    path = (
        OUTPUT_ROOT
        / "demo_imu_5min.csv"
    )

    output.to_csv(
        path,
        index=False
    )

    print(
        f"[OK] {path}"
    )

    print(
        f"Shape: {imu.shape}"
    )

    print(
        f"Duration: "
        f"{len(imu)/IMU_FS:.2f} sec"
    )

    return imu


# ============================================================
# STEP 5
# WINDOWS
# ============================================================

def make_windows(
    signal,
    window,
    step,
    filename,
    fs
):

    windows = []

    timestamps = []

    for start in range(
        0,
        len(signal) - window + 1,
        step
    ):

        end = start + window

        windows.append(
            signal[start:end]
        )

        timestamps.append(
            start / fs
        )

    windows = np.asarray(
        windows,
        dtype=np.float32
    )

    timestamps = np.asarray(
        timestamps,
        dtype=np.float32
    )

    path = (
        OUTPUT_ROOT
        / filename
    )

    np.savez_compressed(
        path,
        windows=windows,
        timestamps=timestamps
    )

    print(
        f"[OK] {filename}"
    )

    print(
        f"     shape = {windows.shape}"
    )


def create_windows(
    ecg,
    ppg,
    imu
):

    banner(
        "STEP 5 - CREATE MODEL WINDOWS"
    )

    make_windows(
        ecg,
        ECG_WINDOW,
        ECG_STEP,
        "demo_ecg_windows.npz",
        ECG_TARGET_FS
    )

    make_windows(
        ppg,
        PPG_WINDOW,
        PPG_STEP,
        "demo_ppg_windows.npz",
        PPG_TARGET_FS
    )

    make_windows(
        imu,
        IMU_WINDOW,
        IMU_STEP,
        "demo_imu_windows.npz",
        IMU_FS
    )


# ============================================================
# STEP 6
# MANIFEST
# ============================================================

def create_manifest():

    banner(
        "STEP 6 - CREATE MANIFEST"
    )

    manifest = {

        "mode":
            "DATASET_REPLAY",

        "demo_duration_seconds":
            DURATION_SEC,

        "clinical_use":
            False,

        "live_sensor_data":
            False,

        "datasets": {

            "ECG": {
                "name":
                    "SensSmartTech",
                "source":
                    "PhysioNet",
                "source_fs":
                    ECG_SOURCE_FS,
                "replay_fs":
                    ECG_TARGET_FS,
                "window":
                    ECG_WINDOW
            },

            "PPG": {
                "name":
                    "SensSmartTech",
                "source":
                    "PhysioNet",
                "source_fs":
                    PPG_SOURCE_FS,
                "replay_fs":
                    PPG_TARGET_FS,
                "window":
                    PPG_WINDOW
            },

            "IMU": {
                "name":
                    "SisFall",
                "source":
                    "Existing project parsed dataset",
                "replay_fs":
                    IMU_FS,
                "channels": [
                    "acc_x",
                    "acc_y",
                    "acc_z",
                    "gyro_x",
                    "gyro_y",
                    "gyro_z"
                ],
                "window":
                    IMU_WINDOW
            }
        }
    }

    path = (
        OUTPUT_ROOT
        / "demo_manifest.json"
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            manifest,
            f,
            indent=4
        )

    print(
        f"[OK] {path}"
    )


# ============================================================
# VALIDATION
# ============================================================

def validate():

    banner(
        "FINAL VALIDATION"
    )

    expected = {

        "demo_ecg_5min.csv":
            ECG_TARGET_FS * DURATION_SEC,

        "demo_ppg_5min.csv":
            PPG_TARGET_FS * DURATION_SEC,

        "demo_imu_5min.csv":
            IMU_FS * DURATION_SEC
    }

    for filename, expected_rows in expected.items():

        path = OUTPUT_ROOT / filename

        df = pd.read_csv(path)

        print(
            f"{filename:30s}"
            f" rows={len(df):,}"
            f" expected={expected_rows:,}"
        )

        if len(df) != expected_rows:

            raise RuntimeError(
                f"{filename} has incorrect length."
            )

    print(
        "\nALL THREE DATASETS ARE EXACTLY "
        "5 MINUTES."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    banner(
        "5-MINUTE MULTIMODAL REPLAY PREPARATION"
    )

    OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True
    )

    SENS_CSV_ROOT.mkdir(
        parents=True,
        exist_ok=True
    )

    print(
        "\nECG  : SensSmartTech / PhysioNet"
    )

    print(
        "PPG  : SensSmartTech / PhysioNet"
    )

    print(
        "IMU  : SisFall"
    )

    print(
        "Time : 300 seconds"
    )

    # 1
    download_senssmarttech()

    # 2
    ecg = build_ecg()

    # 3
    ppg = build_ppg()

    # 4
    imu = load_imu()

    # 5
    create_windows(
        ecg,
        ppg,
        imu
    )

    # 6
    create_manifest()

    # 7
    validate()

    banner(
        "DONE"
    )

    print(
        "\nReplay data is ready at:"
    )

    print(
        OUTPUT_ROOT
    )

    print(
        "\nGenerated:"
    )

    for file in sorted(
        OUTPUT_ROOT.iterdir()
    ):

        print(
            "  ",
            file.name
        )


if __name__ == "__main__":
    main()