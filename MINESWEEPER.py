import random
import numpy as np
import time


def minesweeper():
    size = int(input('What size grid would you like ? (n x n): '))
    mines = int(input('How many mines would you like?: '))

    TIME = time.time()
    emptymat = np.zeros((int(size), int(size)))
    minemap=[]

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
                    emptymat[a][b] = 1
                    l = 0
                elif g == 1:
                    l = 1
            else:
                minemap.append([a, b])
                l = 0

    #print(minemap)

    for i in range(0,mines):
        for j in range(-1, 2):
             for k in range(-1, 2):
                 if minemap[i][0] + j >= 0 and minemap[i][0] + j <= size - 1  and minemap[i][1] + k >= 0 and minemap[i][1] + k <= size -1 :
                    emptymat[minemap[i][0] + j][minemap[i][1] + k] += 1


    for i in range(0,mines):
        emptymat[minemap[i][0]][minemap[i][1]] = -1

    t = 1 # to keep the game running

    qmat1 = []

    for j in range(size):
        quickmat = []
        for i in range(size):
            quickmat.append('-')
        qmat1 = qmat1 + [quickmat]

    qmat2 = np.array(qmat1)

    print('\n', qmat2)

    shadow = np.zeros((int(size), int(size)))


    flagcount = 0
    d = 0 # the correct flag counter

    while t == 1:
        Rpos = input('\nChoose the Row number: ')
        Cpos = input('Choose the Column number: ')
        type = input('Type "f" for flag or "g" for guess: ')

        if type == 'g':

            if emptymat[int(Rpos)][int(Cpos)] == -1:
                print('You hit a mine, GAME OVER')
                qmat2[int(Rpos)][int(Cpos)] = 'M'
                t = 0

            if qmat2[int(Rpos)][int(Cpos)] == 'F':
                flagcount += -1
                print('current flagcount: ', flagcount)

            if emptymat[int(Rpos)][int(Cpos)] == 0:
                shadow[int(Rpos)][int(Cpos)] = 1




                # search

                for j in range(-1, 2):
                    for k in range(-1, 2):
                        if int(Rpos) + j >= 0 and int(Rpos) + j <= size - 1 and int(Cpos) + k >= 0 and int(Cpos) + k <= size - 1:
                            if emptymat[int(Rpos) + j][int(Cpos) + k] == 0:
                                shadow[int(Rpos) + j][int(Cpos) + k] = 1
                                qmat2[int(Rpos) + j][int(Cpos) + k] = '0'

                            if emptymat[int(Rpos) + j][int(Cpos) + k] >= 1:
                                qmat2[int(Rpos) + j][int(Cpos) + k] = str(emptymat[int(Rpos) + j][int(Cpos) + k])
                                shadow[int(Rpos) + j][int(Cpos) + k] = 2
                shadow[int(Rpos)][int(Cpos)] = 2



                A = []
                for i in range(size):
                    A.append(int(i))

                for i in range(size - 1):
                    A.append(A[size - 2 - i])


                for i1 in A:
                    for j1 in A:
                        if shadow[i1][j1] == 1:
                            for j in [1, 0, -1]:
                                for k in [1, 0, -1]:
                                    if i1 + j >= 0 and i1 + j <= size - 1 and j1 + k >= 0 and int(j1) + k <= size - 1:
                                        if emptymat[i1 + j][j1 + k] == 0:
                                            shadow[i1 + j][j1 + k] = 1
                                            qmat2[i1 + j][j1 + k] = '0'

                                        if emptymat[i1 + j][j1 + k] >= 1:
                                            qmat2[i1 + j][j1 + k] = str(emptymat[i1 + j][j1 + k])
                                            shadow[i1 + j][j1 + k] = 2
                            shadow[i1][j1] = 2


            if emptymat[int(Rpos)][int(Cpos)] >= 0:
                shadow[int(Rpos)][int(Cpos)] = 2
                qmat2[int(Rpos)][int(Cpos)] = str(emptymat[int(Rpos)][int(Cpos)])

            print('You have : ', mines - flagcount, ' flags remaining.')
            print(' GAME: \n',qmat2)

        if type == 'f':
            flagcount += 1

            if flagcount <= mines:
                qmat2[int(Rpos)][int(Cpos)] = 'F'
                for i in range(mines):
                    if [int(Rpos), int(Cpos)] == minemap[i]:
                        d += 1 # conunter of correct flags


                print('You have : ', mines - flagcount, ' flags remaining.')

                if flagcount == mines:

                    if d == mines:
                        print('\n--------YOU WIN---------')
                        print('The elapsed time was:', int(time.time() - TIME), ' seconds !')
                        return
                    else:
                        print('Unfortunately (at least) one of your flags is wrong...')
            else:
                print('there are already ', str(mines), ' flags')
                flagcount += -1

            print('GAME: \n', qmat2)


minesweeper()
input()
