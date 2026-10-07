from invert import *
import time, sys
sids = sys.argv[1:] or ALL
for sid in sids:
  for ds in (False, True):
    t0=time.time(); n=0; tot=0; to=0
    for w in ['ਸਤਿ', 'ਨਾਮੁ', 'ਕਰਤਾ', 'ਸਿੰਘ', 'ਨਿਰਭਉ', 'ਸਚਿਆਰਾ']:
        t = render(sid, w, ds); c = invert(sid, t, ds)
        if isinstance(c, tuple): to += 1; c = c[0]
        n += (w in c); tot += len(c)
    print(sid, ds, round(time.time()-t0,1), n, '/6 truth found; cands', tot, 'timeouts', to, flush=True)
