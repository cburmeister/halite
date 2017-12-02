import logging

import hlt

game = hlt.Game('Settler')
logging.info('Starting my Settler bot!')

destination_by_ship_id = {}

while True:
    game_map = game.update_map()
    command_queue = []
    for ship in game_map.get_me().all_ships():
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            continue

        for planet in game_map.all_planets():
            if planet.is_owned():
                continue

            if planet in destination_by_ship_id.values():
                continue

            if ship.can_dock(planet):
                command_queue.append(ship.dock(planet))
                destination_by_ship_id.pop(ship.id, None)
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
