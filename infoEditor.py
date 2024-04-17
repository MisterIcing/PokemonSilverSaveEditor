from enum import Enum
import os
import sys
import json

# File type class for offsetting save
class fileType(Enum):
    BGB = 1
    save = 2
    unknown = 3

# read in important values from JSON
with open('keyVals.json', 'r') as jsonFile:
    addr = json.load(jsonFile)


# Main function
def main(filename: str) -> None:
    if not os.path.exists(filename) or (fileTypeData := getFileType(filename)) == fileType.unknown:
        print("Could not validate file")

    # Display inventory & Party
    clearTerm()
    invTotal = int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["inventory"]["total"], filename), 1), byteorder='big')
    print(f"Inventory: {invTotal}")
    for x in range(1,21):
        dispItemRow(filename, fileTypeData, x, x == invTotal)
    partyTotal = int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["party"]["total"], filename), 1), 'big')
    print(f"Party: {partyTotal}")
    for x in range(1,7):
        dispPartyRow(filename, fileTypeData, x, x == partyTotal,)

    # modification loop
    while (mod := input('What would you like to modify[inventory, party, misc]: ').lower()) != 'exit':
        # inventory editing
        if mod == "inventory":
            if (inp := input('Which item would you like to modify (1 to 20): ').lower()) == 'back':
                continue

            # get RAM addresses
            itemNum = max(min(int(inp), 20), 1) #1-20
            totalAddr = addr["inventory"]["total"]
            itemAddr = addr["inventory"]["items"][str(itemNum)]

            # adjust to SNA addresses
            adjTotal = getAdjOffset(fileTypeData, totalAddr, filename)
            adjItem = getAdjOffset(fileTypeData, itemAddr[0], filename)
            adjQuant = getAdjOffset(fileTypeData, itemAddr[1], filename)
            
            # display selected item
            dispItemRow(filename, fileTypeData, itemNum, True)

            # item change section
            if (inp := input('New item value(int[0-255] or name): ').lower()) == 'back':
                continue
            # input handling
            val = item2byte(inp)
            if val == None:
                continue
            # save new bytes to file
            hexEdit(filename, adjItem, val)

            # amount change section
            if (inp := input('New item amount(int[0-255]): ').lower()) == 'back':
                continue
            # input handling
            val = int2byte(inp)
            if val == None:
                continue
            # save new bytes to file
            hexEdit(filename, adjQuant, val)

            # check to expand inventory range
            if int.from_bytes(hexRead(filename, adjTotal, 1), byteorder='big') < itemNum and int.from_bytes(hexRead(filename, adjItem, 1), 'big') != 0 and int.from_bytes(hexRead(filename, adjItem, 1), 'big') != 255:
                # increase inventory size to number
                hexEdit(filename, adjTotal, int.to_bytes(itemNum, 1, 'big'))
                # add cancel to item after
                    # values after are technically unallocated and thus allowed to be changed
                if itemNum == 20: # "edge case"
                    endAddr = getAdjOffset(fileTypeData, addr["inventory"]["end"], filename)
                    hexEdit(filename, endAddr, int.to_bytes(255, 1, 'big'))
                else:
                    nextAddr = getAdjOffset(fileTypeData, addr["inventory"]["items"][str(itemNum+1)][0], filename)
                    hexEdit(filename, nextAddr, int.to_bytes(255, 1, 'big'))

            # check to shrink inventory range
            lastValid = 0
            for x in range(1,21):
                item = getAdjOffset(fileTypeData, addr["inventory"]["items"][str(x)][0], filename)
                inByte = int.from_bytes(hexRead(filename, item, 1), 'big')
                if inByte != 0 and inByte != 255:
                    lastValid = x
            # change if inv is different from current total
            invTotal = int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["inventory"]["total"], filename), 1), byteorder='big')
            if lastValid != 20:
                hexEdit(filename, adjTotal, int.to_bytes(lastValid, 1, 'big'))
                nextAddr = getAdjOffset(fileTypeData, addr["inventory"]["items"][str(lastValid+1)][0], filename)
                hexEdit(filename, nextAddr, int.to_bytes(255, 1, 'big'))
        
        # party modification
        if mod == "party":
            if (pNum := input('Which pokemon would you like to modify (1 to 6): ').lower()) == 'back':
                continue
            
            # get selected pokemon & disp
            clearTerm()
            partyTotal = int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["party"]["total"], filename), 1), 'big')
            pokeNum: int = max(min(int(pNum), 6), 1) #1-6
            print(f"Party: {partyTotal:1}")
            dispPartyRow(filename, fileTypeData, pokeNum, True, True)
            
            # prompt what to change
            while (inp := input('[pokemon, name, hp, level, exp, item, move #, attack, attEV, defense, defEV, speed, spdEV, spAttack, spDefense, spcEV, attdefIV, spdspcIV]\nWhat would you like to modify: ').lower()) != 'back':
                # change which pokemon it is
                if inp == "pokemon":
                    # change both positions, I think one just controls the icon
                    if (inp := input('New pokemon(int[0-255] or name): ').lower()) != 'back':
                        val = pkmn2byte(inp)
                        if val == None:
                            continue
                        offset = [getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["pokemon"][x], filename) for x in range(2)]
                        for x in range(2):
                            hexEdit(filename, offset[x], val)

                elif inp == "name":
                    # ask for 10 letter name, encode w/\x50
                    newName = input("New name(10 characters): ")
                    newName = newName[:10]
                    byteArr = toString(newName)
                    for x in range(11):
                        hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["name"][x], filename), byteArr[x])

                elif inp == "hp":
                    # change both hp & maxhp(if lower than hp)
                    if (inp := input('New HP amount(int[0-65535])\nNote: math caps at 0x03e7(999): ').lower()) == 'back':
                        continue
                    # input handling
                    val = int2byte(inp, 2)
                    if val == None:
                        continue
                    # save new bytes to file
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["hp"][0], filename), val)
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["hpev"][0], filename), val)

                    # increase max health to match
                    if int.from_bytes(val, 'big') > int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["maxHp"][0], filename), 2), 'big'):
                        hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["maxHp"][0], filename), val)

                elif inp == "level":
                    if (inp := input('New level(int[0-255]): ').lower()) == 'back':
                        continue
                    # input handling
                    val = int2byte(inp)
                    if val == None:
                        continue
                    # save new bytes to file
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["level"], filename), val)
                elif inp == "exp":
                    if (inp := input('New exp(int[0-16777215])\nNote: Level 100 is 0x0f4240(1000000): ').lower()) == 'back':
                        continue
                    # input handling
                    val = int2byte(inp, 3)
                    if val == None:
                        continue
                    # save new bytes to file
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["exp"][0], filename), val)

                elif inp == "item":
                    # similar to inventory editing
                    if (inp := input('New item value(int[0-255] or name): ').lower()) == 'back':
                        continue
                    # input handling
                    val = item2byte(inp)
                    if val == None:
                        continue
                    # save new bytes to file
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["item"], filename), val)

                elif inp.find("move") != -1:
                    id = inp.split(" ")[-1] # extract move number
                    if not id.isdigit():
                        continue
                    id = min(max((int(id)-1) , 0), 3) #0-3
                    if (inp := input('New move(int[0-255] or name): ').lower()) == 'back':
                        continue
                    # input handling
                    val = mov2byte(inp)
                    if val == None:
                        continue
                    # save new bytes to file
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["moves"][id], filename), val)
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["pp"][id], filename), b'\x39')

                elif inp == "attack":
                    if (inp := input('New attack(int[0-65535]): ').lower()) == 'back':
                        continue
                    # input handling
                    val = int2byte(inp, 2)
                    if val == None:
                        continue
                    # save new bytes to file
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["attack"][0], filename), val)
                elif inp == "attev":
                    if (inp := input('New attack EV(int[0-65535]): ').lower()) == 'back':
                        continue
                    # input handling
                    val = int2byte(inp, 2)
                    if val == None:
                        continue
                    # save new bytes to file
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["atkev"][0], filename), val)


                elif inp == "defense":
                    if (inp := input('New defense(int[0-65535]): ').lower()) == 'back':
                        continue
                    # input handling
                    val = int2byte(inp, 2)
                    if val == None:
                        continue
                    # save new bytes to file
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["defense"][0], filename), val)
                elif inp == "defev":
                    if (inp := input('New defense EV(int[0-65535]): ').lower()) == 'back':
                        continue
                    # input handling
                    val = int2byte(inp, 2)
                    if val == None:
                        continue
                    # save new bytes to file
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["defev"][0], filename), val)

                elif inp == "speed":
                    if (inp := input('New speed(int[0-65535]): ').lower()) == 'back':
                        continue
                    # input handling
                    val = int2byte(inp, 2)
                    if val == None:
                        continue
                    # save new bytes to file
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["speed"][0], filename), val)
                elif inp == "spdev":
                    if (inp := input('New speed EV(int[0-65535]): ').lower()) == 'back':
                        continue
                    # input handling
                    val = int2byte(inp, 2)
                    if val == None:
                        continue
                    # save new bytes to file
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["spdev"][0], filename), val)

                elif inp == "spattack":
                    if (inp := input('New special attack(int[0-65535]): ').lower()) == 'back':
                        continue
                    # input handling
                    val = int2byte(inp, 2)
                    if val == None:
                        continue
                    # save new bytes to file
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["spAttack"][0], filename), val)
                elif inp == "spdefense":
                    if (inp := input('New special defense(int[0-65535]): ').lower()) == 'back':
                        continue
                    # input handling
                    val = int2byte(inp, 2)
                    if val == None:
                        continue
                    # save new bytes to file
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["spDefense"][0], filename), val)
                elif inp == "spcev":
                    if (inp := input('New special EV value(int[0-65535]): ').lower()) == 'back':
                        continue
                    # input handling
                    val = int2byte(inp, 2)
                    if val == None:
                        continue
                    # save new bytes to file
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["spcev"][0], filename), val)

                elif inp == "attdefiv":
                    if (inp := input('New attack/defense IV(int[0-255]): ').lower()) == 'back':
                        continue
                    # input handling
                    val = int2byte(inp, 1)
                    if val == None:
                        continue
                    # save new bytes to file
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["adiv"], filename), val)
                
                elif inp == "spdspciv":
                    if (inp := input('New speed/special IV(int[0-255]): ').lower()) == 'back':
                        continue
                    # input handling
                    val = int2byte(inp, 1)
                    if val == None:
                        continue
                    # save new bytes to file
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["sdiv"], filename), val)
                elif inp == "pokerus":
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["pokerus"], filename), b'\xff') # 4 day strain @ 15 days
                elif inp == "status":
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["status"], filename), b'\x00')

                # Change max pokemon to highest edited
                if (pNum := int(pNum)) > (partyTotal := int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["party"]["total"], filename), 1), 'big')):
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["total"], filename), int.to_bytes(pNum, 1, 'big'))

                # display updated info
                clearTerm()
                partyTotal = int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["party"]["total"], filename), 1), 'big')
                pokeNum: int = max(min(int(pNum), 6), 1) #1-6
                print(f"Party: {partyTotal:1}")
                dispPartyRow(filename, fileTypeData, pokeNum, True, True)

        if mod == "misc":
            clearTerm()
            while (inp := input('Toggle[johto badges, kanto badges]/max[money, cached, casino, repel, fly]/mod[pos] which value: ').lower()) != 'back':
                if inp.find("johto") != -1:
                    badges = hexRead(filename, getAdjOffset(fileTypeData, addr["misc"]["jBadges"], filename), 1)
                    if badges != b'\xff':
                        hexEdit(filename, getAdjOffset(fileTypeData, addr["misc"]["jBadges"], filename), b'\xff')
                    else:
                        hexEdit(filename, getAdjOffset(fileTypeData, addr["misc"]["jBadges"], filename), b'\x00')
                elif inp.find("kanto") != -1:
                    badges = hexRead(filename, getAdjOffset(fileTypeData, addr["misc"]["kBadges"], filename), 1)
                    if badges != b'\xff':
                        hexEdit(filename, getAdjOffset(fileTypeData, addr["misc"]["kBadges"], filename), b'\xff')
                    else:
                        hexEdit(filename, getAdjOffset(fileTypeData, addr["misc"]["kBadges"], filename), b'\x00')
                elif inp == "money":
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["misc"]["money"][0], filename), b'\xff\xff\xff')
                elif inp == "cached":
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["misc"]["storedMoney"][0], filename), b'\xff\xff\xff')
                elif inp == "casino":
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["misc"]["casino"][0], filename), b'\xff\xff')
                elif inp == "repel":
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["misc"]["repel"], filename), b'\xff')
                elif inp == "fly":
                    hexEdit(filename, getAdjOffset(fileTypeData, addr["misc"]["fly"][0], filename), b'\xff\xff\xff\xff')
                elif inp == "pos":
                    dir = input(f'({hex(int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["misc"]["posXY"][0], filename), 1), "big"))},{hex(int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["misc"]["posXY"][1], filename), 1), "big"))}) Nudge which direction(up, down, left, right): ')
                    if dir == 'up':
                        hexEdit(filename, getAdjOffset(fileTypeData, addr["misc"]["posXY"][1], filename), int2byte(str(int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["misc"]["posXY"][1], filename), 1), 'big')-1)))
                    elif dir == 'down':
                        hexEdit(filename, getAdjOffset(fileTypeData, addr["misc"]["posXY"][1], filename), int2byte(str(int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["misc"]["posXY"][1], filename), 1), 'big')+1)))
                    elif dir == 'left':
                        hexEdit(filename, getAdjOffset(fileTypeData, addr["misc"]["posXY"][0], filename), int2byte(str(int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["misc"]["posXY"][0], filename), 1), 'big')-1)))
                    elif dir == 'right':
                        hexEdit(filename, getAdjOffset(fileTypeData, addr["misc"]["posXY"][0], filename), int2byte(str(int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["misc"]["posXY"][0], filename), 1), 'big')+1)))
                input(f"{inp.title()} toggled/maxed/modified")

        
        # redisplay info
        clearTerm()
        invTotal = int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["inventory"]["total"], filename), 1), byteorder='big')
        print(f"Inventory: {invTotal}")
        for x in range(1,21):
            dispItemRow(filename, fileTypeData, x, x == invTotal)
        partyTotal = int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["party"]["total"], filename), 1), 'big')
        print(f"Party: {partyTotal}")
        for x in range(1,7):
            dispPartyRow(filename, fileTypeData, x, x == partyTotal,)

