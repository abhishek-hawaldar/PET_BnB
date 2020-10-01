from typing import List, Optional

import datetime

import bson
from data.bookings import Booking
from data.shelters import Shelter
from data.owners import Owner
from data.pets import Pet


def create_account(name: str, email: str) -> Owner:
    owner = Owner()
    owner.name = name
    owner.email = email

    owner.save()

    return owner


def find_account_by_email(email: str) -> Owner:
    owner = Owner.objects(email=email).first()
    return owner


def register_shelter(active_account: Owner,
                  name, allow_dangerous, has_toys,
                  carpeted, meters, price) -> Shelter:
    shelter = Shelter()

    shelter.name = name
    shelter.square_meters = meters
    shelter.is_carpeted = carpeted
    shelter.has_toys = has_toys
    shelter.allow_dangerous_pets = allow_dangerous
    shelter.price = price

    shelter.save()

    account = find_account_by_email(active_account.email)
    account.shelter_ids.append(shelter.id)
    account.save()

    return shelter


def find_shelters_for_user(account: Owner) -> List[Shelter]:
    query = Shelter.objects(id__in=account.shelter_ids)
    shelters = list(query)

    return shelters


def add_available_date(shelter: Shelter,
                       start_date: datetime.datetime, days: int) -> Shelter:
    booking = Booking()
    booking.check_in_date = start_date
    booking.check_out_date = start_date + datetime.timedelta(days=days)

    shelter = Shelter.objects(id=shelter.id).first()
    shelter.bookings.append(booking)
    shelter.save()

    return shelter


def add_pet(account, name, length, species, is_venomous) -> Pet:
    pet = Pet()
    pet.name = name
    pet.length = length
    pet.species = species
    pet.is_venomous = is_venomous
    pet.save()

    owner = find_account_by_email(account.email)
    owner.pet_ids.append(pet.id)
    owner.save()

    return pet


def get_pets_for_user(user_id: bson.ObjectId) -> List[Pet]:
    owner = Owner.objects(id=user_id).first()
    pets = Pet.objects(id__in=owner.pet_ids).all()

    return list(pets)


def get_available_shelters(checkin: datetime.datetime,
                        checkout: datetime.datetime, pet: Pet) -> List[Shelter]:
    min_size = pet.length / 4

    query = Shelter.objects() \
        .filter(square_meters__gte=min_size) \
        .filter(bookings__check_in_date__lte=checkin) \
        .filter(bookings__check_out_date__gte=checkout)

    if pet.is_venomous:
        query = query.filter(allow_dangerous_pets=True)

    shelters = query.order_by('price', '-square_meters')

    final_shelters = []
    for c in shelters:
        for b in c.bookings:
            if b.check_in_date <= checkin and b.check_out_date >= checkout and b.guest_pet_id is None:
                final_shelters.append(c)

    return final_shelters


def book_shelter(account, pet, shelter, checkin, checkout):
    booking: Optional[Booking] = None

    for b in shelter.bookings:
        if b.check_in_date <= checkin and b.check_out_date >= checkout and b.guest_pet_id is None:
            booking = b
            break

    booking.guest_owner_id = account.id
    booking.guest_pet_id = pet.id
    booking.check_in_date = checkin
    booking.check_out_date = checkout
    booking.booked_date = datetime.datetime.now()

    shelter.save()


def get_bookings_for_user(email: str) -> List[Booking]:
    account = find_account_by_email(email)

    booked_shelters = Shelter.objects() \
        .filter(bookings__guest_owner_id=account.id) \
        .only('bookings', 'name')

    def map_shelter_to_booking(shelter, booking):
        booking.shelter = shelter
        return booking

    bookings = [
        map_shelter_to_booking(shelter, booking)
        for shelter in booked_shelters
        for booking in shelter.bookings
        if booking.guest_owner_id == account.id
    ]

    return bookings
