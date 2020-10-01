import datetime
from colorama import Fore
from dateutil import parser

from infrastructure.switchlang import switch
import infrastructure.state as state
import services.data_service as svc


def run():
    print(' ****************** Welcome host **************** ')
    print()

    show_commands()

    while True:
        action = get_action()

        with switch(action) as s:
            s.case('c', create_account)
            s.case('a', create_account)
            s.case('l', log_into_account)
            s.case('y', list_shelters)
            s.case('r', register_shelter)
            s.case('u', update_availability)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')
            s.case(['x', 'bye', 'exit', 'exit()'], exit_app)
            s.case('?', show_commands)
            s.case('', lambda: None)
            s.default(unknown_command)

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an [a]ccount')
    print('[L]ogin to your account')
    print('List [y]our shelters')
    print('[R]egister a shelter')
    print('[U]pdate shelter availability')
    print('[V]iew your bookings')
    print('Change [M]ode (guest or host)')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def create_account():
    print(' ****************** REGISTER **************** ')

    name = input('What is your name? ')
    email = input('What is your email? ').strip().lower()

    old_account = svc.find_account_by_email(email)
    if old_account:
        error_msg(f"ERROR: Account with email {email} already exists.")
        return

    state.active_account = svc.create_account(name, email)
    success_msg(f"Created new account with id {state.active_account.id}.")


def log_into_account():
    print(' ****************** LOGIN **************** ')

    email = input('What is your email? ').strip().lower()
    account = svc.find_account_by_email(email)

    if not account:
        error_msg(f'Could not find account with email {email}.')
        return

    state.active_account = account
    success_msg('Logged in successfully.')


def register_shelter():
    print(' ****************** REGISTER shelter **************** ')

    if not state.active_account:
        error_msg('You must login first to register a shelter.')
        return

    meters = input('How many square meters is the shelter? ')
    if not meters:
        error_msg('Cancelled')
        return

    meters = float(meters)
    carpeted = input("Is it carpeted [y, n]? ").lower().startswith('y')
    has_toys = input("Have pet toys [y, n]? ").lower().startswith('y')
    allow_dangerous = input("Can you host violent pets [y, n]? ").lower().startswith('y')
    name = input("Give your shelter a name: ")
    price = float(input("How much are you charging?  "))

    shelter = svc.register_shelter(
        state.active_account, name,
        allow_dangerous, has_toys, carpeted, meters, price
    )

    state.reload_account()
    success_msg(f'Register new shelter with id {shelter.id}.')


def list_shelters(suppress_header=False):
    if not suppress_header:
        print(' ******************     Your shelters     **************** ')

    if not state.active_account:
        error_msg('You must login first to register a shelter.')
        return

    shelters = svc.find_shelters_for_user(state.active_account)
    print(f"You have {len(shelters)} shelters.")
    for idx, c in enumerate(shelters):
        print(f' {idx + 1}. {c.name} is {c.square_meters} meters.')
        for b in c.bookings:
            print('      * Booking: {}, {} days, booked? {}'.format(
                b.check_in_date,
                (b.check_out_date - b.check_in_date).days,
                'YES' if b.booked_date is not None else 'no'
            ))


def update_availability():
    print(' ****************** Add available date **************** ')

    if not state.active_account:
        error_msg("You must log in first to register a shelter")
        return

    list_shelters(suppress_header=True)

    shelter_number = input("Enter shelter number: ")
    if not shelter_number.strip():
        error_msg('Cancelled')
        print()
        return

    shelter_number = int(shelter_number)

    shelters = svc.find_shelters_for_user(state.active_account)
    selected_shelter = shelters[shelter_number - 1]

    success_msg("Selected shelter {}".format(selected_shelter.name))

    start_date = parser.parse(
        input("Enter available date [yyyy-mm-dd]: ")
    )
    days = int(input("How many days is this block of time? "))

    svc.add_available_date(
        selected_shelter,
        start_date,
        days
    )

    success_msg(f'Date added to shelter {selected_shelter.name}.')


def view_bookings():
    print(' ****************** Your bookings **************** ')

    if not state.active_account:
        error_msg("You must log in first to register a shelter")
        return

    shelters = svc.find_shelters_for_user(state.active_account)

    bookings = [
        (c, b)
        for c in shelters
        for b in c.bookings
        if b.booked_date is not None
    ]

    print("You have {} bookings.".format(len(bookings)))
    for c, b in bookings:
        print(' * shelter: {}, booked date: {}, from {} for {} days.'.format(
            c.name,
            datetime.date(b.booked_date.year, b.booked_date.month, b.booked_date.day),
            datetime.date(b.check_in_date.year, b.check_in_date.month, b.check_in_date.day),
            b.duration_in_days
        ))


def exit_app():
    print()
    print('bye')
    raise KeyboardInterrupt()


def get_action():
    text = '> '
    if state.active_account:
        text = f'{state.active_account.name}> '

    action = input(Fore.YELLOW + text + Fore.WHITE)
    return action.strip().lower()


def unknown_command():
    print("Sorry we didn't understand that command.")


def success_msg(text):
    print(Fore.LIGHTGREEN_EX + text + Fore.WHITE)


def error_msg(text):
    print(Fore.LIGHTRED_EX + text + Fore.WHITE)
