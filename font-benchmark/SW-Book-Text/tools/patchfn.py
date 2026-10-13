"""Replace one top-level function in a module by name:  patchfn.py FILE NAME < new_body"""
import sys, re
f, name = sys.argv[1], sys.argv[2]
new = sys.stdin.read().strip("\n") + "\n\n\n"
s = open(f).read()
m = re.search(r"^def %s\(" % re.escape(name), s, re.M)
assert m, "function %s not found" % name
n = re.search(r"^(def |[A-Z_]+ = )", s[m.end():], re.M)
end = m.end() + n.start() if n else len(s)
open(f, "w").write(s[:m.start()] + new + s[end:])
