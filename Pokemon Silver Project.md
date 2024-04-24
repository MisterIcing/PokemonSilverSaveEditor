# Operating Manual
- Invocation
	- `python3 PkmnSilverEditor.py <path/to/saveFile>`
		- | Right now only `.sna` saves are functional
- Prompts:
	- `Name of file to open: `: path to save file to edit
	- General format for prompts
		- `Prompt(expected type[expected range/values])` or
		- `Prompt[expected values]`
	- Typing `back` in sub sections should return to previous section prompt
	- Typing `exit` in the main menu will exit the program
		- There is the tried and true `ctrl+c` as well

# General Gameboy
- [Opcodes](https://www.pastraiser.com/cpu/gameboy/gameboy_opcodes.html)
	- `db` seems to be the header information
		- Starts at `0x104`
		- Name of game at `0x134`
# Pokemon/Moves/Item Mappings
- Refer to [[keyVals.json]]'s convert for usable list in program
- % Visuals cap at `0x63`(99)
# RAM Locations & Values
## Positioning
- Position %% Not the best way to move around %%
	- `0xd20d`: X position %% inc right%%
	- `0xd20e`: Y position %% inc down%%
	- % Use to move player onto other character & move
- Can be used to get onto magnet train w/o repairing
## Inventory
- Items
	- `0xd5b7`: Total items
	- `Item-Amount` pairs
		- Item 1: `0xd5b8-0xd5b9`
		- Item 2: `0xd5ba-0xd5bb`
		- Item 3: `0xd5bc-0xd5bd`
		- Item 4: `0xd5be-0xd5bf`
		- Item 5: `0xd5c0-0xd5c1`
		- Item 6: `0xd5c2-0xd5c3`
		- Item 7: `0xd5c4-0xd5c5`
		- Item 8: `0xd5c6-0xd5c7`
		- Item 9: `0xd5c8-0xd5c9`
		- Item 10: `0xd5ca-0xd5cb`
		- Item 11: `0xd5cc-0xd5cd`
		- Item 12: `0xd5ce-0xd5cf`
		- Item 13: `0xd5d0-0xd5d1`
		- Item 14: `0xd5d2-0xd5d3`
		- Item 15: `0xd5d4-0xd5d5`
		- Item 16: `0xd5d6-0xd5d7`
		- Item 17: `0xd5d8-0xd5d9`
		- Item 18: `0xd5da-0xd5db`
		- Item 19: `0xd5dc-0xd5dd`
		- Item 20: `0xd5de-0xd5df`
	- `0xd5e0`: End of items %% Set 0xd5d3 to FF for cancel %%
- Key Items %% No amount of item %%
	- % 2nd offset set to 0 bc value is irrelevant
	- `0xd5e1`: Total keys
	- `0xd5e2-0xd5fa`: key items
	- `0xd5fb`: End of keys
- Pokeball inventory %% item, amount pairs %%
	- `0xd5fc`: Total balls
	- `0xd5fd-0xd5fe`: [ball 1, amount]
	- `0xd5ff-0xd614`: 11 other pairs
	- `0xd615`: End of balls 
- Stored Inventory %% item, amount pairs %%
	- `0xd616`: Total stored
	- `0xd617-0xd618`: [item 1, amount]
	- `0xd619-0xd67a`: 49 other items
	- `0xd67b`: End of Stored
## Party
- Pokemon Party
	- `0xda22`: # of pokemon [01]
	- `0xda23-0xda28`: pokemon [hex of universal number]
	- `0xda29`: end of party, just set to `0xff`
	- Pokemon 1 info [Cyndaquil]
		- `0xda2a`: Pokemon [9b]
		- `0xda2b`: Item held [ad]
		- `0xda2c-0xda2f`: Moves [21 2b 00 00]
		- `0xda30-0xda31`: ID num [05 69] %% Dont think this determines anything in Gen 2 %%
		- `0xda32-0xda34`: exp [00 00 87] %% Around 0x0f4240(1000000) %% %% Just change level to 99 and adjust from there %%
		- `0xda35-0xda36`: HP EV [00 00] 
		- `0xda37-0xda38`: Attack EV [00 00]
		- `0xda39-0xda3a`: Defense EV [00 00] 
		- `0xda3b-0xda3c`: Speed EV [00 00] 
		- `0xda3d-x0da3e`: Special EV [00 00]
		- `0xda3f`: Attack/Defense IV [6d] %% Shiny: 0x{2, 3, 6, 7, a, b, e, f}a %%
		- `0xda40`: Speed/Special IV [30] %% Shiny: 0xaa %%
		- `0xda41-0xda44`: Current PP [23 1e 00 00] %% Max at 0x39? (Supposedly a key number for max value, acts as max PP)%%
		- `0xda45`: Happiness [46]
		- `0xda46`: Pokerus [00]
			- % upper byte is strain
			- % lower byte is duration
		- `0xda47-0xda48`: Caught Data [00 00] %% Starter, so... %%
		- `0xda49`: level %% Max 0x64 %%
		- `0xda4a`: Status [00] %% Each bit acts as flag to status (?) %%
			- % `0x0da4b` is unused to my knowledge
		- `0xda4c-0xda4d`: HP [00 13] %% Visuals caps at 999 (03 e7), glitched bar when max & current are off %%
		- `0xda4e-0xda4f`: Max HP [00 13] %% See HP comments %%
		- `0xda50-0xda51`: Attack [00 0a] %% Visuals max at 999 (03 e7), random glyphs after %% 
		- `0xda52-0xda53`: Defense [00 0a] %% See Attack %%
		- `0xda54-0xda55`: Speed [00 0b] %% See Attack %%
		- `0xda56-0xda57`: Special Attack [00 0b] %% See Attack %%
		- `0xda58-0xda59`: Special Defense [00 0a] %% See Attack %%
		- & Repeat per pokemon (Pkmn 2: `0xda5a`)
	- Trainer Names %% Null terminate w/50 %%
		- `0xdb4a-0xdb51`: Pokemon 1 Trainer Name
		- `0xdb55-0xdb`: Pokemon 2 Trainer Name
		- ...
	- Pokemon Names %% Null terminate w/50 %%
		- `0xdb8c-0xdb96`: Pokemon 1 Name
		- `0xdb97-0xdba1`: Pokemon 2 Name
		- `0xdba2-0xdbac`: Pokemon 3 Name
		- `0xdbad-0xdbb7`: Pokemon 4 Name
		- `0xdbb8-0xdbc2`: Pokemon 5 Name
		- `0xdbc3-0xdbcd`: Pokemon 6 Name
## Random
- Letters
	- 80 ~> A
- Writing RAM base: `0xc000`
- Map drawing?
	- WRA0:C3A0 -> C620
- Char Sprite
	- Always in center
	- Made of 4 sprites per corner
	- C300: `4c 48 00 00 4c 50 01 00 54 48 02 00 54 50 03 00`
		- `<Ypos><Xpos><tile/sprite>`
			- TL: `4c 48 00` 
			- TR: `4c 50 01`
			- BL: `54 48 02`
			- BR: `54 50 03`
	- ? Generally not useful, will change once redrawn unless skipping function that draws sprite
	- ! Collision is own seperate value
	- Movement animations in 8800s (VRAM)
		- Stationary in 8000s
		- Background in 9000s
			- Not sure if they can be accessed for sprite values since mvnt & stat sprites take up `0xFF` spaces
- Wild Pokemon Fights
	- `0xd20b`: Non-0 value means you can get attacked
		- % Consider freezing
		- ? Not usable unless manually frozen or if you save the state & update for each step in tall grass
	- `0xd9eb`: Repel
		- % Also consider freezing bc 255 can go by quick
- Cash
	- `0xd573-0xd575`: In hand cash
	- `0xd576-0xd578`: Money stored by mom for tax purposes
		- $ and by taxes, I mean pokedolls that she buys you
	- `0xd57a-0xd57b`: Casino coins
- Badges %% Add flags to mix badges (toggle sets to 0xff or 0x00) %%
	- Johto: `0xd57c` %% Chuck & Jasmine have odd order %%
		- `0x01`: Falkner
		- `0x02`: Bugsy
		- `0x04`: Whitney
		- `0x08`: Morty
		- `0x10`: Jasmine %% Note order %%
		- `0x20`: Chuck
		- `0x40`: Pyrce
		- `0x80`: Clair
	- Kanto: `0xd57d` %% Although in Kanto & defeated Brock, ID didnt switch so assumes Soul Silver ordering %%
		- `0x01`: Brock
		- `0x02`: Misty
		- `0x04`: Lt. Surge
		- `0x08`: Erika
		- `0x10`: Janine
		- `0x20`: Sabrina
		- `0x40`: Blaine
		- `0x80`: Blue %% Viridian was empty when I went :| %%
	- | Only battles if you do not have the badge
		- Toggling the badge off allows you to repeat the fight
		- Toggling the badge on allows you to skip the battle and get the reward
- Flying %% After extensive mapping, 0xffffffff flys to everywhere %%
	- @ Have to use magnet train or boat to switch which map you can fly through
		- Soul Silver fixed this
		- Possible to also get to right path on Indigo Platau to Kanto
		- Or to Mt. Silver's Pokemon center to Johto
	- `0xd9ee-0xd9f1`: Fly locations
		- % Uses bit flags, but easier to just brute force with `0xff`
- | I keep skipping the part where I get a pokedex, so I do not know what values control the seen/captured
	- I also skip a lot of battles so Im not helping myself
# Save Manipulation Data
## Save State (SNA)
- Inventory `0xd5b7` -> `0x1b35`
	- `0x1b35`: total items
	- `0x1b36-0x1b37`: 
- Party Pokemon: `0xda22` -> `0x1fa0
	- Stats & Info
		- `0x1fa0`: Total pokemon in party
		- `0x1da8`: Pokemon 1 Stats
		- `0x1fd8`: Pokemon 2 Stats
		- `0x2008`: Pokemon 3 Stats
		- `0x2038:` Pokemon 4 Stats
		- `0x2068`: Pokemon 5 Stats
		- `0x2098`: Pokemon 6 Stats
		- & Internally continue with new base
	- Names %% Null Terminators already added to range %%
		- Trainer Names: `0xdb4a` -> `0x20c8`
			- `0x20c8-0x20cf`: Pokemon 1 Trainer Name
			- ...
		- Pokemon Names: `0xdb8c` -> `0x210a` 
			- `0x210a-0x2114`: Pokemon 1 Name
			- `0x2115-0x211f`: Pokemon 2 Name
			- `0x2120-0x212a`: Pokemon 3 Name
			- `0x212b-0x2135`: Pokemon 4 Name
			- `0x2136-0x2140`: Pokemon 5 Name
			- `0x2141-0x214b`: Pokemon 6 Name
- | Since this is a save state of the RAM, rebase RAM addresses from earlier w/
	- `(offset - 0xc000) + (hexFind(filename, "WRAM")+0x9)`
	- where offset is the RAM location
	- The hex find will adjusts for varying ROM name sizes
## Save File (SAV)
- Player Name: `0x1210-0x1217`
- Pokemon 1 Name: `0x1250-0x125c`
- @ Future