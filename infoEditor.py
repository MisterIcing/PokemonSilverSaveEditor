from curses.ascii import isdigit
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
        invTotal = int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["inventory"]["total"]), 1), byteorder='little')
        print(f"Inventory: {invTotal}")
        for x in range(1,21):
            dispItemRow(filename, fileTypeData, x, x == invTotal)

        # modification loop
        while (mod := input('What would you like to modify[inventory, party]: ').lower()) != 'exit':
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
                if int.from_bytes(hexRead(filename, adjTotal, 1), byteorder='little') < itemNum and int.from_bytes(hexRead(filename, adjItem, 1), 'little') != 0 and int.from_bytes(hexRead(filename, adjItem, 1), 'little') != 255:
                    # increase inventory size to number
                    hexEdit(filename, adjTotal, int.to_bytes(itemNum, 1, 'little'))
                    # add cancel to item after
                        # values after are technically unallocated and thus allowed to be changed
                    if itemNum == 20: # "edge case"
                        endAddr = getAdjOffset(fileTypeData, addr["inventory"]["end"])
                        hexEdit(filename, endAddr, int.to_bytes(255, 1, 'little'))
                    else:
                        nextAddr = getAdjOffset(fileTypeData, addr["inventory"]["items"][str(itemNum+1)][0])
                        hexEdit(filename, nextAddr, int.to_bytes(255, 1, 'little'))

                # check to shrink inventory range
                lastValid = 0
                for x in range(1,21):
                    item = getAdjOffset(fileTypeData, addr["inventory"]["items"][str(x)][0])
                    inByte = int.from_bytes(hexRead(filename, item, 1), 'little')
                    if inByte != 0 and inByte != 255:
                        lastValid = x
                # change if inv is different from current total
                invTotal = int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["inventory"]["total"]), 1), byteorder='little')
                if lastValid != 20:
                    hexEdit(filename, adjTotal, int.to_bytes(lastValid, 1, 'little'))
                    nextAddr = getAdjOffset(fileTypeData, addr["inventory"]["items"][str(lastValid+1)][0])
                    hexEdit(filename, nextAddr, int.to_bytes(255, 1, 'little'))
            
            # redisplay info
            clearTerm()
            invTotal = int.from_bytes(hexRead(filename, getAdjOffset(fileTypeData, addr["inventory"]["total"]), 1), byteorder='little')
            print(f"Inventory: {invTotal}")
            for x in range(1,21):
                dispItemRow(filename, fileTypeData, x, x == invTotal)

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
def dispItemRow(filename, type, itemNum, arrow: bool) -> None:
    # get the item's hex value
    itemHex = hex(int.from_bytes(hexRead(filename, getAdjOffset(type, addr["inventory"]["items"][str(itemNum)][0]), 1), byteorder='little'))

    # get the item's quantity
    itemQuant = hex(int.from_bytes(hexRead(filename, getAdjOffset(type, addr["inventory"]["items"][str(itemNum)][1]), 1), byteorder='little'))

    # 
    itemConv = addr["convert"][str(int.from_bytes(hexRead(filename, getAdjOffset(type, addr["inventory"]["items"][str(itemNum)][0]), 1), byteorder='little'))]["item"]
    print(f"{'->' if arrow else ''}\tItem {itemNum:2}: {itemHex:4}({itemConv.title():^14}) Amount: {itemQuant:4}")

# Function to handle item to byte data for saving
def item2byte(inp) -> bytes | None:
    # try decimal
    if inp.isdigit():
        return int.to_bytes(max(min(int(inp), 255), 0), 1, byteorder='little')
    # try hex
    elif inp[:2] == "0x":
        return int.to_bytes(max(min(int(inp, 16), 255), 0), 1, byteorder='little')
    # try string to key to hex
    else:
        for key, items in addr["convert"].items():
            if items["item"] == inp:
                return int.to_bytes(int(key), 1, byteorder='little')
        print(f"Could not find item. Please refer to keyVals.json's convert for names")
    return None

# Function to handle numbers to bytedata
def int2byte(inp) -> bytes | None:
    # try decimal
    if inp.isdigit():
        return int.to_bytes(max(min(int(inp), 255), 0), 1, byteorder='little')
    # try hex
    elif inp[:2] == "0x":
        return int.to_bytes(max(min(int(inp, 16), 255), 0), 1, byteorder='little')
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