# Function to check which type of file is being edited(save or savestate)
def getFileType(filename):
    # BGB save state header is BGB
    if hexRead(filename, 0, 3) == b'BGB':
        return fileType.BGB
    # .sav files have no dissernable header
    # assume extension is always correct
    elif filename.split('.')[-1] == 'sav':
        return fileType.save
    else:
        return fileType.unknown
    
# Function to get adjusted offset whether it is a save state or save file
def getAdjOffset(type: fileType, offset: int, filename) -> int:
    # print(f"Origial Offset: {hex(offset)}")
    # print(f"WRAM start: {hex(hexFind(filename, 'WRAM'))}")
    if type == fileType.BGB: # adjusts RAM to SNA
        offset = (offset - 0xc000) + (hexFind(filename, "WRAM")+0x9)
    elif type == fileType.save:
        offset = offset - 0xc93c
    # print(f"New Offset: {hex(offset)}")
    return offset

# Displays single row for item table or item display
def dispItemRow(filename, type, itemNum, arrow: bool=False) -> None:
    # get the item's hex value
    itemHex = hex(int.from_bytes(hexRead(filename, getAdjOffset(type, addr["inventory"]["items"][str(itemNum)][0], filename), 1), byteorder='big'))

    # get the item's quantity
    itemQuant = hex(int.from_bytes(hexRead(filename, getAdjOffset(type, addr["inventory"]["items"][str(itemNum)][1], filename), 1), byteorder='big'))

    # 
    itemConv = addr["convert"][str(int.from_bytes(hexRead(filename, getAdjOffset(type, addr["inventory"]["items"][str(itemNum)][0], filename), 1), byteorder='big'))]["item"]
    print(f"{'->' if arrow else ''}\tItem {itemNum:2}: {itemHex:4}({itemConv.title():^14}) Amount: {itemQuant:4}")

