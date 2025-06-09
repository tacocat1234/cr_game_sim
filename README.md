# cr_game_sim
download python package from software center
run run_me.bat
if on school computer, move or diable the taskbar or the elxiir bar wont fit on screen
modify deck.txt to set deck. type in lowercase.
modify bot_deck.txt to set bot_deck
format is 
{cardname} {level}
random format is
random {level} for a entirely random deck with level = level
random.{type}.{min elixir}-{max elixir} {level}
type = spell, troop, building
to indicate evolution, type "evolution" before
bot automatically uses all evolutions possible, and there is no evolution limit (but its very op (but also fun) if you have more than 2)

examples:
"firecracker 11" is a level 11 firecracker
"evolution skeletons 11" is a level 11 skeletons, which can evolve
"random.building.3-7 11" is a random building from 3-7 elixir, at level 11
"random.spell.4-4 200" is a random spell with 4 elxir, at level 200
"random 13" randomizes the entire deck according to an algorithim, where every card is level 13

recommended bot_deck.txt levels is 13 comapred to your 11, becuase bot is stupid.

special note:
only evos are:
knight, archers, musketeer, archers, skeletons, bomber.
more coming soon

## Troops
Implemented troops include:

knight, minipekka, giant, minions, archers, musketeer, 
speargoblins, goblins, 
skeletons, bomber, valkyrie, 
barbarians, megaminion, battleram, 
firespirit, electrospirit, skeletondragons, wizard, 
bats, hogrider, flyingmachine, 
skeletonarmy, guards, babydragon, witch, pekka, 
darkprince, royalhogs, balloon, prince, royalgiant, royalrecruits, threemusketeers, 
icespirit, icegolem, battlehealer, giantskeleton, 
beserker, goblingang, dartgoblin, skeletonbarrel, goblingiant, 
zappies, hunter, minionhorde, elitebarbarians, golem, 
miner, princess, electrowizard, infernodragon, sparky, megaknight
wallbreakers, royalghost, icewizard, firecracker, phoenix, electrodragon
healspirit, suspiciousbush, bandit, magicarcher, bowler, rascals, electrogiant, lavahound,
elixirgolem, lumberjack, nightwitch, executioner,
fisherman, motherwitch, cannoncart
## Spells
Implemented spells include:

fireball, arrows, 
zap, rocket, 
goblinbarrel, 
giantsnowball, freeze, lightning, 
poison, barbarianbarrel,
log,
earthquake, graveyard,
rage, goblincurse, royaldelivery,
void, clone, tornado
## Buildings
Implemented buildings include:

goblinhut, goblincage, 
tombstone, 
cannon, 
bombtower, infernotower, 
mortar, 
barbarianhut, 
furnace, tesla, xbow,
goblindrill,
elixirpump
## Towers
kingtower, princesstower, cannoneer, daggerduchess