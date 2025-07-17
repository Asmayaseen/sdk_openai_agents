def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """
    Calculate Body Mass Index (BMI).

    Args:
        weight_kg (float): Weight in kilograms. Must be > 0.
        height_m (float): Height in meters. Must be > 0.

    Returns:
        float: Calculated BMI (kg/m^2), rounded to 2 decimal places.

    Raises:
        ValueError: If weight or height is not positive.
    """
    if weight_kg <= 0:
        raise ValueError("Weight must be greater than 0 kg.")
    if height_m <= 0:
        raise ValueError("Height must be greater than 0 meters.")

    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)
