import json
from pyniryo import*
from time import sleep as delay

robot_ip = "172.21.182.53"  # Remplacez par l'IP de votre robot
robot = NiryoRobot(robot_ip)

#robot.pull_air_vacuum_pump()  # Activer la ventouse
#robot.push_air_vacuum_pump()  # Désactiver la ventouse

def define_tcp():
    # Définition du TCP pour la ventouse
    # Values in meters [x, y, z, roll, pitch, yaw]
    VACUUM_TCP = [0.05, 0, 0, 0, 0, 0]  # Adjust these values based on your specific vacuum tool

    # Configuration du TCP
    robot.reset_tcp()
    print('TCP Reset')
    robot.set_tcp(VACUUM_TCP)
    print('TCP Set')
    robot.enable_tcp(True)
    print('TCP Activate')

def save_all_positions(robot):
    positions = {}
    position_names = []
    
    # Get list of positions to save
    print("\n=== Position Recording Setup ===")
    print("Enter position names (one per line). Enter empty line when done.")
    while True:
        name = input("Position name (or press Enter to finish): ").strip()
        if not name:
            break
        position_names.append(name)
    
    print("\n=== Starting Position Recording ===")
    # Record each position
    for position_name in position_names:
        input(f"\nPlease move robot to position '{position_name}' then press Enter to save...")
        current_pose = robot.get_pose().to_list()
        positions[position_name] = current_pose
        print(f"Position '{position_name}' saved!")
    
    # Save all positions to file
    with open('positions.json', 'w') as f:
        json.dump(positions, f, indent=4)
    
    # Show recap
    print("\n=== Saved Positions Recap ===")
    for name, pose in positions.items():
        print(f"\nPosition: {name}")
        print(f"X: {pose[0]:.2f}, Y: {pose[1]:.2f}, Z: {pose[2]:.2f}")
        print(f"RX: {pose[3]:.2f}, RY: {pose[4]:.2f}, RZ: {pose[5]:.2f}")
    
    print("\nAll positions have been saved to positions.json")
    return positions

def move_to_saved_positions(robot):
    # Load saved positions
    with open('positions.json', 'r') as f:
        positions = json.load(f)
    
    while True:
        # Show available positions
        print("\n=== Available Positions ===")
        for i, name in enumerate(positions.keys(), 1):
            print(f"{i}. {name}")
        print("0. Exit")
        
        # Get user choice
        choice = input("\nEnter position number to move to (0 to exit): ")
        if choice == '0':
            break
            
        try:
            index = int(choice) - 1
            position_name = list(positions.keys())[index]
            target_pose = positions[position_name]
            
            # Confirm movement
            print(f"\nMoving to position: {position_name}")
            print(f"Target coordinates:")
            print(f"X: {target_pose[0]:.2f}, Y: {target_pose[1]:.2f}, Z: {target_pose[2]:.2f}")
            print(f"RX: {target_pose[3]:.2f}, RY: {target_pose[4]:.2f}, RZ: {target_pose[5]:.2f}")
            
            confirm = input("Confirm movement? (y/n): ")
            if confirm.lower() == 'y':
                # Move robot to position
                robot.move_pose(target_pose)
                print(f"Moved to position: {position_name}")
            else:
                print("Movement cancelled")
                
        except (ValueError, IndexError):
            print("Invalid selection")
            
        except Exception as e:
            print(f"Error moving robot: {e}")

color_list = [
    [15, 50, 255],
    [255, 0, 0],
    [0, 255, 0],
]

define_tcp()
robot.led_ring_alternate(color_list)
#save_all_positions(robot)
#delay(3)
move_to_saved_positions(robot)
delay(5)
robot.close_connection()