# Displays single row for party table or pokemon display
def dispPartyRow(filename, type, pokeNum, arrow: bool=False, extended: bool=False):
    # get name value
    name = [int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["name"][x], filename), 1), 'big') for x in range(10)]
    name: str = getString(name)
    pokeName: str = addr["convert"][str(int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["pokemon"][0], filename), 1), 'big'))]["pokemon"]
    adivby = hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["adiv"], filename), 1)
    ssivby = hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["sdiv"], filename), 1)
    
    print(f"{'->' if arrow else ''}\tPokemon {pokeNum:1}: {name:<10} ({pokeName.title():<10}){'*' if (((int.from_bytes(adivby, 'big') & 0xf0) >> 4) in {2, 3, 6, 7, 10, 11, 14, 15} and (int.from_bytes(adivby, 'big') & 0x0f) == 10 and (int.from_bytes(ssivby, 'big') & 0x0f) == 10 and ((int.from_bytes(ssivby, 'big') & 0xf0) >> 4) == 10) else ''}")
    if extended:
        hp: int = int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["hp"][0], filename), 2), 'big')
        maxHp: int = int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["maxHp"][0], filename), 2), 'big')
        level: int = int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["level"], filename), 1), 'big')
        heldItem:str = addr["convert"][str(int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["item"], filename), 1), 'big'))]["item"]
        moves: list[str] = [addr["convert"][str(int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["moves"][x], filename), 1), 'big'))]["move"] for x in range(4)]
        pp: list[int] = [int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["pp"][x], filename), 1), 'big') for x in range(4)]
        att: int = int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["atkev"][0], filename), 2), 'big')
        defe: int = int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["defev"][0], filename), 2), 'big')
        spd: int = int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["spdev"][0], filename), 2), 'big')
        sp: int = int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["spcev"][0], filename), 2), 'big')
        adiv: int = int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["adiv"], filename), 1), 'big')
        sdiv: int = int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["sdiv"], filename), 1), 'big')
        attVal = int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["attack"][0], filename), 2), 'big')
        defVal = int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["defense"][0], filename), 2), 'big')
        spdVal = int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["speed"][0], filename), 2), 'big')
        spAtkVal = int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["spAttack"][0], filename), 2), 'big')
        spDefVal = int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["spDefense"][0], filename), 2), 'big')
        status = int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["status"], filename), 2), 'big')
        exp = int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["exp"][0], filename), 3), 'big')
        pokerus = int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["pokerus"], filename), 1), 'big') & 0x0f

        print(f"\t\tHP:{'!' if (status != 0) or (pokerus > 0) else ' '}\t{hp:>5}/{maxHp:<5}")
        print(f"\t\tLevel: \t{level:<3}")
        print(f"\t\tEXP: \t{exp:>8}/1000000")
        print(f"\t\tItem: \t{heldItem.title():<14}")
        print(f"\t\tMoves: ")
        for x in range(4):
            print(f"\t\t\tMove {(x+1):1}: {moves[x]:>14}({pp[x]:3})")
        print(f"\t\tAttack (EV):\t\t{attVal:>5}({att:<5})\n\t\tDefense (EV):\t\t{defVal:>5}({defe:<5})\n\t\tSpeed (EV):\t\t{spdVal:>5}({spd:<5})\n\t\tSpecial Attack (EV):\t{spAtkVal:>5}({sp:<5})\n\t\tSpecial Defense (EV):\t{spDefVal:>5}({sp:<5})")
        print(f"\t\tAttack/Defense IV:\t{adiv:>5}\n\t\tSpeed/Special IV:\t{sdiv:>5}")

