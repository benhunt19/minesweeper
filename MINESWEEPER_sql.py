import random
import numpy as np
import time
import psycopg2
import datetime

# CONSTS 
flag = 'f'
guess = 'g'

def innit_leaderboard(username) -> None:
    """
    Description:
    Log into database and get the top 5 scores on the leaderboard.
    Creates globals 'con' and 'cur' which can be used to execute
    queries on the database.
    """
    global con
    con = psycopg2.connect(
        user='postgres',
        password='password',
        host='**removed**',
        port='5432',
        database='postgres'
    )
    global cur
    cur = con.cursor()
    cur.execute(f"SELECT * FROM minesweeper m ORDER BY m.score ASC LIMIT 5")
    leaderboard = np.array(cur.fetchall())
    print(f"{'Name':<15}{'Score':<10}{'Date':<25}{'Size':<10}{'Mines':<10}")
    for row in leaderboard:
        print(f"{row[0]:<15}{row[1]:<10}{row[2]:<25}{row[3]:<10}{row[4]:<10}")
    for i in range(len(leaderboard)):
        if leaderboard[i][0] == username:
            cur.execute(
                f"""SELECT * FROM minesweeper m WHERE m.name='{username}' ORDER BY SCORE ASC""")
            print(f'\n{username}, your highscore is: {cur.fetchall()[0][1]}\n')
            break

def create_row(data_list) -> str:
    """
    Description:
    Insert new score into the database
    """
    value_string = ", ".join(map(str, data_list))
    return f"INSERT INTO minesweeper VALUES ({value_string})"

