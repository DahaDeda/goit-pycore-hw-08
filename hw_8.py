import re
import datetime as dt
from datetime import datetime as dtdt
from collections import UserDict
import pickle

class Field:
    pass

class Name(Field):
    def __init__(self, name):
        self.name = name

class Phone(Field):
    def __init__(self, number):
        if not re.match(r'^\d{10}$', number):
            raise ValueError("Invalid phone number format. Must be 10 digits.")
        self.number = number

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.name] = record
        return "Record added successfully."

    def find(self, name):
        return self.data.get(name)

    def find_phone(self, phone_number):
        for record in self.data.values():
            phone = record.find_phone(phone_number)
            if phone:
                return phone
        return None

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return "Record deleted successfully."
        else:
            return "Record not found."

    def show_all_records(self):
        for record in self.data.values():
            print(f"Name: {record.name.name}")
            for phone in record.phones:
                print(f"Phone: {phone.number}")
            print("------")

    def get_upcoming_birthdays(self):
        tdate = dtdt.today().date()
        tdate.toordinal()
        bdays = []
        for record in self.data.values():
            if record.birthday:
                bdate = record.birthday.value
                bdate = dt.date(tdate.year, bdate.month, bdate.day)
                week_day = bdate.isoweekday()
                bdo = bdate.toordinal()
                days_between = bdo - tdate.toordinal()
                if 0 <= days_between <= 7:
                    if week_day < 7:
                        bdays.append({'name': record.name.name, 'birthday': bdate.isoformat().replace('-', '.')[:10]})
        return bdays

class Record:
    def __init__(self, name):
        self.name = name
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(phone)
        return "Phone added successfully."

    def remove_phone(self, phone_number):
        for phone in self.phones:
            if phone.number == phone_number:
                self.phones.remove(phone)
                return "Phone removed successfully."
        return "Phone not found."

    def edit_phone(self, new_phone):
        for phone in self.phones:
            phone.number = new_phone
        return "Phone edited successfully."

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.number == phone_number:
                return phone
        return None
    
    def add_birthday(self, birthday):
        if not self.birthday:
            self.birthday = birthday
            return "Birthday added successfully."
        else:
            return "Record already has a birthday."
    
class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = dt.datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Check your name, it isn't in the database, try again"
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Check the correct input"
    return wrapper  

com_exit = ("exit" or "close")

@input_error
def parse_input(our_command):
    cmd, *args = our_command.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_record(args, address_book):
    name, *phones = args
    name_obj = Name(name)
    record = Record(name_obj)
    for phone in phones:
        record.add_phone(Phone(phone))
    address_book.add_record(record)
    return "Record added"

@input_error
def find_record(args, address_book):
    record = address_book.find(args[0])
    if record:
        return f"Record found: {record.name.name} - {', '.join([phone.number for phone in record.phones])}"
    else:
        return "Record not found"

@input_error
def delete_record(args, address_book):
    address_book.delete(args[0])
    return "Record deleted"

@input_error
def edit_phone_number(args, address_book):
    if len(args) != 2:
        return "Невірна кількість аргументів для редагування номера телефону."

    name, new_phone = args
    record = address_book.find(name)
    if record:
        result = record.edit_phone(new_phone)
        return result
    else:
        return "Запис не знайдено."

@input_error
def show_all_records(address_book):
    address_book.show_all_records()

@input_error
def add_birthday(args, address_book):
    name, birthday_str = args
    record = address_book.find(name)
    if record:
        result = record.add_birthday(Birthday(birthday_str))
        return result
    else:
        return "Record not found."
    
@input_error
def show_birthday(args, address_book):
    name = args[0]
    record = address_book.find(name)
    if record and record.birthday:
        return f"{record.name.name}'s birthday: {record.birthday.value.strftime('%d.%m.%Y')}"
    elif record:
        return f"{record.name.name} doesn't have a birthday."
    else:
        return "Record not found."   
    
@input_error
def birthdays(args, address_book):
    upcoming_birthdays = address_book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "Upcoming birthdays:\n" + "\n".join([f"{bd['name']}'s birthday on {bd['birthday']}" for bd in upcoming_birthdays])
    else:
        return "No upcoming birthdays." 
    
@input_error
def main():
    address_book = load_data()
    print("Hello, it's your personal Helper")
    while True:                
        our_command = input("Enter a command: ").strip().lower()
        command, *args = parse_input(our_command)
        if command == com_exit:
            save_data(address_book)
            print("Bye")
            break
        elif command == "hello":
            print("How can I help you: ")
        elif command == "add":
            print(add_record(args, address_book))
        elif command == "find":
            print(find_record(args, address_book))
        elif command == "delete":
            print(delete_record(args, address_book))
        elif command == "all":
            print(show_all_records(address_book))
        elif command == "edit":
            print(edit_phone_number(args, address_book))
        elif command == "add-birthday":
            print(add_birthday(args, address_book))
        elif command == "show-birthday":
            print(show_birthday(args, address_book))
        elif command == "birthdays":
            print(birthdays(args, address_book))

if __name__ == "__main__":
    main()