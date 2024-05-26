#-------------------------------------------------
doc:
  Struct for Pokemon Silver Save File
meta:
  id: saves
  file-extension: sav
  endian: be # GB is big endian
#-------------------------------------------------
# Define custom type
types:
  bag:
    params:
      - id: bag_size  # parameter for the size of bag
        type: u4
    seq:
      - id: total # total items in bag
        type: u1
      - id: used_slots # Items covered in total
        type: item
        repeat: expr
        repeat-expr: total
      - id: remaining_slots # Items not covered in total / should be ? and cancel
        type: item
        repeat: expr
        repeat-expr: bag_size - total
      - id: end # final item location for cancel
        type: u1

  one_bag: # Special bag for item or amount
    params:
      - id: bag_size
        type: u4
      - id: bag_type
        type: u1
    seq:
      - id: total
        type: u1
      - id: item_slots # If bag only uses items
        type: u1
        repeat: expr
        repeat-expr: bag_size
        enum: item_names
        if: bag_type == 0
      - id: amount_slots # If bag only uses amounts
        type: u1
        repeat: expr
        repeat-expr: bag_size
        if: bag_type != 0
      - id: end
        type: u1
      
  item: # define item type
    seq:
      - id: item # u1 item identifier
        type: u1
        enum: item_names
      - id: amount # u1 item amount
        type: u1
  
  party: # define party struct
    seq:
      - id: active_size
        type: u1
      - id: party
        type: u1
        repeat: expr
        repeat-expr: 6
        enum: pokemon_names
      - id: end_list
        type: u1
      - id: party_stats
        type: stats
        repeat: expr
        repeat-expr: 6
      - id: trainer_names
        type: str
        # eventually add encoding
        encoding: utf-8
        size: 11
        repeat: expr
        repeat-expr: 6
      - id: party_names
        # eventually add encoding
        type: str
        encoding: utf-8
        size: 11
        repeat: expr
        repeat-expr: 6
      
  stats:
    seq:
      - id: pokemon
        type: u1
        enum: pokemon_names
      - id: item
        type: u1
        enum: item_names
      - id: moves
        type: u1
        repeat: expr
        repeat-expr: 4
        enum: move_names
      - id: id_num
        type: u2
      - id: exp
        type: u3("be")
      - id: hp_ev
        type: u2
      - id: attack_ev
        type: u2
      - id: defense_ev
        type: u2
      - id: speed_ev
        type: u2
      - id: special_ev
        type: u2
      - id: attack_defense_iv
        type: u1
      - id: speed_special_iv
        type: u1
      - id: pp
        type: u1
        repeat: expr
        repeat-expr: 4
      - id: mood
        type: u1
      - id: pokerus
        type: u1 # maybe add value
      - id: caught_data
        type: u2 # idk what this converts to
      - id: level
        type: u1
      - id: status
        type: u1
      - id: unused
        type: u1
      - id: hp
        type: u2
      - id: max_hp
        type: u2
      - id: attack
        type: u2
      - id: defnse
        type: u2
      - id: speed
        type: u2
      - id: special_attack
        type: u2
      - id: special_defense
        type: u2

  u3: # needed for exp & the like
    params: # evenntuall use root?
      - id: endianess
        type: str
    seq:
      - id: b1
        type: u1
      - id: b2
        type: u1
      - id: b3
        type: u1
    instances:
      value:
        value: endianess == 'be' ? (b1 << 16) | (b2 << 8) | (b3) : (b3 << 16) | (b2 << 8) | (b1)

  unknown: # variably sized unknown area
    params:
      - id: unksize
        type: u8
    seq:
      - id: byte
        type: u1
        repeat: expr
        repeat-expr: unksize
