import streamlit as st
import random
import numpy as np

BOARD_SIZE = 10
SHIP_SIZES = {
    'Carrier': 5,
    'Battleship': 4,
    'Cruiser': 3,
    'Submarine': 3,
    'Destroyer': 2
}

def empty_board():
    return [['~'] * BOARD_SIZE for _ in range(BOARD_SIZE)]

def place_ship(board, occupied, size):
    for _ in range(100):
        direction = random.choice(['H', 'V'])
        if direction == 'H':
            x = random.randint(0, BOARD_SIZE - size)
            y = random.randint(0, BOARD_SIZE - 1)
            coords = [(x + i, y) for i in range(size)]
        else:
            x = random.randint(0, BOARD_SIZE - 1)
            y = random.randint(0, BOARD_SIZE - size)
            coords = [(x, y + i) for i in range(size)]
        # Ensure all coordinates are within bounds and not occupied
        if all(0 <= cx < BOARD_SIZE and 0 <= cy < BOARD_SIZE and (cx, cy) not in occupied for cx, cy in coords):
            for cx, cy in coords:
                occupied.add((cx, cy))
            return coords
    return []

def init_computer_ships():
    occupied = set()
    ships = {}
    for name, size in SHIP_SIZES.items():
        coords = place_ship(None, occupied, size)
        ships[name] = {'coords': coords, 'hits': set()}
    return ships

def check_hit(ships, coord):
    for name, ship in ships.items():
        if coord in ship['coords']:
            ship['hits'].add(coord)
            sunk = len(ship['hits']) == len(ship['coords'])
            return 'hit', sunk, name
    return 'miss', False, None

def all_sunk(ships):
    return all(len(ship['hits']) == len(ship['coords']) for ship in ships.values())

def render_board(board, ships=None, reveal=False):
    arr = np.array(board)
    if reveal and ships:
        for ship in ships.values():
            for (x, y) in ship['coords']:
                if arr[y, x] == '~':
                    arr[y, x] = 'S'
    return arr

def main():
    st.set_page_config(page_title="Battleship", layout="centered")
    st.title("🚢 Battleship Game")
    if 'player_board' not in st.session_state:
        st.session_state.player_board = empty_board()
        st.session_state.computer_board = empty_board()
        st.session_state.player_ships = init_computer_ships()  # random for demo
        st.session_state.computer_ships = init_computer_ships()
        st.session_state.player_guesses = set()
        st.session_state.computer_guesses = set()
        st.session_state.turn = 'player'
        st.session_state.status = ''
        st.session_state.game_over = False

    st.subheader("Your Board")
    st.dataframe(render_board(st.session_state.player_board, st.session_state.player_ships, reveal=True))
    st.subheader("Opponent Board (click to attack)")
    board_arr = render_board(st.session_state.computer_board)
    cols = st.columns(BOARD_SIZE)
    for y in range(BOARD_SIZE):
        row = []
        for x in range(BOARD_SIZE):
            label = board_arr[y, x]
            key = f"btn_{x}_{y}"
            if label == '~' and not st.session_state.game_over and st.session_state.turn == 'player':
                if cols[x].button(' ', key=key, help=f"Attack {x},{y}"):
                    coord = (x, y)
                    if coord in st.session_state.player_guesses:
                        st.warning("You already attacked here.")
                    else:
                        st.session_state.player_guesses.add(coord)
                        result, sunk, ship_name = check_hit(st.session_state.computer_ships, coord)
                        st.session_state.computer_board[y][x] = 'X' if result == 'hit' else 'O'
                        if result == 'hit':
                            st.success(f"You hit a ship at {coord}!")
                            if sunk:
                                st.balloons()
                                st.success(f"You sunk the opponent's {ship_name}!")
                        else:
                            st.info(f"Miss at {coord}.")
                        if all_sunk(st.session_state.computer_ships):
                            st.session_state.status = "Congratulations! You win!"
                            st.session_state.game_over = True
                        else:
                            st.session_state.turn = 'computer'
            else:
                cols[x].write(label)
    if st.session_state.turn == 'computer' and not st.session_state.game_over:
        st.info("Computer's turn...")
        # Computer picks random
        while True:
            x = random.randint(0, BOARD_SIZE - 1)
            y = random.randint(0, BOARD_SIZE - 1)
            coord = (x, y)
            if coord not in st.session_state.computer_guesses:
                st.session_state.computer_guesses.add(coord)
                result, sunk, ship_name = check_hit(st.session_state.player_ships, coord)
                st.session_state.player_board[y][x] = 'X' if result == 'hit' else 'O'
                if result == 'hit':
                    st.warning(f"Computer hit your ship at {coord}!")
                    if sunk:
                        st.warning(f"Your {ship_name} was sunk!")
                else:
                    st.info(f"Computer missed at {coord}.")
                if all_sunk(st.session_state.player_ships):
                    st.session_state.status = "Sorry, you lost. Computer wins."
                    st.session_state.game_over = True
                else:
                    st.session_state.turn = 'player'
                break
    if st.session_state.status:
        st.header(st.session_state.status)
        if st.button("Restart Game"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()

if __name__ == "__main__":
    main()
