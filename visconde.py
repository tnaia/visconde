import sys
import re

banner = "This is VISCONDE version 0.1.2."
file = ""
fence_regexp = re.compile('```+')
chunk = {}
def chunks_of(code):
    return [line.strip()[2:-1].strip() for line in code if is_chunk_line(line)]
def is_chunk_line(l):
    aux = l.strip()
    return aux and (aux[0:2] == '@{' and aux[-1] == '}')

def chunk_line_name(line):
    return line.strip()[2:-1].strip()

def indent_code(indentation, code):
    return [' '*indentation + line for line in code]

file = sys.argv[-1]
print(banner) # Hi!

with open(file, 'r') as input_file:
    reading_code_chunk = False
    last_line_blank = False
    chunk_name = ''
    chunk_text = [] # list of lines

    for line_number, line in enumerate(input_file):
        if not reading_code_chunk:
            if line.strip() == "":
                last_line_blank = True
                continue
            elif last_line_blank:
                match_fence = fence_regexp.match(line) # at least 3 backticks
                if match_fence:
                    fence_length = match_fence.end()
                    chunk_name = line[fence_length:].strip()
                    chunk_line = line_number
                    chunk_text = []
                    reading_code_chunk = True
                else:
                    last_line_blank = False
        
            continue
    
        match_fence = fence_regexp.match(line) # at least 3 backticks
        if match_fence and match_fence.end() == fence_length:
            if chunk_name not in chunk:
                chunk[chunk_name] = []
            chunk[chunk_name] += [(chunk_line+1, chunk_text)]
            reading_code_chunk = False
            last_line_blank = False
        else:
            chunk_text += [line]
used_at = dict()

for blk in chunk:
    if blk not in used_at:
        used_at[blk] = []
    for l,b in chunk[blk]:
        for chk in chunks_of(b):
            if chk not in used_at:
                used_at[chk] = [blk]
            else:
                used_at[chk] += [blk]

# expansion_order = [blk for blk, parents in sorted(used_at.items(), key=lambda t: len(t[1]),reverse=True)]
root_chunks = [blk for blk, parents in used_at.items() if len(parents) == 0]


for blk in root_chunks:
    print("Writing file %s... " % blk,end='')
    with open(blk, 'w') as output:
        buffer = [l for c in chunk[blk] for l in c[1]]
        i = 0
        while i < len(buffer):
            if is_chunk_line(buffer[i]):
                the_chunk_name = chunk_line_name(buffer[i])
                if the_chunk_name not in chunk:       # do we know what to insert in place of line?
                    print("! warning: missing text for chunk: %s" % the_chunk_name)
                    print(buffer[i], file=output, end='')
                    i += 1
                else:
                    indentation = re.compile(' *').match(buffer[i]).end()
                    indented_lines = [x for l,c in  chunk[the_chunk_name] for x in indent_code(indentation, c)]
                    buffer = indented_lines + buffer[i+1:]
                    i = 0
            else:
                print(buffer[i], file=output, end='')
                i += 1
        
    print("[ DONE ]")
