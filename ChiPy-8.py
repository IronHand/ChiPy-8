#Chip-8 Python Interpreter by Iron Hand
#--------------------------------------


import pygame, sys
import pygame.locals
import pygame.gfxdraw
import tkFileDialog
import random

pygame.init()
mainClock = pygame.time.Clock()

random.seed()

#Global Emulator Variables
#if pause == 1 stop to interprete the RAM
emu_pause = 0
RAM_offset = 0x200
#Size of the loaded ROM in HEX (Bytes)
ROM_leng = 0
#Size of one Pixel 
pixel_size = 10
#Fill Pixels 0 = Fullfill, >0 = Wiredsize of pixels / MUST 1 if pixel_size < 2
pixel_fill = 0
#Speed of the Emulation defaul 400
MainClockSpeed = 400
#Debugg Switch
debugger_on = False

#Main Windows Options, calculate windows size from pixel size
WINDOWWIDTH = 64*pixel_size
WINDOWHEIGHT = 32*pixel_size
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
pygame.display.set_caption('Chyp-8')

#Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

if len(sys.argv) > 1:
	if sys.argv[1] == "-d":
		debugger_on = True
	
#Chip-8 has 16 general purpose 8-bit registers V0-VF
#The VF register is used as a flag by some instructions. It should not be used by any programm when used as flag.
Vx = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
#There is also a 16-bit register called I. 
#This register is generally used to store memory addresses, so only the lowest (rightmost) 12 bits are usually used.
VI = 0
#Chip-8 also has two special purpose 8-bit registers, for the delay and sound timers. When these registers are non-zero, they are automatically decremented at a rate of 60Hz

#The delay timer is active whenever the delay timer register (DT) is non-zero. This timer does nothing more than subtract 1 from the value of DT at a rate of 60Hz. When DT reaches 0, it deactivates.
DT = 0
#The sound timer is active whenever the sound timer register (ST) is non-zero. This timer also decrements at a rate of 60Hz, however, as long as ST's value is greater than zero, the Chip-8 buzzer will sound. When ST reaches zero, the sound timer deactivates.
ST = 0

#There are also some "pseudo-registers" which are not accessable from Chip-8 programs. The program counter (PC) should be 16-bit, and is used to store the currently executing address. 
PC = RAM_offset #Programs start at Adress 0x200
#The stack pointer (SP) can be 8-bit, it is used to point to the topmost level of the stack.
SP = 0
#The stack is an array of 16 16-bit values, used to store the address that the interpreter shoud return to when finished with a subroutine. Chip-8 allows for up to 16 levels of nested subroutines.
STACK = []

#The Chip-8 language is capable of accessing up to 4KB (4,096 bytes) of RAM, from location 0x000 (0) to 0xFFF (4095). The first 512 bytes, from 0x000 to 0x1FF, are where the original interpreter was located, and should not be used by programs.

#Most Chip-8 programs start at location 0x200 (512), but some begin at 0x600 (1536). Programs beginning at 0x600 are intended for the ETI 660 computer.

RAM = []
RAM.extend(["00"] * RAM_offset)

#0
RAM[0] = "f0"
RAM[1] = "90"
RAM[2] = "90"
RAM[3] = "90"
RAM[4] = "f0"
#1
RAM[5] = "20"
RAM[6] = "60"
RAM[7] = "20"
RAM[8] = "20"
RAM[9] = "70"
#2
RAM[10] = "f0"
RAM[11] = "10"
RAM[12] = "f0"
RAM[13] = "80"
RAM[14] = "f0"
#3
RAM[15] = "f0"
RAM[16] = "10"
RAM[17] = "f0"
RAM[18] = "10"
RAM[19] = "f0"
#4
RAM[20] = "90"
RAM[21] = "90"
RAM[22] = "f0"
RAM[23] = "10"
RAM[24] = "10"
#5
RAM[25] = "f0"
RAM[26] = "80"
RAM[27] = "F0"
RAM[28] = "10"
RAM[29] = "f0"
#6
RAM[30] = "f0"
RAM[31] = "80"
RAM[32] = "f0"
RAM[33] = "90"
RAM[34] = "f0"
#7
RAM[35] = "f0"
RAM[36] = "10"
RAM[37] = "20"
RAM[38] = "40"
RAM[39] = "40"
#8
RAM[40] = "f0"
RAM[41] = "90"
RAM[42] = "f0"
RAM[43] = "90"
RAM[44] = "f0"
#9
RAM[45] = "f0"
RAM[46] = "90"
RAM[47] = "f0"
RAM[48] = "10"
RAM[49] = "f0"
#A
RAM[50] = "f0"
RAM[51] = "90"
RAM[52] = "f0"
RAM[53] = "90"
RAM[54] = "90"
#B
RAM[55] = "e0"
RAM[56] = "90"
RAM[57] = "e0"
RAM[58] = "90"
RAM[59] = "e0"
#C
RAM[60] = "f0"
RAM[61] = "80"
RAM[62] = "80"
RAM[63] = "80"
RAM[64] = "f0"
#D
RAM[65] = "e0"
RAM[66] = "90"
RAM[67] = "90"
RAM[68] = "90"
RAM[69] = "e0"
#E
RAM[70] = "f0"
RAM[71] = "80"
RAM[72] = "f0"
RAM[73] = "80"
RAM[74] = "f0"
#F
RAM[75] = "f0"
RAM[76] = "80"
RAM[77] = "f0"
RAM[78] = "80"
RAM[79] = "80"

