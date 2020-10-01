from colorama import Fore
import program_guests
import program_hosts
import data.mongo_setup as mongo_setup


def main():
    mongo_setup.global_init()

    print_header()

    try:
        while True:
            if find_user_intent() == 'book':
                program_guests.run()
            else:
                program_hosts.run()
    except KeyboardInterrupt:
        return


def print_header():


    print(Fore.WHITE + '****************  pet BnB  ****************')

    print(Fore.WHITE + '*********************************************')
    print()
    print("Welcome to pet BnB!")
    print("Why are you here?")
    print()


def find_user_intent():
    print("[g] Book a shelter for your pet")
    print("[h] Offer extra shelter space")
    print()
    choice = input("Are you a [g]uest or [h]ost? ")
    if choice == 'h':
        return 'offer'

    return 'book'


if __name__ == '__main__':
    main()
