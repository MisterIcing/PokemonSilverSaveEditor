from enum import Enum
import os
import sys
import json

saveFile = './bgb/Ace-1.sna'
# saveFile = './bgb/Pokemon - Silver Version (USA, Europe) (SGB Enhanced) (GB Compatible).sav'
# saveFile = './bgb/bgb.html'

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
    elif fileTypeData == fileType.BGB:
        # Sets translation offset to 0x1fa0
        # Display inventory & Party
        clearTerm()
        invTotal = int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["inventory"]["total"]), 1), byteorder='big')
        print(f"Inventory: {invTotal}")
        for x in range(1,21):
            dispItemRow(filename, fileTypeData, x, x == invTotal)
        partyTotal = int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["party"]["total"]), 1), 'big')
        print(f"Party: {partyTotal}")
        for x in range(1,7):
            dispPartyRow(filename, fileTypeData, x, x == partyTotal,)

        # modification loop
        while (mod := input('What would you like to modify[inventory, party]: ').lower()) != 'exit':
            # inventory editing
            if mod == "inventory":
                if (inp := input('Which item would you like to modify (1 to 20): ').lower()) == 'back':
                    continue

                # get RAM addresses
                itemNum = max(min(int(inp), 20), 1) #1-20
                totalAddr = addr["inventory"]["total"]
                itemAddr = addr["inventory"]["items"][str(itemNum)]

                # adjust to SNA addresses
                adjTotal = getAdjOffset(fileTypeData, totalAddr)
                adjItem = getAdjOffset(fileTypeData, itemAddr[0])
                adjQuant = getAdjOffset(fileTypeData, itemAddr[1])
               
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
                        endAddr = getAdjOffset(fileTypeData, addr["inventory"]["end"])
                        hexEdit(filename, endAddr, int.to_bytes(255, 1, 'big'))
                    else:
                        nextAddr = getAdjOffset(fileTypeData, addr["inventory"]["items"][str(itemNum+1)][0])
                        hexEdit(filename, nextAddr, int.to_bytes(255, 1, 'big'))

                # check to shrink inventory range
                lastValid = 0
                for x in range(1,21):
                    item = getAdjOffset(fileTypeData, addr["inventory"]["items"][str(x)][0])
                    inByte = int.from_bytes(hexRead(filename, item, 1), 'big')
                    if inByte != 0 and inByte != 255:
                        lastValid = x
                # change if inv is different from current total
                invTotal = int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["inventory"]["total"]), 1), byteorder='big')
                if lastValid != 20:
                    hexEdit(filename, adjTotal, int.to_bytes(lastValid, 1, 'big'))
                    nextAddr = getAdjOffset(fileTypeData, addr["inventory"]["items"][str(lastValid+1)][0])
                    hexEdit(filename, nextAddr, int.to_bytes(255, 1, 'big'))
            
            # party modification
            if mod == "party":
                if (pNum := input('Which pokemon would you like to modify (1 to 6): ').lower()) == 'back':
                    continue
                
                # get selected pokemon & disp
                clearTerm()
                pokeNum: int = max(min(int(pNum), 6), 1) #1-6
                dispPartyRow(filename, fileTypeData, pokeNum, True, True)
                
                # prompt what to change
                while (inp := input('[pokemon, name, hp, level, item, move #, attack, defense, speed, spAttack, spDefense]\nWhat would you like to modify: ').lower()) != 'back':
                    # change which pokemon it is
                    if inp == "pokemon":
                        # change both positions, I think one just controls the icon
                        if (inp := input('New pokemon(int[0-255] or name): ').lower()) != 'back':
                            val = pkmn2byte(inp)
                            if val == None:
                                continue
                            offset = [getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["pokemon"][x]) for x in range(2)]
                            for x in range(2):
                                hexEdit(filename, offset[x], val)

                    elif inp == "name":
                        # ask for 10 letter name, encode w/\x50
                        newName = input("New name(10 characters): ")
                        newName = newName[:10]
                        byteArr = toString(newName)
                        for x in range(11):
                            hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["name"][x]), byteArr[x])

                    elif inp == "hp":
                        # change both hp & maxhp(if lower than hp)
                        if (inp := input('New HP amount(int[0-65535])\nNote: math caps at 0x03e7(999): ').lower()) == 'back':
                            continue
                        # input handling
                        val = int2byte(inp, 2)
                        if val == None:
                            continue
                        # save new bytes to file
                        hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["hp"][0]), val)

                        # increase max health to match
                        if int.from_bytes(val, 'big') > int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["maxHp"][0]), 2), 'big'):
                            hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["maxHp"][0]), val)

                    elif inp == "level":
                        if (inp := input('New level(int[0-255]): ').lower()) == 'back':
                            continue
                        # input handling
                        val = int2byte(inp)
                        if val == None:
                            continue
                        # save new bytes to file
                        hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["level"]), val)

                    elif inp == "item":
                        # similar to inventory editing
                        if (inp := input('New item value(int[0-255] or name): ').lower()) == 'back':
                            continue
                        # input handling
                        val = item2byte(inp)
                        if val == None:
                            continue
                        # save new bytes to file
                        hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["item"]), val)

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
                        hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["moves"][id]), val)
                        hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["pp"][id]), b'\x39')

                    elif inp == "attack":
                        if (inp := input('New attack value(int[0-65535])\nNote: display caps at 0x03e7(999): ').lower()) == 'back':
                            continue
                        # input handling
                        val = int2byte(inp, 2)
                        if val == None:
                            continue
                        # save new bytes to file
                        hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["attack"][0]), val)

                    elif inp == "defense":
                        if (inp := input('New defense value(int[0-65535])\nNote: display caps at 0x03e7(999): ').lower()) == 'back':
                            continue
                        # input handling
                        val = int2byte(inp, 2)
                        if val == None:
                            continue
                        # save new bytes to file
                        hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["defense"][0]), val)

                    elif inp == "speed":
                        if (inp := input('New speed value(int[0-65535])\nNote: display caps at 0x03e7(999): ').lower()) == 'back':
                            continue
                        # input handling
                        val = int2byte(inp, 2)
                        if val == None:
                            continue
                        # save new bytes to file
                        hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["speed"][0]), val)

                    elif inp == "spattack":
                        if (inp := input('New special attack value(int[0-65535])\nNote: display caps at 0x03e7(999): ').lower()) == 'back':
                            continue
                        # input handling
                        val = int2byte(inp, 2)
                        if val == None:
                            continue
                        # save new bytes to file
                        hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["spAttack"][0]), val)

                    elif inp == "spdefense":
                        if (inp := input('New special defense value(int[0-65535])\nNote: display caps at 0x03e7(999): ').lower()) == 'back':
                            continue
                        # input handling
                        val = int2byte(inp, 2)
                        if val == None:
                            continue
                        # save new bytes to file
                        hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["party"][str(pokeNum)]["spDefense"][0]), val)

                    # Change max pokemon to highest edited
                    if (pNum := int(pNum)) > (partyTotal := int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["party"]["total"]), 1), 'big')):
                        hexEdit(filename, getAdjOffset(fileTypeData, addr["party"]["total"]), int.to_bytes(pNum, 1, 'big'))

                    # display updated info
                    clearTerm()
                    partyTotal = int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["party"]["total"]), 1), 'big')
                    pokeNum: int = max(min(int(pNum), 6), 1) #1-6
                    print(f"Party: {partyTotal:1}")
                    dispPartyRow(filename, fileTypeData, pokeNum, True, True)
                    
            
            # redisplay info
            clearTerm()
            invTotal = int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["inventory"]["total"]), 1), byteorder='big')
            print(f"Inventory: {invTotal}")
            for x in range(1,21):
                dispItemRow(filename, fileTypeData, x, x == invTotal)
            partyTotal = int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["party"]["total"]), 1), 'big')
            print(f"Party: {partyTotal}")
            for x in range(1,7):
                dispPartyRow(filename, fileTypeData, x, x == partyTotal,)

    elif fileTypeData == fileType.save:
        # Set translation offset
        print("Save file")
    else:
       print("Major error")
       exit(1)
    exit(0)

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
def getAdjOffset(type: fileType, offset: int) -> int:
    # print(f"Origial Offset: {hex(offset)}")
    if type == fileType.BGB: # adjusts RAM to SNA by -0xba82
        offset = offset - 0xba82
    # print(f"New Offset: {hex(offset)}")
    return offset