#Display
#The original implementation of the Chip-8 language used a 64x32-pixel monochrome display with this format
DISPLAY = []
for i in range(0,64,1):
	DISPLAY.append([])
	for j in range(0,32,1):
		DISPLAY[i].append(0)
DISPLAY_DIFF = []

#Print all Debug Data
def debug_out(format):
	
	print 
	
	if format == "dez":
		print "GP Registers:"
		for x in range(0, 16, 1):
			print "V" + str(hex(x)) + ":", Vx[x]
		print "Special Registers:"
		print "VI:", VI
		print "DT:", DT
		print "ST:", ST
		print "Pseudo Registers:"
		print "PC:", PC
		print "SP:", SP
	
	elif format == "hex":
		print "GP Registers:"
		for x in range(0, 16, 1):
			print "V" + str(hex(x)) + ":", hex(Vx[x])
		print "Special Registers:"
		print "VI:", hex(VI)
		print "DT:", hex(DT)
		print "ST:", hex(ST)
		print "Pseudo Registers:"
		print "PC:", hex(PC)
		print "SP:",hex(SP)
		
	print "Others:"
	print "ROM Leng:", hex(ROM_leng), " <=> ", ROM_leng, " Bytes"
	print "Stack:"
	for e in STACK:
		print hex(e)
	try:
		print "Aktual RAM Data", RAM[PC], RAM[PC+1]
	except:
		print "Aktual RAM Data", RAM[PC-1]

#print the RAM Data
def ram_out():
	print RAM
	
#Load a ROM File into the RAM
def load_rom(rom_path):
	global RAM, ROM_leng
	
	#RAM = []
	#RAM.extend(["00"] * RAM_offset)

	rom = open(rom_path, "rb")
	rom_data = rom.read()
	ROM_leng = len(rom_data)
	for d in range(0,len(rom_data),1):
		h = rom_data[d].encode("hex")
		#h1 = rom_data[d+1].encode("hex")
		RAM.append(h)
		
	RAM.extend(["00"] * (4096 - len(RAM)))

def reset_emulator():	
	global DISPLAY, STACK, PC, Vx, VI, DT, ST, SP
	
	for i in range(0,64,1):
		for j in range(0,32,1):
			DISPLAY[i][j] = 0
		windowSurface.fill(BLACK)
		Vx = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
		VI = 0
		DT = 0
		ST = 0
		SP = 0
		STACK = []
		PC = RAM_offset
		
#load_rom("15 Puzzles")
load_rom("ROMs//GUESS")
	
keydown = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

