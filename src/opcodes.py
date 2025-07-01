from cpu import *

class OPCODES:
    def OP_00E0(self):
        self.video.fill(0)
        self.pc += 2

    def OP_00EE(self):
        if self.sp > 0:
            self.sp -= 1
            self.pc = self.stack[self.sp]
        else:
            self.pc = START_ADDRESS

    def OP_1nnn(self):
        address = self.opcode & 0x0FFF
        self.pc = address

    def OP_2nnn(self):
        address = self.opcode & 0x0FFF
        if self.sp < len(self.stack):
            self.stack[self.sp] = self.pc + 2
            self.sp += 1
            self.pc = address
        else:
            print("[2NNN] ERROR: Stack overflow — unable to push return address.")

    def OP_3xkk(self):
        Vx = (self.opcode & 0x0F00) >> 8
        byte = self.opcode & 0x00FF
        if self.registers[Vx] == byte:
            self.pc += 4
        else:
            self.pc += 2

    def OP_4xkk(self):
        Vx = (self.opcode & 0x0F00) >> 8
        byte = self.opcode & 0x00FF
        if self.registers[Vx] != byte:
            self.pc += 4
        else:
            self.pc += 2

    def OP_5xy0(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4
        if self.registers[Vx] == self.registers[Vy]:
            self.pc += 4
        else:
            self.pc += 2

    def OP_6xkk(self):
        Vx = (self.opcode & 0x0F00) >> 8
        byte = self.opcode & 0x00FF
        self.registers[Vx] = byte
        self.pc += 2

    def OP_7xkk(self):
        Vx = (self.opcode & 0x0F00) >> 8
        byte = self.opcode & 0x00FF
        self.registers[Vx] = (self.registers[Vx] + byte) & 0xFF
        self.pc += 2

    def OP_8xy0(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4
        self.registers[Vx] = self.registers[Vy]
        self.pc += 2

    def OP_8xy1(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4
        self.registers[Vx] |= self.registers[Vy]
        self.pc += 2

    def OP_8xy2(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4
        self.registers[Vx] &= self.registers[Vy]
        self.pc += 2

    def OP_8xy3(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4
        self.registers[Vx] ^= self.registers[Vy]
        self.pc += 2

    def OP_8xy4(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4
        sum_val = self.registers[Vx] + self.registers[Vy]
        self.registers[0xF] = 1 if sum_val > 0xFF else 0
        self.registers[Vx] = sum_val & 0xFF
        self.pc += 2

    def OP_8xy5(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4
        self.registers[0xF] = 1 if self.registers[Vx] > self.registers[Vy] else 0
        self.registers[Vx] = (self.registers[Vx] - self.registers[Vy]) & 0xFF
        self.pc += 2

    def OP_8xy6(self):
        Vx = (self.opcode & 0x0F00) >> 8
        self.registers[0xF] = self.registers[Vx] & 0x1
        self.registers[Vx] >>= 1
        self.pc += 2

    def OP_8xy7(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4
        self.registers[0xF] = 1 if self.registers[Vy] > self.registers[Vx] else 0
        self.registers[Vx] = (self.registers[Vy] - self.registers[Vx]) & 0xFF
        self.pc += 2

    def OP_8xyE(self):
        Vx = (self.opcode & 0x0F00) >> 8
        self.registers[0xF] = (self.registers[Vx] & 0x80) >> 7
        self.registers[Vx] = (self.registers[Vx] << 1) & 0xFF
        self.pc += 2

    def OP_9xy0(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4
        if self.registers[Vx] != self.registers[Vy]:
            self.pc += 4
        else:
            self.pc += 2

    def OP_Annn(self):
        address = self.opcode & 0x0FFF
        self.index = address
        self.pc += 2

    def OP_Bnnn(self):
        address = self.opcode & 0x0FFF
        self.pc = self.registers[0] + address

    def OP_Cxkk(self):
        Vx = (self.opcode & 0x0F00) >> 8
        byte = self.opcode & 0x00FF
        self.registers[Vx] = self.random_byte() & byte
        self.pc += 2

    def OP_Dxyn(self):
        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4
        height = self.opcode & 0x000F
        xPos = self.registers[Vx] % VIDEO_WIDTH
        yPos = self.registers[Vy] % VIDEO_HEIGHT
        self.registers[0xF] = 0

        for row in range(height):
            spriteByte = self.memory[self.index + row]
            for col in range(8):
                mask = 0x80 >> col
                spritePixel = (spriteByte & mask) != 0
                screenX = (xPos + col) % VIDEO_WIDTH
                screenY = (yPos + row) % VIDEO_HEIGHT
                if spritePixel:
                    if self.video[screenY, screenX]:
                        self.registers[0xF] = 1
                    self.video[screenY, screenX] ^= 1
        self.pc += 2

    def OP_Ex9E(self):
        Vx = (self.opcode & 0x0F00) >> 8
        key = self.registers[Vx]
        if self.keypad[key]:
            self.pc += 4
        else:
            self.pc += 2

    def OP_ExA1(self):
        Vx = (self.opcode & 0x0F00) >> 8
        key = self.registers[Vx]
        if not self.keypad[key]:
            self.pc += 4
        else:
            self.pc += 2

    def OP_Fx07(self):
        Vx = (self.opcode & 0x0F00) >> 8
        self.registers[Vx] = self.delayTimer
        self.pc += 2

    def OP_Fx0A(self):
        Vx = (self.opcode & 0x0F00) >> 8
        for i in range(16):
            if self.keypad[i]:
                self.registers[Vx] = i
                self.pc += 2
                return
        # If no key pressed, do not increment PC

    def OP_Fx15(self):
        Vx = (self.opcode & 0x0F00) >> 8
        self.delayTimer = self.registers[Vx]
        self.pc += 2

    def OP_Fx18(self):
        Vx = (self.opcode & 0x0F00) >> 8
        self.soundTimer = self.registers[Vx]
        self.pc += 2

    def OP_Fx1E(self):
        Vx = (self.opcode & 0x0F00) >> 8
        self.index = (self.index + self.registers[Vx]) & 0xFFFF
        self.pc += 2

    def OP_Fx29(self):
        Vx = (self.opcode & 0x0F00) >> 8
        digit = self.registers[Vx]
        self.index = FONTSET_START_ADDRESS + (5 * digit)
        self.pc += 2

    def OP_Fx33(self):
        Vx = (self.opcode & 0x0F00) >> 8
        value = self.registers[Vx]
        self.memory[self.index + 2] = value % 10
        value //= 10
        self.memory[self.index + 1] = value % 10
        value //= 10
        self.memory[self.index] = value % 10
        self.pc += 2

    def OP_Fx55(self):
        Vx = (self.opcode & 0x0F00) >> 8
        for i in range(Vx + 1):
            self.memory[self.index + i] = self.registers[i]
        self.pc += 2

    def OP_Fx65(self):
        Vx = (self.opcode & 0x0F00) >> 8
        for i in range(Vx + 1):
            self.registers[i] = self.memory[self.index + i]
        self.pc += 2