# Generates a string from int array
# Transitions GBA chars to ascii
def getString(charStar) -> str:
    buildStr = ''
    for char in charStar:
        if char == 80:
            break
        try: 
            buildStr += chr(char - 63) or "?"
        except ValueError:
            buildStr += "?"
    return buildStr

# Generates bytes array from string
def toString(charStar:str) -> list[bytes]:
    arr = []
    # Fill in letters to length
    for char in charStar:
        arr.append(ord(char) + 63)
    for x in range(len(arr),11): #11 spaces w/delim
        arr.append(0x50)
    arr: list[bytes] = [int.to_bytes(arr[x], 1, 'big') for x in range(len(arr))]
    return arr

# Function to handle pokemon to byte data for saving
def pkmn2byte(inp):
    attempt = int2byte(inp)
    if attempt == None:
        for key, arr in addr["convert"].items():
            if arr["pokemon"] == inp:
                return int.to_bytes(int(key), 1, 'big')
        print("Could not find pokemon. Please refer to keyVals.json's convert for names.")
    else:
        return attempt
    return None

# Function to handle move to byte data for saving
def mov2byte(inp):
    attempt = int2byte(inp)
    if attempt == None:
        for key, arr in addr["convert"].items():
            if arr["move"] == inp:
                return int.to_bytes(int(key), 1, 'big')
        print("Could not find move. Please refer to keyVals.json's convert for names.")
    else:
        return attempt
    return None
    # I thought about just making 1 dynamic, but its too late now