def minesweeper(db=True):
    """
    Description:
    Main executable running function, the process is the following:
    1. Initialise the database and get current highscores.
    2. Initialise the various display and non display data grids.
    3. Start the main running loop, prompting the user to enter
       their coordinates and guess type (f = 'flag', g = 'guess').
    4. Based on their guess, update the grid, displaying the current
       guesses and visible points. The regular rules of minesweeper
       will apply.
    5. Once the user has successfully (or unsuccessfully) played
       finished playing the game, update the database with new 
       entry and display it to the user.
    
    """
    # Take the users username
    username = input('Enter your name: ')

    # Initialize the leaderboard
    if db:
        innit_leaderboard(username)

    # Initialize the size of the grid
    size = int(input('What size grid would you like ? (n x n): '))
    mines = int(input('How many mines would you like?: '))

    # Countdown, start game and timer
    print('Game starting in...')
    for i in range(3):
        print(3 - i)
        time.sleep(1)
    TIME = time.time()
    
    # Initilize the main grid and the minemap with randomly placed mines
    data_grid = np.zeros((int(size), int(size)))
    minemap = []
    for i in range(0, mines):
        l = 1
        while l == 1:
            a = random.randint(0, size - 1)
            b = random.randint(0, size - 1)
            if np.size(minemap) != 0:
                g = 0
                for k in range(i):
                    if np.array(minemap[k])[0] == a and np.array(minemap[k])[1] == b:
                        g = 1
                if g == 0:
                    minemap.append([a, b])
                    data_grid[a][b] = 1
                    l = 0
                elif g == 1:
                    l = 1
            else:
                minemap.append([a, b])
                l = 0
                
    # Add counters to the minemap matrix, how many
    # adjacent mines there are to each position
    for i in range(0,mines):
        for j in range(-1, 2):
             for k in range(-1, 2):
                 if minemap[i][0] + j >= 0 and minemap[i][0] + j <= size - 1  and minemap[i][1] + k >= 0 and minemap[i][1] + k <= size -1 :
                    data_grid[minemap[i][0] + j][minemap[i][1] + k] += 1

    # Add mines to the board, defined with a '-1'
    for i in range(0,mines):
        data_grid[minemap[i][0]][minemap[i][1]] = -1

    # Create the matrix to display to the user
    display_grid = np.full((size, size), '-')
    print('\n', display_grid)

    # Used to store 'shadow' data that isn't visible to the user,
    # used for checking surrounding nodes when taking a guess
    # 1: Checked, no surrounding mines
    # 2: Checked, surrounding mines
    shadow = np.zeros((int(size), int(size)))

    flagcount = 0      # How many flags the user has placed
    correct_flags = 0  # How many correct flags have been placed
    
    # Main running loop while the user plays
    running = True # to keep the game running
    while running:
        rPos = int(input('\nChoose the Row number: '))
        cPos = int(input('Choose the Column number: '))
        type = input('Type "f" for flag or "g" for guess: ')

        if type == guess:

            # Check if there is a mine
            if data_grid[rPos][cPos] == -1:
                print('You hit a mine, GAME OVER')
                display_grid[rPos][cPos] = 'M'
                running = False
                break
            
            # Check if there is a flag 
            elif display_grid[rPos][cPos] == 'F':
                flagcount += -1
                print('current flagcount: ', flagcount)

            # Check if there are no flags or mines
            elif data_grid[rPos][cPos] == 0:
                shadow[rPos][cPos] = 1

                # Search surrounding nodes for other blank spaces
                for j in range(-1, 2):
                    for k in range(-1, 2):
                        if rPos + j >= 0 and rPos + j <= size - 1 and cPos + k >= 0 and cPos + k <= size - 1:
                            if data_grid[rPos + j][cPos + k] == 0:
                                shadow[rPos + j][cPos + k] = 1
                                display_grid[rPos + j][cPos + k] = '0'

                            if data_grid[rPos + j][cPos + k] >= 1:
                                display_grid[rPos + j][cPos + k] = str(data_grid[rPos + j][cPos + k])
                                shadow[rPos + j][cPos + k] = 2
                
                shadow[rPos][cPos] = 2

                # Initialize list A, used for searching surroundings
                A = []
                for i in range(size):
                    A.append(int(i))
                for i in range(size - 1):
                    A.append(A[size - 2 - i])

                # Using the shadow matrix, find all adjacent
                # positions that need to be displayed to the user
                for i1 in A:
                    for j1 in A:
                        if shadow[i1][j1] == 1:
                            for j in [1, 0, -1]:
                                for k in [1, 0, -1]:
                                    if i1 + j >= 0 and i1 + j <= size - 1 and j1 + k >= 0 and int(j1) + k <= size - 1:
                                        if data_grid[i1 + j][j1 + k] == 0:
                                            shadow[i1 + j][j1 + k] = 1
                                            display_grid[i1 + j][j1 + k] = '0'

                                        if data_grid[i1 + j][j1 + k] >= 1:
                                            display_grid[i1 + j][j1 + k] = str(data_grid[i1 + j][j1 + k])
                                            shadow[i1 + j][j1 + k] = 2
                            shadow[i1][j1] = 2


            if data_grid[rPos][cPos] >= 0:
                shadow[rPos][cPos] = 2
                display_grid[rPos][cPos] = str(data_grid[rPos][cPos])

            print('You have : ', mines - flagcount, ' flags remaining.')
            print(' GAME: \n',display_grid)

        # Logic to run if the user places a flag
        if type == flag:
            flagcount += 1

            if flagcount <= mines:
                display_grid[rPos][cPos] = 'F'
                for i in range(mines):
                    if [rPos, cPos] == minemap[i]:
                        correct_flags += 1 # Counter of correct flags

                # Update the user on their remaining flags
                print('You have : ', mines - flagcount, ' flags remaining.')

                if flagcount == mines:
                    
                    # End the game if they have all correct flags
                    if correct_flags == mines:
                        print('\n--------YOU WIN---------')
                        total_time = int(time.time() - TIME)
                        print('The elapsed time was:', total_time, ' seconds !')
                        
                        # Update and show new leaderboard
                        if db:
                            cur.execute(create_row([f"'{username}'", total_time, f"'{datetime.datetime.now()}'", size, mines]))
                            cur.execute("SELECT * FROM minesweeper m ORDER BY m.score ASC")
                            print(f"the new leaderboard is:\n", np.array(cur.fetchall()))
                            con.commit()
                            cur.close()
                            con.close()
                            
                        running = False
                        break
                    
                    else:
                        print('Unfortunately (at least) one of your flags is wrong...')
            else:
                print('there are already ', str(mines), ' flags')
                flagcount += -1

            print('GAME: \n', display_grid)


# Main executable
if __name__ == '__main__':
    minesweeper(
        db=False
    )