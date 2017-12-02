from collections import defaultdict
import logging

import hlt

game = hlt.Game('Settler')
logging.info('Starting my Settler bot!')

destination_by_ship_id = {}


def get_command_for_undocked_ship(game_map, ship):
    """Return the best command for the given undocked ship."""

    # Get all of the planets and sort them by distance from the ship
    planets = game_map.all_planets()
    planets = sorted(
        planets,
        key=lambda x: x.calculate_distance_between(ship)
    )

    # First try to dock to any unowned planets
    for planet in [x for x in planets if not x.is_owned()]:

        # Dock the ship at the planet if possible
        if ship.can_dock(planet):
            command = ship.dock(planet)
            destination_by_ship_id.pop(ship.id, None)
            return command

    # Next try to navigate to any unowned planets
    for planet in [x for x in planets if not x.is_owned()]:

        # Skip this planet if there's already a ship heading its way
        if planet in destination_by_ship_id.values():
            continue

        # Otherwise head towards it
        command = ship.navigate(
            ship.closest_point_to(planet),
            game_map,
            speed=int(hlt.constants.MAX_SPEED),
            ignore_ships=True
        )
        if command:
            destination_by_ship_id[ship.id] = planet
            return command


while True:
    game_map = game.update_map()
    command_queue = []

    # Organize ships by docking status
    ships_by_docking_status = defaultdict(list)
    for ship in game_map.get_me().all_ships():
        ships_by_docking_status[ship.docking_status].append(ship)

    # Loop over every undocked ship and try to give them something to do
    for ship in ships_by_docking_status.get(ship.DockingStatus.UNDOCKED, []):
        command = get_command_for_undocked_ship(game_map, ship)
        if command:
            command_queue.append(command)

    game.send_command_queue(command_queue)
