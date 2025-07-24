def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """
    Calculate Body Mass Index (BMI).

    Args:
        weight_kg (float): Weight in kilograms (must be > 0).
        height_m (float): Height in meters (must be > 0).

    Returns:
        float: The calculated BMI, rounded to 2 decimal places.

    Raises:
        ValueError: If weight or height is not positive.
    """
    if weight_kg <= 0:
        raise ValueError("Weight must be greater than 0 kg.")
    if height_m <= 0:
        raise ValueError("Height must be greater than 0 meters.")

    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)


def get_bmi_category(bmi: float) -> str:
    """
    Determine the BMI category based on standard classification.
    Args:
        bmi (float): The Body Mass Index.
    Returns:
        str: Category string.
    """
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 24.9:
        return "Normal weight"
    elif 25 <= bmi < 29.9:
        return "Overweight"
    else:
        return "Obesity"


def main():
    print("=== BMI CALCULATOR ===")
    try:
        # Input: weight in kg, height in cm, convert to m
        weight = float(input("Enter your weight in kilograms: "))
        height_cm = float(input("Enter your height in centimeters: "))
        height_m = height_cm / 100.0

        bmi = calculate_bmi(weight, height_m)
        category = get_bmi_category(bmi)

        print(f"\nYour BMI is: {bmi}")
        print(f"Category  : {category}")

    except ValueError as ve:
        print(f"Invalid input: {ve}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