#Game Loop
while True:
		
	for event in pygame.event.get():
		#Quit Event
		if event.type == pygame.locals.QUIT:
			pygame.quit()
			sys.exit()
		if event.type == pygame.locals.KEYDOWN:
			#print event.key
			if event.key == 27:
				pygame.quit()
				sys.exit()
			if event.key == ord('d') and debugger_on == False:
				debug_out("hex")
				debugger_on = True
				
			elif event.key == ord('d') and debugger_on == True:
				debugger_on = False
			if event.key == ord('p') and emu_pause == 0:
				emu_pause = 1
			elif event.key == ord('p') and emu_pause == 1:
				emu_pause = 0
			#Reset
			if event.key == 283:
				reset_emulator()
			if event.key == 284:
				filename = tkFileDialog.askopenfilename()
				print filename
			
			if event.key == 256:
				keydown[0] = 1
			if event.key == 257:
				keydown[7] = 1
			if event.key == 258:
				keydown[8] = 1
			if event.key == 259:
				keydown[9] = 1
			if event.key == 260:
				keydown[4] = 1
			if event.key == 261:
				keydown[5] = 1
			if event.key == 262:
				keydown[6] = 1
			if event.key == 263:
				keydown[1] = 1
			if event.key == 264:
				keydown[2] = 1
			if event.key == 265:
				keydown[3] = 1
			if event.key == 267:
				keydown[10] = 1
			if event.key == 268:
				keydown[11] = 1
			if event.key == 269:
				keydown[12] = 1
			if event.key == 270:
				keydown[13] = 1
			if event.key == 271:
				keydown[14] = 1
			if event.key == 266:
				keydown[15] = 1
					
		if event.type == pygame.locals.KEYUP:
			if event.key == 256:
				keydown[0] = 0
			if event.key == 257:
				keydown[7] = 0
			if event.key == 258:
				keydown[8] = 0
			if event.key == 259:
				keydown[9] = 0
			if event.key == 260:
				keydown[4] = 0
			if event.key == 261:
				keydown[5] = 0
			if event.key == 262:
				keydown[6] = 0
			if event.key == 263:
				keydown[1] = 0
			if event.key == 264:
				keydown[2] = 0
			if event.key == 265:
				keydown[3] = 0
			if event.key == 267:
				keydown[10] = 0
			if event.key == 268:
				keydown[11] = 0
			if event.key == 269:
				keydown[12] = 0
			if event.key == 270:
				keydown[13] = 0
			if event.key == 271:
				keydown[14] = 0
			if event.key == 266:
				keydown[15] = 0
	
	#Debugger
	if debugger_on == True:
		debug_out("hex")
		debugger_input = raw_input(hex(PC))
		if debugger_input == "exit":
			pygame.quit()
			sys.exit()
		elif debugger_input == "dd":
			debug_out("dez")
		elif debugger_input == "dh":
			debug_out("hex")
		elif debugger_input == "ram":
			ram_out()
		elif debugger_input == "run":
			debugger_on = False
			
	#--------------------------------------------------------------------------------------------------------------	
	#Read next Byte from RAM and interprete
	if (PC < ROM_leng+RAM_offset) and (emu_pause == 0):
		
		DISPLAY_DIFF = []
		#next command at adress PC
		next_command_start = RAM[PC]
		#High and Low byte of this command
		high_b = RAM[PC]
		low_b = RAM[PC+1]
		
		#0XXX 
		if high_b[0] == "0" and high_b[1] == "0":
			#00E0 - CLS : Clear the display.
			if low_b == "e0":
				for i in range(0,64,1):
					for j in range(0,32,1):
						DISPLAY[i][j] = 0
				windowSurface.fill(BLACK)
			#00EE - RET : Return from a subroutine. The interpreter sets the program counter to the address at the top of the stack, then subtracts 1 from the stack pointer.
			elif low_b == "ee":
				if SP > 0:
					PC = STACK[SP-1]
					del STACK[len(STACK)-1]
					SP -= 1
				else:
					pass
					#Error Message
		#elif high_b[0] == "0" and high_b[1] != "0":
			#pass
				#0nnn - SYS addr
				#Jump to a machine code routine at nnn.

				#This instruction is only used on the old computers on which Chip-8 was originally implemented. It is ignored by modern interpreters.
		
		#1nnn - JP addr : Jump to location nnn. The interpreter sets the program counter to nnn.		
		elif high_b[0] == "1":
			PC = int(high_b[1]+low_b, 16)-2
		
		#2nnn - CALL addr : Call subroutine at nnn. The interpreter increments the stack pointer, then puts the current PC on the top of the stack. The PC is then set to nnn.
		elif high_b[0] == "2":
			SP += 1
			STACK.append(PC)
			PC = int(high_b[1]+low_b, 16)-2
			
		#3xkk - SE Vx, byte : Skip next instruction if Vx = kk. The interpreter compares register Vx to kk, and if they are equal, increments the program counter by 2.
		elif high_b[0] == "3":
			regnr = int(high_b[1], 16)
			if Vx[regnr] == int(low_b, 16):
				PC += 2
				
		#4xkk - SNE Vx, byte : Skip next instruction if Vx != kk. The interpreter compares register Vx to kk, and if they are not equal, increments the program counter by 2.
		elif high_b[0] == "4":
			regnr = int(high_b[1], 16)
			if Vx[regnr] != int(low_b, 16):
				PC += 2
				
		#5xy0 - SE Vx, Vy : Skip next instruction if Vx = Vy. The interpreter compares register Vx to register Vy, and if they are equal, increments the program counter by 2.
		elif high_b[0] == "5":
			regnr_x = int(high_b[1], 16)
			regnr_y = int(low_b[0], 16)
			if Vx[regnr_x] == Vx[regnr_y]:
				PC += 2
		
		#6xkk - LD Vx, byte : Set Vx = kk. The interpreter puts the value kk into register Vx.
		elif high_b[0] == "6":
			regnr = int(high_b[1], 16)
			Vx[regnr] = int(low_b, 16)
		
		#7xkk - ADD Vx, byte : Set Vx = Vx + kk. Adds the value kk to the value of register Vx, then stores the result in Vx. 		
		elif high_b[0] == "7":
			regnr = int(high_b[1], 16)
			Vx[regnr] += int(low_b, 16)
			Vx[regnr] &= 0xff
			#while Vx[regnr] > 255:
				#Vx[regnr] -= 256
			
		#8xxx - Bitewise Logic Operations
		elif high_b[0] == "8":
			regnr_x = int(high_b[1], 16)
			regnr_y = int(low_b[0], 16)
			#8xy0 - LD Vx, Vy : Set Vx = Vy. Stores the value of register Vy in register Vx.
			if low_b[1] == "0":	
				Vx[regnr_x] = Vx[regnr_y]
			
			#8xy1 - OR Vx, Vy:Set Vx = Vx OR Vy. Performs a bitwise OR on the values of Vx and Vy, then stores the result in Vx. A bitwise OR compares the corrseponding bits from two values, and if either bit is 1, then the same bit in the result is also 1. Otherwise, it is 0. 
			if low_b[1] == "1":
				Vx[regnr_x] |= Vx[regnr_y]
			
			#8xy2 - AND Vx, Vy : Set Vx = Vx AND Vy. Performs a bitwise AND on the values of Vx and Vy, then stores the result in Vx. A bitwise AND compares the corrseponding bits from two values, and if both bits are 1, then the same bit in the result is also 1. Otherwise, it is 0. 
			if low_b[1] == "2":
				Vx[regnr_x] &= Vx[regnr_y]

			#8xy3 - XOR Vx, Vy : Set Vx = Vx XOR Vy. Performs a bitwise exclusive OR on the values of Vx and Vy, then stores the result in Vx. An exclusive OR compares the corrseponding bits from two values, and if the bits are not both the same, then the corresponding bit in the result is set to 1. Otherwise, it is 0. 
			if low_b[1] == "3":
				Vx[regnr_x] ^= Vx[regnr_y]
			
			#8xy4 - ADD Vx, Vy : Set Vx = Vx + Vy, set VF = carry. The values of Vx and Vy are added together. If the result is greater than 8 bits (i.e., > 255,) VF is set to 1, otherwise 0. Only the lowest 8 bits of the result are kept, and stored in Vx.
			if low_b[1] == "4":	
				temp_reg = Vx[regnr_x] + Vx[regnr_y]
				if temp_reg > 255:
					#while temp_reg > 255:
						#temp_reg -= 256
					Vx[15] = 1
					#Vx[regnr_x] = temp_reg
				else:
					Vx[15] = 0
				
				Vx[regnr_x] = temp_reg & 0xff
				#print bin(Vx[regnr_x])
				
			#8xy5 - SUB Vx, Vy : Set Vx = Vx - Vy, set VF = NOT borrow. If Vx > Vy, then VF is set to 1, otherwise 0. Then Vy is subtracted from Vx, and the results stored in Vx.
			if low_b[1] == "5":	
				if Vx[regnr_x] > Vx[regnr_y]:
					Vx[15] = 1
				else:
					Vx[15] = 0
				Vx[regnr_x] -= Vx[regnr_y]
				while Vx[regnr_x] < 0:
					Vx[regnr_x] += 256
			
			#8xy6 - SHR Vx {, Vy} : Set Vx = Vx SHR 1. If the least-significant bit of Vx is 1, then VF is set to 1, otherwise 0. Then Vx is divided by 2.
			if low_b[1] == "6":
				if bin(Vx[regnr_x] | 0x100)[10] == "1":
					Vx[15] = 1
				else:
					Vx[15] = 0
				Vx[regnr_x] >>= Vx[regnr_x]
			
			#8xy7 - SUBN Vx, Vy : Set Vx = Vy - Vx, set VF = NOT borrow. If Vy > Vx, then VF is set to 1, otherwise 0. Then Vx is subtracted from Vy, and the results stored in Vx.
			if low_b[1] == "7":	
				if Vx[regnr_y] > Vx[regnr_x]:
					Vx[15] = 1
				else:
					Vx[15] = 0
				Vx[regnr_x] = Vx[regnr_y] - Vx[regnr_x]
			
			#8xyE - SHL Vx {, Vy} : Set Vx = Vx SHL 1. If the most-significant bit of Vx is 1, then VF is set to 1, otherwise to 0. Then Vx is multiplied by 2.			
			if low_b[1] == "e":
				if bin(Vx[regnr_x] | 0x100)[10] == "1":
					Vx[15] = 1
				else:
					Vx[15] = 0
				Vx[regnr_x] <<= Vx[regnr_x]
				
		#9xy0 - SNE Vx, Vy : Skip next instruction if Vx != Vy. The values of Vx and Vy are compared, and if they are not equal, the program counter is increased by 2.
		elif high_b[0] == "9":
			regnr_x = int(high_b[1], 16)
			regnr_y = int(low_b[0], 16)
			if Vx[regnr_x] != Vx[regnr_y]:
				PC += 2
				
		#Annn - LD I, addr : Set I = nnn. The value of register I is set to nnn.
		elif high_b[0] == "a":
			VI = int(high_b[1]+low_b, 16) & 0xfff
		
		#Bnnn - JP V0, addr : Jump to location nnn + V0. The program counter is set to nnn plus the value of V0.
		elif high_b[0] == "b":		
			PC = int(high_b[1]+low_b, 16)+Vx[0]-2
		
		#Cxkk - RND Vx, byte : Set Vx = random byte AND kk. The interpreter generates a random number from 0 to 255, which is then ANDed with the value kk. The results are stored in Vx.
		elif high_b[0] == "c":
			regnr = int(high_b[1], 16)
			randnr = random.randint(0,255)
			
			Vx[regnr] = randnr & int(low_b, 16)
		
		#Dxyn - DRW Vx, Vy, nibble
		#Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision.
		#The interpreter reads n bytes from memory, starting at the address stored in I. These bytes are then displayed as sprites on screen at coordinates (Vx, Vy). Sprites are XORed onto the existing screen. If this causes any pixels to be erased, VF is set to 1, otherwise it is set to 0. If the sprite is positioned so part of it is outside the coordinates of the display, it wraps around to the opposite side of the screen.
		elif high_b[0] == "d":
			x = Vx[int(high_b[1], 16)]
			y = Vx[int(low_b[0], 16)]
			n = int(low_b[1], 16)
			#print x,y,n
			sprite = bin(int(RAM[VI], 16) | 0x100)[3:]
			#binsprite = sprite[2:]
			#while len(sprite) < 10:
				#print binsprite
				#binsprite = "0" + binsprite
				#print binsprite
				#sprite = "0b" + binsprite	
			
			collision = False
			
			for bytes in range(1,n+1,1):
				#print bytes
				#print sprite
				for s in range(0, 7, 1):
					if x+s > 63:
						#x = 0
						break
					#print sprite
					#print sprite[s], s
					sprite_pos = int(sprite[s])	#s+2
					#print DISPLAY[x+s][y], sprite_pos
					if (DISPLAY[x+s][y] == 1) and (sprite_pos == 1):
						Vx[15] = 1
						collision = True
					elif collision == False:
						Vx[15] = 0
					
					#print s, sprite, sprite[s+2]
					DISPLAY[x+s][y] ^= sprite_pos
					
					if sprite_pos == 1:
						DISPLAY_DIFF.append((x+s,y,DISPLAY[x+s][y]))
					#print DISPLAY[x+s][y]
				
				if bytes < n:
					sprite = bin(int(RAM[VI + bytes], 16) | 0x100)[3:]
					#binsprite = sprite[2:]
					#while len(sprite) < 10:
						#binsprite = "0" + binsprite
						#sprite = "0b" + binsprite
					
					y += 1
				
		#Keyboard Funktions
		elif high_b[0] == "e":
			regnr = int(high_b[1], 16)
			#Ex9E - SKP Vx : Skip next instruction if key with the value of Vx is pressed. Checks the keyboard, and if the key corresponding to the value of Vx is currently in the down position, PC is increased by 2.
			if low_b == "9e":
				if keydown[Vx[regnr]] == 1:
					PC += 2
			#ExA1 - SKNP Vx : Skip next instruction if key with the value of Vx is not pressed. Checks the keyboard, and if the key corresponding to the value of Vx is currently in the up position, PC is increased by 2.
			elif low_b == "a1":
				if keydown[Vx[regnr]] == 0:
					PC += 2
			
		#Delay and Wait Funktions
		elif high_b[0] == "f":
			#Fx07 - LD Vx, DT : Set Vx = delay timer value. The value of DT is placed into Vx.
			if low_b == "07":
				regnr = int(high_b[1], 16)
				Vx[regnr] = DT
			
			#Fx0A - LD Vx, K : Wait for a key press, store the value of the key in Vx. All execution stops until a key is pressed, then the value of that key is stored in Vx.
			elif low_b == "0a":
				regnr = int(high_b[1], 16)
				count = 0
				# while not "1" in keydown:
					# count = 0
					# for k in keydown:
						# if k == 1:
							# break
						# count += 1
				if not 1 in keydown:
					PC -= 2
				else:
					for k in keydown:
						if k == 1:
							break
						count += 1
					Vx[regnr] = count
			
			#Fx15 - LD DT, Vx : Set delay timer = Vx. DT is set equal to the value of Vx.
			elif low_b == "15":
				regnr = int(high_b[1], 16)
				DT = Vx[regnr]
			
			#Fx18 - LD ST, Vx : Set sound timer = Vx. ST is set equal to the value of Vx.
			elif low_b == "18":
				regnr = int(high_b[1], 16)
				ST = Vx[regnr]
			
			#Fx1E - ADD I, Vx : Set I = I + Vx. The values of I and Vx are added, and the results are stored in I.
			elif low_b == "1e":
				regnr = int(high_b[1], 16)
				VI += Vx[regnr] & 0xfff
			
			#Fx29 - LD F, Vx Set I = location of sprite for digit Vx. The value of I is set to the location for the hexadecimal sprite corresponding to the value of Vx.
			elif low_b == "29":
				regnr = int(high_b[1], 16)
				VI = Vx[regnr]*5 & 0xfff
				
					#for i in range(0, 5, 1):
						#print bin(int(RAM[VI + i], 16))
						
			#Fx33 - LD B, Vx : Store BCD representation of Vx in memory locations I, I+1, and I+2. The interpreter takes the decimal value of Vx, and places the hundreds digit in memory at location in I, the tens digit at location I+1, and the ones digit at location I+2.
			elif low_b == "33":
				regnr = int(high_b[1], 16)
				RAM[VI] = hex(Vx[regnr]/100%10)
				RAM[VI + 1] = hex(Vx[regnr]/10%10)
				RAM[VI + 2] = hex(Vx[regnr]/1%10)
				
			#Fx55 - LD [I], Vx : Store registers V0 through Vx in memory starting at location I. The interpreter copies the values of registers V0 through Vx into memory, starting at the address in I.
			elif low_b == "55":
				regnr = int(high_b[1], 16)
				for i in range(0, regnr + 1, 1):
					#print i, RAM[VI + i], hex(Vx[i])
					RAM[VI + i] = hex(Vx[i])
			
			#Fx65 - LD Vx, [I] : Read registers V0 through Vx from memory starting at location I. The interpreter reads values from memory starting at location I into registers V0 through Vx.
			elif low_b == "65":
				regnr = int(high_b[1], 16)
				for i in range(0, regnr + 1, 1):
					Vx[i] = int(RAM[VI + i], 16)
	#--------------------------------------------------------------------------------------------------------------	
	
		if DT > 0:
			DT -= 1
		#Increment the program counter
		PC += 2
		#print hex(PC)
	
	#print DISPLAY_DIFF
	if len(DISPLAY_DIFF) > 0:
			for pixel in DISPLAY_DIFF:
				if pixel[2] == 1:
					pygame.draw.rect(windowSurface, WHITE, pygame.Rect(pixel[0]*pixel_size, pixel[1]*pixel_size, pixel_size, pixel_size), pixel_fill)
				else:
					pygame.draw.rect(windowSurface, BLACK, pygame.Rect(pixel[0]*pixel_size, pixel[1]*pixel_size, pixel_size, pixel_size), pixel_fill)
		
	#Clear Screen
	#windowSurface.fill(BLACK)
		
	#Zeiche alles auf den Schirm
	pygame.display.update()
	mainClock.tick(MainClockSpeed)
