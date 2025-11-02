

import csv
import os


class RoomNotFoundError(Exception):
    """Raised when the room id is not found."""
    pass

class TimeslotAlreadyBookedError(Exception):
    """Raised when trying to book an hour that's already booked."""
    pass

class RoomAlreadyExistsError(Exception):
    """Raised when trying to create a room with an id that already exists."""
    pass


class Room:

    def __init__(self, room_no: str, building: str, capacity: int, booked_hours=None):
        self.room_no = room_no
        self.building = building
        self.capacity = int(capacity)
        self.booked_hours = [] if booked_hours is None else list(map(int, booked_hours))

    def is_free_at(self, hour: int) -> bool:

        return hour not in self.booked_hours

    def book_hour(self, hour: int):
  
        if not self.is_free_at(hour):
            raise TimeslotAlreadyBookedError(f"Room {self.room_no} is already booked at hour {hour}")
        self.booked_hours.append(hour)

        self.booked_hours.sort()

    def booked_hours_str(self) -> str:

        return ";".join(str(h) for h in self.booked_hours)

    def __str__(self):
        return f"Room {self.room_no} | Building: {self.building} | Capacity: {self.capacity} | Booked: {self.booked_hours_str()}"

class BookingSystem:

    CSV_FILE = "bookings_final_state.csv"

    def __init__(self):

        self.rooms = {}

        self.load_from_csv()


    def add_room(self, room_no: str, building: str, capacity: int):

        if room_no in self.rooms:
            raise RoomAlreadyExistsError(f"Room {room_no} already exists.")
        room = Room(room_no, building, capacity)
        self.rooms[room_no] = room

    def get_room(self, room_no: str) -> Room:

        if room_no not in self.rooms:
            raise RoomNotFoundError(f"No room with id {room_no} found.")
        return self.rooms[room_no]


    def book_room(self, room_no: str, hour: int):

        room = self.get_room(room_no)
        if hour < 0 or hour > 23:
            raise ValueError("Hour must be between 0 and 23.")
        room.book_hour(hour)


    def find_rooms(self, building=None, min_capacity=None, free_at_hour=None):



        results = list(self.rooms.values())
        if building is not None:
            results = [r for r in results if r.building.lower() == building.lower()]
        if min_capacity is not None:
            results = [r for r in results if r.capacity >= int(min_capacity)]
        if free_at_hour is not None:
            results = [r for r in results if r.is_free_at(int(free_at_hour))]
        return results


    def load_from_csv(self):

        if not os.path.exists(self.CSV_FILE):

            return
        try:
            with open(self.CSV_FILE, newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    room_no = row.get('room_no', '').strip()
                    building = row.get('building', '').strip()
                    capacity = row.get('capacity', '0').strip()
                    booked_hours_str = row.get('booked_hours', '').strip()
                    if booked_hours_str == "":
                        booked_hours = []
                    else:

                        booked_hours = [int(x) for x in booked_hours_str.split(';') if x.strip() != '']
                    if room_no == "":

                        continue

                    room = Room(room_no, building, capacity, booked_hours)
                    self.rooms[room_no] = room
        except Exception as e:
            print("Warning: could not load CSV file. Starting with empty data.")
            print("Error:", e)

    def save_to_csv(self):

        with open(self.CSV_FILE, 'w', newline='') as f:
            fieldnames = ['room_no', 'building', 'capacity', 'booked_hours']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for room in self.rooms.values():
                writer.writerow({
                    'room_no': room.room_no,
                    'building': room.building,
                    'capacity': room.capacity,
                    'booked_hours': room.booked_hours_str()
                })



def print_menu():
    print('\n----- Classroom Booking -----')
    print('1. Create a new room')
    print('2. Book a room for one hour')
    print('3. Find / filter rooms')
    print('4. View room bookings')
    print('5. List all rooms')
    print('6. Exit and save')


def ask(prompt: str) -> str:

    return input(prompt).strip()



system = BookingSystem()
print("Hello! This is a simple room booking program.")
print("If a saved file 'bookings_final_state.csv' exists, it was loaded already.")

while True:
    print_menu()
    choice = ask('Choose a number: ')
    if choice == '1':

        try:
            room_no = ask('Enter room id (like NAB101): ')
            building = ask('Enter building name (like NAB): ')
            capacity_str = ask('Enter capacity (a number): ')
            if not capacity_str.isdigit():
                print('Capacity must be a whole number. Try again.')
                continue
            capacity = int(capacity_str)
            system.add_room(room_no, building, capacity)
            print('Room added:', room_no)
        except RoomAlreadyExistsError as e:
            print('Oops! That room id is already used. Try a different id.')
        except Exception as e:
            print('Something went wrong while adding room:', e)

    elif choice == '2':

        try:
            room_no = ask('Enter room id to book: ')
            hour_str = ask('Enter hour (0-23): ')
            if not hour_str.isdigit():
                print('Hour must be a number between 0 and 23.')
                continue
            hour = int(hour_str)
            system.book_room(room_no, hour)
            print(f'Booked room {room_no} at hour {hour} ')
        except RoomNotFoundError:
            print('The room doesn\'t exist. Check the room id and try again.')
        except TimeslotAlreadyBookedError:
            print('That hour is already booked for this room. Pick another hour.')
        except ValueError as e:
            print('Bad ask:', e)
        except Exception as e:
            print('Could not book the room:', e)

    elif choice == '3':

        print('\nType filters. Leave blank to skip a filter.')
        building = ask('Filter by building (exact name): ')
        min_capacity_str = ask('Filter by minimum capacity: ')
        free_hour_str = ask('Filter by free at hour (0-23): ')

        if building == '':
            building = None
        if min_capacity_str == '':
            min_capacity = None
        else:
            if not min_capacity_str.isdigit():
                print('Capacity must be a number. Search cancelled.')
                continue
            min_capacity = int(min_capacity_str)
        if free_hour_str == '':
            free_hour = None
        else:
            if not free_hour_str.isdigit():
                print('Hour must be a number. Search cancelled.')
                continue
            free_hour = int(free_hour_str)
            if free_hour < 0 or free_hour > 23:
                print('Hour must be 0..23. Search cancelled.')
                continue

        results = system.find_rooms(building=building, min_capacity=min_capacity, free_at_hour=free_hour)
        print(f"\nFound {len(results)} room(s):")
        for r in results:
            print(r)

    elif choice == '4':

        try:
            room_no = ask('Enter room id to view: ')
            room = system.get_room(room_no)
            print('\n')
            print('Room details:')
            print('Room id:', room.room_no)
            print('Building:', room.building)
            print('Capacity:', room.capacity)
            if room.booked_hours:
                print('Booked hours (sorted):', ', '.join(str(h) for h in room.booked_hours))
            else:
                print('No bookings yet for this room.')
        except RoomNotFoundError:
            print('Sorry, that room id does not exist.')

    elif choice == '5':

        if not system.rooms:
            print('No rooms in the system yet.')
        else:
            print('\nAll rooms:')
            for r in system.rooms.values():
                print(r)

    elif choice == '6':

        try:
            system.save_to_csv()
            print("Saved data to bookings_final_state.csv. Goodbye!")
        except Exception as e:
            print('Could not save data. Error:', e)
        break

    else:
        print('Please type a number from 1 to 6.')