# Displays single row for item table or item display
def dispItemRow(filename, type, itemNum, arrow: bool=False) -> None:
    # get the item's hex value
    itemHex = hex(int.from_bytes(hexRead(filename, getAdjOffset(type, addr["inventory"]["items"][str(itemNum)][0]), 1), byteorder='big'))

    # get the item's quantity
    itemQuant = hex(int.from_bytes(hexRead(filename, getAdjOffset(type, addr["inventory"]["items"][str(itemNum)][1]), 1), byteorder='big'))

    # 
    itemConv = addr["convert"][str(int.from_bytes(hexRead(filename, getAdjOffset(type, addr["inventory"]["items"][str(itemNum)][0]), 1), byteorder='big'))]["item"]
    print(f"{'->' if arrow else ''}\tItem {itemNum:2}: {itemHex:4}({itemConv.title():^14}) Amount: {itemQuant:4}")

# Displays single row for party table or pokemon display
def dispPartyRow(filename, type, pokeNum, arrow: bool=False, extended: bool=False):
    # get name value
    name = [int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["name"][x]), 1), 'big') for x in range(10)]
    name: str = getString(name)
    pokeName: str = addr["convert"][str(int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["pokemon"][0]), 1), 'big'))]["pokemon"]
    print(f"{'->' if arrow else ''}\tPokemon {pokeNum:1}: {name:<10} ({pokeName.title():<10})")
    if extended:
        hp: int = int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["hp"][0]), 2), 'big')
        maxHp: int = int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["maxHp"][0]), 2), 'big')
        level: int = int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["level"]), 1), 'big')
        heldItem:str = addr["convert"][str(int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["item"]), 1), 'big'))]["item"]
        moves: list[str] = [addr["convert"][str(int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["moves"][x]), 1), 'big'))]["move"] for x in range(4)]
        pp: list[int] = [int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["pp"][x]), 1), 'big') for x in range(4)]
        att: int = int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["attack"][0]), 2), 'big')
        defe: int = int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["defense"][0]), 2), 'big')
        spd: int = int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["speed"][0]), 2), 'big')
        spAtt: int = int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["spAttack"][0]), 2), 'big')
        spDef: int = int.from_bytes(hexRead(filename, getAdjOffset(type, addr["party"]["party"][str(pokeNum)]["spDefense"][0]), 2), 'big')

        print(f"\t\tHP: \t{hp:>5}/{maxHp:<5}")
        print(f"\t\tLevel: \t{level:<3}")
        print(f"\t\tItem: \t{heldItem.title():<14}")
        print(f"\t\tMoves: ")
        for x in range(4):
            print(f"\t\t\tMove {(x+1):1}: {moves[x]:>14}({pp[x]:3})")
        print(f"\t\tAttack: {att:>5}\n\t\tDefense: {defe:>5}\n\t\tSpeed: {spd:>5}")
        print(f"\t\tSpecial Attack: {spAtt:>5}\n\t\tSpecial Defense: {spDef:>5}")

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
    # try decimal
    if inp.isdigit():
        return int.to_bytes(max(min(int(inp), 255), 0), 1, byteorder='big')
    # try hex
    elif inp[:2] == "0x":
        return int.to_bytes(max(min(int(inp, 16), 255), 0), 1, byteorder='big')
    # try string to key to hex
    else:
        for key, items in addr["convert"].items():
            if items["item"] == inp:
                return int.to_bytes(int(key), 1, byteorder='big')
        print(f"Could not find item. Please refer to keyVals.json's convert for names.")
    return None

# Function to handle numbers to bytedata
def int2byte(inp, byteSize=1) -> bytes | None:
    # try decimal
    if inp.isdigit():
        return int.to_bytes(max(min(int(inp), 2**(8*byteSize)-1), 0), byteSize, byteorder='big')
    # try hex
    elif inp[:2] == "0x":
        return int.to_bytes(max(min(int(inp, 16), 2**(8*byteSize)-1), 0), byteSize, byteorder='big')
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
        # filename: str = input("Name of file to open: ")
        main(saveFile)
    input("Enter to exit")