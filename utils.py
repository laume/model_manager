import sys

def input_number(message):
    while True:
        try:
            user_input = int(input(message))
            if user_input <= 0:
                print('Exiting without any changes!')
                sys.exit()
        except ValueError:
            print('Not an integer! Try again.')
            continue
        else:
            return user_input

# print(input_number('input integer: \n'))


def confirm_input(message):
    yes = {'yes', 'y', 'ye', ''}
    no = {'no', 'n'}
    while True:
        choice = input(message).lower()
        if choice in yes:
            return True
        elif choice in no:
            return False
        else:
            print("Please respond with 'yes' or 'no'")
            continue

# confirm_input('confirm')

def simple_input(message, to_expect):
    while True:
        choice = input(message).lower()
        if choice in to_expect:
            return choice
        elif choice == 'exit':
            print('Exiting without changes..')
            sys.exit()
        else:
            print("Please provide needed data, enter 'exit' to cancel")
            continue

# simple_input('test', {'d'})
