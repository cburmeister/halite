import logging
import signal

import hlt

game = hlt.Game('Settler')
logging.info('Starting my Settler bot!')

destination_by_ship_id = {}


def get_undocked_ships(ships):
    """Returns an iterable of undocked ships from the given list of ships."""
    for ship in ships:
        if ship.docking_status == hlt.entity.Ship.DockingStatus.UNDOCKED:
            yield ship


def get_owned_planets(planets):
    """Returns an iterable of owned planets from the given planets."""
    for planet in planets:
        if planet.is_owned():
            yield planet


def get_unowned_planets(planets):
    """Returns an iterable of unowned planets from the given planets."""
    for planet in planets:
        if not planet.is_owned():
            yield planet


def get_command_for_undocked_ship(game_map, ship):
    """Return the best command for the given undocked ship.

    This function commands a ship to do one of the following in order:

    1. Dock to the closest unowned planet
    2. Navigate to the closest unowned planet
    3. Dock to the closest owned planet
    4. Swarm an enemy owned planet
    """

    # Get all of the planets and sort them by distance from the ship
    planets = game_map.all_planets()
    planets.sort(key=lambda x: x.calculate_distance_between(ship))

    # First try to dock to any unowned planets
    for planet in get_unowned_planets(planets):

        # Dock the ship at the planet if possible
        if ship.can_dock(planet):
            command = ship.dock(planet)
            destination_by_ship_id.pop(ship.id, None)
            return command

    # Next try to navigate to any unowned planets
    for planet in get_unowned_planets(planets):

        # Skip this planet if there's already a ship heading its way
        if planet in destination_by_ship_id.values():
            continue

        # Otherwise head towards it
        command = ship.navigate(
            ship.closest_point_to(planet),
            game_map,
            speed=int(hlt.constants.MAX_SPEED)
        )
        if command:
            destination_by_ship_id[ship.id] = planet
            return command

    # Next ensure we've filled every docking spot on planets we own
    for planet in get_owned_planets(planets):

        # Skip this planet if it isn't ours
        if planet.owner.id != game_map.my_id:
            continue

        # If there are available docking spots
        docked_ships = planet.all_docked_ships()
        docking_spots = planet.num_docking_spots
        if len(docked_ships) < docking_spots:

            # Dock the ship at the planet if possible
            if ship.can_dock(planet):
                command = ship.dock(planet)
                destination_by_ship_id.pop(ship.id, None)
                return command

            # Skip this planet if there's already a ship heading its way
            if planet in destination_by_ship_id.values():
                continue

            # Head towards it
            command = ship.navigate(
                ship.closest_point_to(planet),
                game_map,
                speed=int(hlt.constants.MAX_SPEED),
                ignore_ships=True
            )
            if command:
                destination_by_ship_id[ship.id] = planet
                return command

    # Next try to swarm an enemy owned planet
    for planet in get_owned_planets(planets):

        # Skip this planet if it's ours
        if planet.owner.id == game_map.my_id:
            continue

        # Head towards it
        docked_enemy_ships = planet.all_docked_ships()
        for enemy_ship in docked_enemy_ships:
            command = ship.navigate(
                ship.closest_point_to(enemy_ship),
                game_map,
                speed=int(hlt.constants.MAX_SPEED),
                ignore_ships=True
            )
            if command:
                return command


def _handler_timeout(signum, frame):
    raise TimeoutError


while True:
    command_queue = []
    game_map = game.update_map()
    ships = game_map.get_me().all_ships()

    # Prevent a timeout from happening after 1.8 seconds
    signal.signal(signal.SIGALRM, _handler_timeout)
    signal.setitimer(signal.ITIMER_REAL, 1.8)
    try:

        # Loop over every undocked ship and try to give them something to do
        for ship in get_undocked_ships(ships):
            command = get_command_for_undocked_ship(game_map, ship)
            if command:
                command_queue.append(command)

    except TimeoutError:
        pass

    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)

    game.send_command_queue(command_queue)
