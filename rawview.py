#!/usr/bin/python
#coding=latin
import sys
import struct
import argparse
from Tkinter import *
from struct import *

parser = argparse.ArgumentParser(description=("Display raw bitmaps"))

parser.add_argument('rawfile', metavar='file', 
                    help=("Font or bitmap to load."))

parser.add_argument('-a', '--amiga', 
                    action='store_true',
                    help="Attempt to load as Amiga font.",)

parser.add_argument('-o', metavar='outfile', 
                    help="Attempt to convert to and write C64 charset.",)

parser.add_argument('--debug', 
                    action='store_true',
                    help="Print debug info.",)

args = parser.parse_args()
rawfile = args.rawfile
debug = args.debug
amiga = args.amiga
outfile = args.o

def dprint(message):
    if debug: print(message)

def decodebyte(byte):
    bits = []
    bit = 1
    for pos in range(0, 8):
        bitstate = ord(byte) & int(bit)
        if bitstate > 0: bitstate = True
        else: bitstate = False
        bits.append(bitstate)
        bit = bit << 1
    bits.reverse()
    return bits

def encodebyte(bits):
    byte = 0
    bitval = 128
    for bit in bits:
        if bit: byte += bitval
        bitval = bitval / 2
    return chr(byte)

def makebitmap(bitmap):
    global height
    global width
    bytepos = 0
    for byte in bitmap:
        bytepos += 1
        bits = decodebyte(byte)
        bitpos = 0
        for bit in bits:
            bitpos += 1
            x1 = bitpos * width 
            y1 = bytepos * height
            x2 = bitpos * width + width
            y2 = bytepos * height + height
            if bit: bitmapView.create_rectangle(x1, y1, x2, y2, fill='black')

def amigaload(font):
    fontsetting = readheader(font)
    if fontsetting['tf_XSize'] == 8 and fontsetting['tf_YSize'] == 8:
        bitmap = ''
        location = []
        charwidth = []
        # Strip header
        font = font[32:]
        lochar = fontsetting['tf_LoChar']
        hichar = fontsetting['tf_HiChar']
        length = fontsetting['tf_Modulo']
        fontpos = fontsetting['tf_CharData']
        charloc = fontsetting['tf_CharLoc']
        numchars = hichar - lochar
        count = 0
        for char in range(0, numchars*4+4, 4):
            data = struct.unpack('>HH',font[char+charloc:char+charloc+4])
            location.append(data[0])
            charwidth.append(data[1])
            count += 1
            dprint('Char number: ' + str(count) + 
                    ' - Location: ' + str(location[count-1]) + 
                    ' - Width :' + str(charwidth[count-1]))

        fontbits = []
        count = 0
        for char in range(fontpos,fontpos + length * 8):
            count += 1
            dprint('Byte: ' + str(count) + ' - Value: ' + str(ord(font[char])))
            bits = decodebyte(font[char])
            fontbits += bits

        dprint(fontbits)

        for char in range(0, numchars):
            for row in range (0, 8):
                #fetchbyte = location[char]/8 + (length * row)
                #if char == 0: fetchbyte = 0
                #dprint(fetchbyte)
                bitlocation = location[char] + (length * 8 * row)
                charbits = fontbits[bitlocation:bitlocation+8]
                #bitmapbyte = font[fetchbyte]
                bitmapbyte = encodebyte(charbits)
                dprint('char: ' + str(char) + 
                       ' - Length: ' + str(len(charbits)) + 
                       ' - Byte value: ' + str(ord(bitmapbyte)))
                #bitmap.append(bitmapbyte)
                bitmap += bitmapbyte
        if outfile: writepetscii(bitmap, lochar, hichar)
        return bitmap
    else:
        print("Can only convert 8x8 fonts.")
        quit()

def bitarray(data):
    bitarray = []
    for byte in data:
        bits = decodebyte(byte)
        bitarray.append(bits)
    return bitarray

def readheader(font):
    header = font[36:][:106]
    fields = (['ln_Succ'    , 'L'],
              ['ln_Pred'    , 'L'],
              ['ln_Type'    , 'B'],
              ['ln_Pri'     , 'B'],
              ['ln_fontName', 'L'],
              ['DFH_ID'     , 'H'],
              ['Revision'   , 'H'],
              ['Segment'    , 'L'],
              ['Fontname'   , '32s'],
              ['ln_Succ2'   , 'L'],
              ['ln_Pred2'   , 'L'],
              ['ln_Type2'   , 'B'],
              ['ln_Pri2'    , 'B'],
              ['ln_fontNam2', 'L'],
              ['mn_ReplyPor', 'L'],
              ['Reserved'   , 'H'],
              ['tf_YSize'   , 'H'],
              ['tf_Style'   , 'B'],
              ['Flags'      , 'B'],
              ['tf_XSize'   , 'H'],
              ['tf_Baseline', 'H'],
              ['tf_Boldsmea', 'H'],
              ['tfAccessors', 'H'],
              ['tf_LoChar'  , 'B'],
              ['tf_HiChar'  , 'B'],
              ['tf_CharData', 'L'],
              ['tf_Modulo'  , 'H'],
              ['tf_CharLoc' , 'L'],
              ['tf_CharSpac', 'L'],
              ['tf_CharKern', 'L'])
    fmtstring = '>'
    for field in fields:
        fmtstring = fmtstring + (field[1])
    dprint(fmtstring)
    dprint(fields)
    values = struct.unpack(fmtstring,header)
    for field in range(0,len(fields)):
        fields[field][1]=values[field]
    dprint(fields)
    return dict(fields)

def writepetscii(bitmap,lochar,hichar):
    global outfile
    petsciiorder = '@abcdefghijklmnopqrstuvwxyz[£]^_ !"#$%&\'()*+,-./0123456789:;<=>?\\ABCDEFGHIJKLMNOPQRSTUVWXYZ'.decode('utf-8')
    asciiorder =   ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[£]^_\\abcdefghijklmnopqrstuvwxyz'.decode('utf-8')
    length = len(petsciiorder)
    outchars = []
    offset = 32 - lochar 

    for count in range(0, 255 * 8):
        outchars.append(0)

    count = 0
    for char in petsciiorder:
        asciipos = asciiorder.index(char)
        dprint(char + ' = ' + petsciiorder[asciipos])

        for line in range(0, 8):
            outchars[count*8+line] = bitmap[asciipos * 8 + line + offset * 8]
        count += 1

    of = open(outfile,'wb')
    try:
        of.write(''.join(outchars[:length*8]))
        print('C64 charset written to ' + outfile + '.')
    except:
        print('File I/O error.')

f = open(rawfile, 'r')
bitmap = f.read()
width = 4
height = 4
root = Tk()
mainContainer = Frame(root)
scroller = Scrollbar(mainContainer)
scroller.pack(side=RIGHT,fill=Y)
mainContainer.pack()
if amiga: bitmap = amigaload(bitmap)
bitmapView = Canvas(mainContainer, width=80, height=len(bitmap)*height, scrollregion = (1,1,width * 8, height * len(bitmap)))
scroller.config(command=bitmapView.yview)

makebitmap(bitmap)
bitmapView.config(yscrollcommand=scroller.set)
bitmapView.pack(side=LEFT)
if not outfile: root.mainloop()

