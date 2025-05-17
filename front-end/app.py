import requests

"http://localhost:5000/api/workouts"

def display_menu():
    
    print("\n" + "=" * 50)
    print("WORKOUT LOG SYSTEM".center(50))
    print("=" * 50)
    print("1. List All Workouts")
    print("2. View Workout Details")
    print("3. Add New Workout")
    print("4. View Progress Charts")
    print("5. Update Workout")
    print("6. Delete Workout")
    print("7. Exit")
    print("=" * 50)

def list_workouts():
    try:
        response = requests.get(f"/workouts")
        if response.status_code == 200:
            workouts = response.json()
            if not workouts:
                print("\nNo workouts found!")
                return

            print("\n" + "-" * 70)
            
            print(f"{'ID':<5}{'Date':<12}{'Exercise':<20}{'Sets':<6}{'Reps':<6}{'Weight':<10}")
            print("-" * 70)
            for w in workouts:
                print(f"{w['id']:<5}{w['date']:<12}{w['exercise']:<20}{w['sets'] or '-':<6}{w['reps'] or '-':<6}{w['weight'] or '-':<10}")
            print("-" * 70)
        else:
            print(f"\nError fetching workouts: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"\nConnection error: {e}")

def view_workout():
    workout_id = input("\nEnter workout ID: ")
    try:
        response = requests.get(f"/workouts/{workout_id}")
        if response.status_code == 200:
            w = response.json()
            print("\n" + "-" * 50)
            print("WORKOUT DETAILS".center(50))
            print("-" * 50)
            print(f"ID: {w['id']}")
            print(f"Date: {w['date']}")
            print(f"Exercise: {w['exercise']}")
            print(f"Sets: {w.get('sets', '-')}")
            print(f"Reps: {w.get('reps', '-')}")
            print(f"Weight: {w.get('weight', '-')} kg")
            print("-" * 50)
        elif response.status_code == 404:
            print("\nWorkout not found!")
        else:
            print(f"\nError: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"\nConnection error: {e}")

def add_workout():
    print("\nEnter workout details:")
    date = input("Date (YYYY-MM-DD): ")
    exercise = input("Exercise: ")
    sets = input("Sets: ")
    reps = input("Reps: ")
    weight = input("Weight (kg): ")

    if not date or not exercise:
        print("\nDate and exercise are required!")
        return

    data = {
        "date": date,
        "exercise": exercise,
        "sets": int(sets) if sets else None,
        "reps": int(reps) if reps else None,
        "weight": float(weight) if weight else None
    }

    try:
        response = requests.post(f"/workouts", json=data)
        if response.status_code == 201:
            print("\nWorkout added successfully!")
            print(f"New Workout ID: {response.json()['id']}")
        else:
            print(f"\nError: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"\nConnection error: {e}")

def view_progress_charts():
    try:
        response = requests.get(f"/progress")
        if response.status_code == 200:
            data = response.json()
            if not data:
                print("\nNo progress data available.")
                return

            print("\n" + "-" * 50)
            print("WORKOUT PROGRESS".center(50))
            print("-" * 50)

            progress = {}
            for entry in data:
                date = entry['date']
                total = entry['total_volume']
                progress[date] = progress.get(date, 0) + float(total)

            print(f"{'Date':<15}{'Total Volume (kg)':<20}")
            print("-" * 35)
            for date, total in progress.items():
                print(f"{date:<15}{total:<20.2f}")
            print("-" * 35)
        else:
            print(f"\nError fetching progress: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"\nConnection error: {e}")


def update_workout():
    workout_id = input("\nEnter workout ID to update: ")
    try:
        response = requests.get(f"/workouts/{workout_id}")
        if response.status_code != 200:
            print("\nWorkout not found!")
            return

        current = response.json()
        print("\nCurrent workout details:")
        print(f"1. Date: {current['date']}")
        print(f"2. Exercise: {current['exercise']}")
        print(f"3. Sets: {current.get('sets', '-')}")
        print(f"4. Reps: {current.get('reps', '-')}")
        print(f"5. Weight: {current.get('weight', '-')}")

        print("\nEnter new values (leave blank to keep current):")
        updates = {}

        date = input("New date (YYYY-MM-DD): ")
        if date: updates["date"] = date

        exercise = input("New exercise: ")
        if exercise: updates["exercise"] = exercise

        sets = input("New sets: ")
        if sets:
            try: updates["sets"] = int(sets)
            except: print("Sets must be an integer."); return

        reps = input("New reps: ")
        if reps:
            try: updates["reps"] = int(reps)
            except: print("Reps must be an integer."); return

        weight = input("New weight (kg): ")
        if weight:
            try: updates["weight"] = float(weight)
            except: print("Weight must be a number."); return

        if not updates:
            print("\nNo changes made.")
            return

        response = requests.put(f"/workouts/{workout_id}", json=updates)
        if response.status_code == 200:
            print("\nWorkout updated successfully!")
        else:
            print(f"\nError: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"\nConnection error: {e}")

def delete_workout():
    workout_id = input("\nEnter workout ID to delete: ")
    confirm = input(f"Are you sure you want to delete workout {workout_id}? (y/n): ")
    if confirm.lower() != 'y':
        print("Deletion cancelled.")
        return

    try:
        response = requests.delete(f"/workouts/{workout_id}")
        if response.status_code == 200:
            print("\nWorkout deleted successfully!")
        else:
            print(f"\nError deleting workout: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"\nConnection error: {e}")

def main():
    while True:
        display_menu()
        choice = input("\nEnter your choice (1-7): ")
        if choice == '1':
            list_workouts()
        elif choice == '2':
            view_workout()
        elif choice == '3':
            add_workout()
        elif choice == '4':
            view_progress_charts()
        elif choice == '5':
            update_workout()
        elif choice == '6':
            delete_workout()
        elif choice == '7':
            print("\nExiting program. Goodbye!")
            break
        else:
            print("\nInvalid choice. Try again.")
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
