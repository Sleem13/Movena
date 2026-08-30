# data/mhealth_mapper.py
"""
Maps mHealth dataset activity IDs to RehabRL prescription parameters.
Activity IDs from mHealth dataset:
1: Standing still        -> very low intensity
2: Sitting and relaxing  -> very low intensity
3: Lying down            -> very low intensity
4: Walking               -> low intensity
5: Climbing stairs       -> medium intensity
6: Waist bends forward   -> medium intensity (ROM focus)
7: Frontal arm elevation -> medium intensity (strength focus)
8: Knees bending         -> medium-high intensity
9: Cycling               -> medium-high intensity (cardio)
10: Jogging              -> high intensity
11: Running              -> very high intensity
12: Jumping              -> very high intensity (explosive)
"""


def mhealth_activity_to_prescription_params(activity_id: int) -> dict:
    """
    Convert mHealth activity ID to prescription parameters compatible with
    your exercise database.

    Returns:
        dict with keys: intensity, rom_benefit, strength_benefit, cardio_benefit, fatigue
    """
    mapping = {
        1: {
            "intensity": 0.1,
            "rom_benefit": 0.05,
            "strength_benefit": 0.05,
            "cardio_benefit": 0.0,
            "fatigue": 0.05,
        },
        2: {
            "intensity": 0.1,
            "rom_benefit": 0.05,
            "strength_benefit": 0.05,
            "cardio_benefit": 0.0,
            "fatigue": 0.05,
        },
        3: {
            "intensity": 0.1,
            "rom_benefit": 0.05,
            "strength_benefit": 0.05,
            "cardio_benefit": 0.0,
            "fatigue": 0.05,
        },
        4: {
            "intensity": 0.3,
            "rom_benefit": 0.15,
            "strength_benefit": 0.10,
            "cardio_benefit": 0.2,
            "fatigue": 0.15,
        },
        5: {
            "intensity": 0.5,
            "rom_benefit": 0.20,
            "strength_benefit": 0.20,
            "cardio_benefit": 0.3,
            "fatigue": 0.25,
        },
        6: {
            "intensity": 0.5,
            "rom_benefit": 0.30,
            "strength_benefit": 0.15,
            "cardio_benefit": 0.1,
            "fatigue": 0.20,
        },
        7: {
            "intensity": 0.5,
            "rom_benefit": 0.25,
            "strength_benefit": 0.25,
            "cardio_benefit": 0.1,
            "fatigue": 0.20,
        },
        8: {
            "intensity": 0.7,
            "rom_benefit": 0.25,
            "strength_benefit": 0.30,
            "cardio_benefit": 0.2,
            "fatigue": 0.30,
        },
        9: {
            "intensity": 0.7,
            "rom_benefit": 0.10,
            "strength_benefit": 0.15,
            "cardio_benefit": 0.5,
            "fatigue": 0.30,
        },
        10: {
            "intensity": 0.9,
            "rom_benefit": 0.10,
            "strength_benefit": 0.20,
            "cardio_benefit": 0.6,
            "fatigue": 0.45,
        },
        11: {
            "intensity": 1.0,
            "rom_benefit": 0.10,
            "strength_benefit": 0.25,
            "cardio_benefit": 0.7,
            "fatigue": 0.50,
        },
        12: {
            "intensity": 1.0,
            "rom_benefit": 0.05,
            "strength_benefit": 0.30,
            "cardio_benefit": 0.4,
            "fatigue": 0.55,
        },
    }
    return mapping.get(activity_id, mapping[4])  # default to walking


def get_prescription_for_mhealth_activity(activity_id: int):
    """
    Find the closest matching prescription in your exercise database.
    Returns prescription index (0-29) and the Prescription object.
    """
    from rehabrl.data.exercise_database import (
        get_prescription_by_intensity_and_focus,
    )

    params = mhealth_activity_to_prescription_params(activity_id)
    # Determine focus: which benefit is highest?
    benefits = {k: v for k, v in params.items() if k.endswith("_benefit")}
    focus = max(benefits, key=benefits.get).replace("_benefit", "")
    return get_prescription_by_intensity_and_focus(params["intensity"], focus)