#-------------------------------------------------
# Sequence of fields in struct
seq:
  # - id: xc3a0_xc4a3
  #   type: unknown(0x104)
  # - id: unknown
  #   type: unknown(0xa)
  
  - id: unknown
    type: unknown(0xcb1)
    
    #0xcb1
  - id: items_bag  # main inventory
    type: bag(0x14)
    #0xcda
    
    #0xcdb
  - id: key_bag # key items, no amount val
    type: one_bag(0x19, 0)
    #0xcf5
    
    #0xcf6
  - id: balls_bag # pokeball inventory
    type: bag(0xc)
    #0xd0f
    
    #0xd10
  - id: stored_bag # PC inventory
    type: bag(0x32)
    #0xd75
    
  - id: unknown2 # unknown area
    type: unknown(0x372)
    
    #0x10e8
  - id: party
    type: party
    #0x1293
  
  # - id: unknown3
  #   type: u1
  #   repeat: eos
#-------------------------------------------------
# Enums to label items hopefully
enums:
  one_type:
    0: item
    1: amount
  item_names:
    0: none
    1: master_ball
    2: ultra_ball
    3: bright_powder
    4: great_ball
    5: poke_ball
    6: teru_sama_0
    7: bicycle
    8: moon_stone
    9: antidote
    10: burn_heal
    11: ice_heal
    12: awakening
    13: paralyze_heal
    14: full_restore
    15: max_potion
    16: hyper_potion
    17: super_potion
    18: potion
    19: escape_rope
    20: repel
    21: max_elixer
    22: fire_stone
    23: thunder_stone
    24: water_stone
    25: teru_sama_1
    26: hp_up
    27: protein
    28: iron
    29: carbos
    30: lucky_punch
    31: calcium
    32: rare_candy
    33: x_accuracy
    34: leaf_stone
    35: metal_powder
    36: nugget
    37: poke_doll
    38: full_heal
    39: revive
    40: max_revive
    41: guard_spec
    42: super_repel
    43: max_repel
    44: dire_hit
    45: teru_sama_2
    46: fresh_water
    47: soda_pop
    48: lemonade
    49: x_attack
    50: teru_sama_3
    51: x_defend
    52: x_speed
    53: x_special
    54: coin_case
    55: item_finder
    56: teru_sama_4
    57: exp_share
    58: old_rod
    59: good_rod
    60: silver_leaf
    61: super_rod
    62: pp_up
    63: ether
    64: max_ether
    65: elixer
    66: red_scale
    67: secret_potion
    68: ss_ticket
    69: mystery_egg
    70: teru_sama_5
    71: silver_wing
    72: moomoo_milk
    73: quick_claw
    74: psncureberry
    75: gold_leaf
    76: soft_sand
    77: sharp_beak
    78: przcureberry
    79: burnt_berry
    80: ice_berry
    81: poison_barb
    82: kings_rock
    83: bitter_berry
    84: mint_berry
    85: red_apricorn
    86: tiny_mushroom
    87: big_mushroom
    88: silver_powder
    89: blu_apricorn
    90: teru_sama_6
    91: amulet_coin
    92: ylw_apricorn
    93: grn_apricorn
    94: cleanse_tag
    95: mystic_water
    96: twisted_spoon
    97: wht_apricorn
    98: blackbelt
    99: blk_apricorn
    100: teru_sama_7
    101: pnk_apricorn
    102: blackglasses
    103: slowpoke_tail
    104: pink_bow
    105: stick
    106: smoke_ball
    107: never_melt_ice
    108: magnet
    109: miracle_berry
    110: pearl
    111: big_pearl
    112: everstone
    113: spell_tag
    114: rage_candy_bar
    115: teru_sama_8
    116: teru_sama_9
    117: miracle_seed
    118: thick_club
    119: focus_band
    120: teru_sama_10
    121: energy_powder
    122: energy_root
    123: heal_powder
    124: revival_herb
    125: hard_stone
    126: lucky_egg
    127: card_key
    128: machine_part
    129: teru_sama_11
    130: lost_item
    131: stardust
    132: star_piece
    133: basement_key
    134: pass
    135: teru_sama_12
    136: teru_sama_13
    137: teru_sama_14
    138: charcoal
    139: berry_juice
    140: scope_lens
    141: teru_sama_15
    142: teru_sama_16
    143: metal_coat
    144: dragon_fang
    145: teru_sama_17
    146: leftovers
    147: teru_sama_18
    148: teru_sama_19
    149: teru_sama_20
    150: mystery_berry
    151: dragon_scale
    152: berserk_gene
    153: teru_sama_21
    154: teru_sama_22
    155: teru_sama_23
    156: sacred_ash
    157: heavy_ball
    158: flower_mail
    159: level_ball
    160: lure_ball
    161: fast_ball
    162: teru_sama_24
    163: light_ball
    164: friend_ball
    165: moon_ball
    166: love_ball
    167: normal_box
    168: gorgeous_box
    169: sun_stone
    170: polkadot_bow
    171: teru_sama_25
    172: up_grade
    173: berry
    174: gold_berry
    175: squirt_bottle
    176: teru_sama_26
    177: park_ball
    178: rainbow_wing
    179: teru_sama_27
    180: brick_piece
    181: surf_mail
    182: lite_blue_mail
    183: portrait_mail
    184: lovely_mail
    185: eon_mail
    186: morph_mail
    187: blue_sky_mail
    188: music_mail
    189: mirage_mail
    190: teru_sama_28
    191: tm01
    192: tm02
    193: tm03
    194: tm04
    195: tm04_dup
    196: tm05
    197: tm06
    198: tm07
    199: tm08
    200: tm09
    201: tm10
    202: tm11
    203: tm12
    204: tm13
    205: tm14
    206: tm15
    207: tm16
    208: tm17
    209: tm18
    210: tm19
    211: tm20
    212: tm21
    213: tm22
    214: tm23
    215: tm24
    216: tm25
    217: tm26
    218: tm27
    219: tm28
    220: tm28_dup
    221: tm29
    222: tm30
    223: tm31
    224: tm32
    225: tm33
    226: tm34
    227: tm35
    228: tm36
    229: tm37
    230: tm38
    231: tm39
    232: tm40
    233: tm41
    234: tm42
    235: tm43
    236: tm44
    237: tm45
    238: tm46
    239: tm47
    240: tm48
    241: tm49
    242: tm50
    243: hm01
    244: hm02
    245: hm03
    246: hm04
    247: hm05
    248: hm06
    249: hm07
    250: hm08
    251: hm09
    252: hm10
    253: hm11
    254: hm12
    255: cancel
  pokemon_names:
    0: none
    1: bulbasaur
    2: ivysaur
    3: venusaur
    4: charmander
    5: charmeleon
    6: charizard
    7: squirtle
    8: wartortle
    9: blastoise
    10: caterpie
    11: metapod
    12: butterfree
    13: weedle
    14: kakuna
    15: beedrill
    16: pidgey
    17: pidgeotto
    18: pidgeot
    19: rattata
    20: raticate
    21: spearow
    22: fearow
    23: ekans
    24: arbok
    25: pikachu
    26: raichu
    27: sandshrew
    28: sandslash
    29: nidoranf
    30: nidorina
    31: nidoqueen
    32: nidoranm
    33: nidorino
    34: nidoking
    35: clefairy
    36: clefable
    37: vulpix
    38: ninetails
    39: jigglypuff
    40: wigglytuff
    41: zubat
    42: golbat
    43: oddish
    44: gloom
    45: vileplume
    46: paras
    47: parasect
    48: venonat
    49: venomoth
    50: diglett
    51: dugtrio
    52: meowth
    53: persian
    54: psyduck
    55: golduck
    56: mankey
    57: primeape
    58: growlithe
    59: arcanine
    60: poliwag
    61: poliwhirl
    62: poliwrath
    63: abra
    64: kadabra
    65: alakazam
    66: machop
    67: machoke
    68: machamp
    69: bellsprout
    70: weepinbell
    71: victreebel
    72: tentacool
    73: tentacruel
    74: geodude
    75: gravler
    76: golem
    77: ponyta
    78: rapidash
    79: slowpoke
    80: slowbro
    81: magnemite
    82: magnetron
    83: farfetchd
    84: doduo
    85: dodrio
    86: seel
    87: dewgong
    88: grimer
    89: muk
    90: shellder
    91: cloyster
    92: gastly
    93: haunter
    94: gengar
    95: onix
    96: drowzee
    97: hypno
    98: krabby
    99: kingler
    100: voltorb
    101: electrode
    102: exeggcute
    103: exeggutor
    104: cubone
    105: marowak
    106: hitmonlee
    107: hitmonchan
    108: lickitung
    109: koffing
    110: weezing
    111: rhyhorn
    112: rhydon
    113: chansey
    114: tangela
    115: kangaskhan
    116: horsea
    117: seadra
    118: goldeen
    119: seaking
    120: staryu
    121: starmie
    122: mr_mime
    123: scyther
    124: jynx
    125: electabuzz
    126: magmar
    127: pinsir
    128: tauros
    129: magikarp
    130: gyrados
    131: lapras
    132: ditto
    133: eevee
    134: vaporeon
    135: jolteon
    136: flareon
    137: porygon
    138: omanyte
    139: omastar
    140: kabuto
    141: kabutops
    142: aerodactyl
    143: snorlax
    144: articuno
    145: zapdos
    146: moltres
    147: dratini
    148: dragonair
    149: dragonite
    150: mewtwo
    151: mew
    152: chikorita
    153: bayleef
    154: maganium
    155: cyndaquil
    156: quilava
    157: typhlosion
    158: totadile
    159: croconaw
    160: feraligatr
    161: sentret
    162: furret
    163: hoothoot
    164: noctowl
    165: ledyba
    166: ledian
    167: spinarak
    168: ariados
    169: crobat
    170: chincou
    171: lanturn
    172: pichu
    173: cleffa
    174: igglybuff
    175: togepi
    176: togetic
    177: natu
    178: xatu
    179: mareep
    180: flaaffy
    181: ampharos
    182: bellossom
    183: marill
    184: azumarill
    185: sudowoodo
    186: politoed
    187: hoppip
    188: skiploom
    189: jumpluff
    190: aipom
    191: subkern
    192: sunflora
    193: yanma
    194: wooper
    195: quagsire
    196: espeon
    197: umbreon
    198: murkrow
    199: slowking
    200: misdreavux
    201: unown
    202: wobbuffet
    203: girafarig
    204: pineco
    205: forretress
    206: dunesparce
    207: gligar
    208: steelix
    209: snubbull
    210: granbull
    211: qwilfish
    212: scizor
    213: shuckle
    214: heracross
    215: sneasel
    216: teddiursa
    217: ursaring
    218: slugma
    219: magcargo
    220: swinub
    221: piloswine
    222: corsola
    223: remoraid
    224: octillery
    225: delibird
    226: mantine
    227: skarmory
    228: houndour
    229: houndoom
    230: kingdra
    231: phanpy
    232: donphan
    233: porygon2
    234: stantler
    235: smeargle
    236: tyrogue
    237: hitmontop
    238: smoochum
    239: elekid
    240: magby
    241: miltank
    242: blissey
    243: raikou
    244: entei
    245: suicune
    246: larvitar
    247: pupitar
    248: tyranitar
    249: lugia
    250: ho_oh
    251: celebi
    252: qmark_0
    253: egg
    254: qmark_1
    255: qmark_2
  move_names:
    0: none
    1: pound
    2: karate_chop
    3: doubleslap
    4: comet_punch
    5: mega_punch
    6: pay_day
    7: fire_punch
    8: ice_punch
    9: thunder_punch
    10: scratch
    11: vicegrip
    12: guillotine
    13: razor_wind
    14: sword_dance
    15: cut
    16: gust
    17: wing_attack
    18: whirlwind
    19: fly
    20: bind
    21: slam
    22: vine_whip
    23: stomp
    24: double_kick
    25: mega_kick
    26: jump_kick
    27: rolling_kick
    28: sand_attack
    29: headbutt
    30: horn_attack
    31: fury_attack
    32: horn_drill
    33: tackle
    34: body_slam
    35: wrap
    36: take_down
    37: thrash
    38: double_edge
    39: tail_whip
    40: poison_sting
    41: twineedle
    42: pin_missile
    43: leer
    44: bite
    45: growl
    46: roar
    47: sing
    48: supersonic
    49: sonicboom
    50: disable
    51: acid
    52: ember
    53: flamethrower
    54: mist
    55: water_gun
    56: hydro_pump
    57: surf
    58: ice_beam
    59: blizzard
    60: psybeam
    61: bubblebeam
    62: aurora_beam
    63: hyper_beam
    64: peck
    65: drill_peck
    66: submission
    67: low_kick
    68: counter
    69: seismic_toss
    70: strength
    71: absorb
    72: mega_drain
    73: leech_seed
    74: growth
    75: razor_leaf
    76: solar_beam
    77: poison_powder
    78: stun_spore
    79: sleep_powder
    80: petal_dance
    81: string_shot
    82: dragon_rage
    83: fire_spin
    84: thundershock
    85: thunderbolt
    86: thunder_wave
    87: thunder
    88: rock_throw
    89: earthquake
    90: fissure
    91: dig
    92: toxic
    93: confusion
    94: psychic
    95: hypnosis
    96: meditate
    97: agility
    98: quick_attack
    99: rage
    100: teleport
    101: night_shade
    102: mimic
    103: screech
    104: double_team
    105: recover
    106: harden
    107: minimize
    108: smokescreen
    109: confuse_ray
    110: withdraw
    111: defense_curl
    112: barrier
    113: light_screen
    114: haze
    115: reflect
    116: focus_energy
    117: bide
    118: metronome
    119: mirror_move
    120: selfdestruct
    121: egg_bomb
    122: lick
    123: smog
    124: sludge
    125: bone_club
    126: fire_blast
    127: waterfall
    128: clamp
    129: swift
    130: skull_bash
    131: spike_cannon
    132: constrict
    133: amnesia
    134: kinesis
    135: softboiled
    136: hi_jump_kick
    137: glare
    138: dream_eater
    139: poison_gas
    140: barrage
    141: leech_life
    142: lovely_kiss
    143: sky_attack
    144: transform
    145: bubble
    146: dizzy_punch
    147: spore
    148: flash
    149: psywave
    150: splash
    151: acid_armor
    152: crabhammer
    153: explosion
    154: fury_swipes
    155: bonemerang
    156: rest
    157: rock_slide
    158: hyper_fang
    159: sharpen
    160: conversion
    161: tri_attack
    162: super_fang
    163: slash
    164: substitute
    165: struggle
    166: sketch
    167: triple_kick
    168: thief
    169: spider_web
    170: mind_reader
    171: nightmare
    172: flame_wheel
    173: snore
    174: curse
    175: flail
    176: conversion2
    177: aeroblast
    178: cotton_spore
    179: reversal
    180: spite
    181: powder_snow
    182: protect
    183: mach_punch
    184: scary_face
    185: faint_attack
    186: sweet_kiss
    187: belly_drum
    188: sludge_bomb
    189: mud_slap
    190: octazooka
    191: spikes
    192: zap_cannon
    193: foresight
    194: destiny_bond
    195: perish_song
    196: icy_wind
    197: detect
    198: bone_rush
    199: lock_on
    200: outrage
    201: sandstorm
    202: giga_drain
    203: endure
    204: charm
    205: rollout
    206: false_swipe
    207: swagger
    208: milk_drink
    209: spark
    210: fury_cutter
    211: steel_wing
    212: mean_look
    213: attract
    214: sleep_talk
    215: heal_bell
    216: return
    217: present
    218: frustration
    219: safeguard
    220: pain_split
    221: sacred_fire
    222: magnitude
    223: dynamic_punch
    224: megahorn
    225: dragonbreath
    226: baton_pass
    227: encore
    228: pursuit
    229: rapid_spin
    230: sweet_scent
    231: iron_tail
    232: metal_claw
    233: vital_throw
    234: morning_sun
    235: synthesis
    236: moonlight
    237: hidden_power
    238: cross_chop
    239: twister
    240: rain_dance
    241: sunny_day
    242: crunch
    243: mirror_coat
    244: psych_up
    245: extremespeed
    246: ancient_power
    247: shadow_ball
    248: future_sight
    249: rock_smash
    250: whirlpool
    251: beat_up
    252: blank
    253: a999zaa
    254: glitch
    255: glitch_2
    