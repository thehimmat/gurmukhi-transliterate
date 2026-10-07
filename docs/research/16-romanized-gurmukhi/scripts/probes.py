from common import *
P = [('addak after C', 'ਪੱਕਾ'), ('addak after matra', 'ਸਿੱਖ'), ('addak+aspirate', 'ਮੱਥਾ'),
     ('tippi after C', 'ਸੰਤ'), ('tippi after matra', 'ਸਿੰਘ'), ('bindi after matra', 'ਮਾਂ'),
     ('nasal after indep V', 'ਆਂਖ'), ('tippi before labial', 'ਕੰਬ'),
     ('subjoined ਰ', 'ਪ੍ਰੀਤਮ'), ('subjoined ਹ', 'ਨ੍ਹਾਵਣ'), ('subjoined ਵ', 'ਸ੍ਵਾਦ'),
     ('final aunkar', 'ਨਾਮੁ'), ('final sihari', 'ਸਤਿ'), ('ਣ vs ਨ', 'ਣਨ'), ('ਟ ਤ ਡ ਦ', 'ਟਤਡਦ'),
     ('ਠ ਥ ਢ ਧ', 'ਠਥਢਧ'), ('ੜ ਰ', 'ੜਰ'), ('ਸ਼ ਸ', 'ਸ਼ਸ'), ('ਖ਼ ਖ', 'ਖ਼ਖ'), ('ਗ਼ ਗ', 'ਗ਼ਗ'), ('ਫ਼ ਫ', 'ਫ਼ਫ'), ('ਜ਼ ਜ', 'ਜ਼ਜ'), ('ਲ਼ ਲ', 'ਲ਼ਲ'),
     ('vowel hiatus a+u', 'ਕਉ'), ('au sign', 'ਕੌ'), ('a+i', 'ਕਇ'), ('ai sign', 'ਕੈ'),
     ('schwa: ਕਰਤਾਰ ds', 'ਕਰਤਾਰ'), ('ੴ', 'ੴ')]
import sys
mode = sys.argv[1] if len(sys.argv) > 1 else 'md'
print('| probe | Gurmukhi | ' + ' | '.join(ALL) + ' |')
print('|' + '---|' * (len(ALL) + 2))
for name, g in P:
    ds = 'ds' in name
    cells = []
    for s in ALL:
        try: cells.append(fwd(s, g + ' ', ds).rstrip(' '))
        except Crash: cells.append('CRASH')
    print(f'| {name} | {g} | ' + ' | '.join('`'+c+'`' for c in cells) + ' |')