# Function to handle item to byte data for saving
def item2byte(inp) -> bytes | None:
    attempt = int2byte(inp)
    if attempt == None:
        for key, items in addr["convert"].items():
            if items["item"] == inp:
                return int.to_bytes(int(key), 1, byteorder='big')
        print(f"Could not find item. Please refer to keyVals.json's convert for names.")
    else:
        return attempt
    return None

# Function to handle numbers to bytedata
def int2byte(inp, byteSize=1) -> bytes | None:
    # try decimal
    if inp.isdigit():
        return int.to_bytes(max(min(int(inp), 2**(8*byteSize)-1), 0), byteSize, byteorder='big')
    # try hex
    elif inp[:2] == "0x":
        return int.to_bytes(max(min(int(inp, 16), 2**(8*byteSize)-1), 0), byteSize, byteorder='big')
    # try bin
    elif inp[:2] == "0b":
        return int.to_bytes(max(min(int(inp, 2), 2**(8*byteSize)-1), 0), byteSize, byteorder='big')
    return None

# Function to edit the hex at the offset
# Assumes data fits correctly to what should change
def hexEdit(filename: str, offset: int, data: int) -> None:
    with open(filename, 'r+b') as file:
        file.seek(offset)
        file.write(data)
    
# Function to read length bytes of data at offset
def hexRead(filename: str, offset: int, length: int) -> bytes:
    with open(filename, 'rb') as file:
        file.seek(offset)
        return file.read(length)
    
# Function to find hex in file
# Used to find start of WRAM
def hexFind(filename: str, string: str):
    with open(filename, 'rb') as file:
        hexdump = file.read().hex()
    searchHex = string.encode().hex()
    return hexdump.find(searchHex)//2

# Function to clear terminal output so that it look slike things update
def clearTerm() -> None:
    # For Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # For Unix/Linux/MacOS
    else:
        _ = os.system('clear')


# run handling
if __name__ == '__main__':
    clearTerm()
    if len(sys.argv) >= 2:
        main(sys.argv[1])
    else:
        filename: str = input("Name of file to open: ")
        main(filename)