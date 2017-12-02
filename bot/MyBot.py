import logging

import hlt

game = hlt.Game('Settler')
logging.info('Starting my Settler bot!')

destination_by_ship_id = {}


while True:
    game_map = game.update_map()
    command_queue = []
    for ship in game_map.get_me().all_ships():

        # Skip this ship if it's not undocked
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            continue

        # Get all of the planets and sort them by distance from the ship
        planets = game_map.all_planets()
        planets = sorted(
            planets,
            key=lambda x: x.calculate_distance_between(ship)
        )

        # Iterate over the planets with the goal of sending a ship to one
        for planet in planets:

            # Skip this planet if it's already owned
            if planet.is_owned():
                continue

            # Skip this planet if there's already a ship heading its way
            if planet in destination_by_ship_id.values():
                continue

            # Dock the ship at the planet if possible
            if ship.can_dock(planet):
                command_queue.append(ship.dock(planet))
                destination_by_ship_id.pop(ship.id, None)

            # Otherwise head towards it
            else:
                navigate_command = ship.navigate(
                    ship.closest_point_to(planet),
                    game_map,
                    speed=int(hlt.constants.MAX_SPEED),
                    ignore_ships=True
                )
                if navigate_command:
                    command_queue.append(navigate_command)
                    destination_by_ship_id[ship.id] = planet

            break

    game.send_command_queue(command_queue)
