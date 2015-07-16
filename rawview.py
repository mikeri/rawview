import sys
import struct
import argparse
from Tkinter import *
from struct import *

parser = argparse.ArgumentParser(description=("Display raw bitmaps"))

parser.add_argument('rawfile', metavar='file', 
                    help=("Font or bitmap to load."))

parser.add_argument('--amiga', 
                    action='store_true',
                    help="Attempt to load as Amiga font.",)

parser.add_argument('--debug', 
                    action='store_true',
                    help="Print debug info.",)

args = parser.parse_args()
rawfile = args.rawfile
debug = args.debug
amiga = args.debug

def dprint(message):
    if debug: print(message)

def decodebyte(byte):
    bits = []
    bit = 1
    for pos in range(0, 8):
        bits.append(ord(byte) & int(bit))
        bit = bit << 1
    bits.reverse()
    return bits

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
            if bit > 0: bitmapView.create_rectangle(x1, y1, x2, y2, fill='black')

def amigaload(font):
    fontsetting = readheader(font)
    if fontsetting['tf_XSize'] == 8 and fontsetting['tf_YSize'] == 8:
        bitmap = []
        location = []
        charwidth = []
        font = font[36:]
        lochar = fontsetting['tf_LoChar']
        hichar = fontsetting['tf_HiChar']
        length = hichar - lochar + 3
        fontpos = fontsetting['tf_CharData']
        charloc = fontsetting['tf_CharLoc']
        count = 0
        for char in range(0, length*4+4, 4):
            data = struct.unpack('>HH',font[char+charloc:char+charloc+4])
            location.append(data[0])
            charwidth.append(data[1])
            count += 1
            dprint(count)
            dprint(location)
            dprint(charwidth)

        for char in range(0, length+1):
            for row in range (0, 8):
                fetchbyte = location[char]/8 + (length * row)
                dprint(('char:' ,char))
                dprint(fetchbyte)
                bitmapbyte = font[fetchbyte]
                dprint(bitmapbyte)
                bitmap.append(bitmapbyte)
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
root.mainloop()
