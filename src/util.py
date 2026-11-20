def slug(s):
    tr = str.maketrans("çğıöşüÇĞİÖŞÜâîûÂÎÛ", "cgiosuCGIOSUaiuAIU")
    out = "".join(c if c.isalnum() else "_" for c in s.translate(tr).lower())
    while "__" in out: out = out.replace("__", "_")
    return out.strip("_")


def fmt_num(cur, final):
    """Turkish number format: 3.713 / 1,5. Decimals follow the final value's precision."""
    s = repr(float(final))
    dec = 0 if float(final).is_integer() else min(2, len(s.split(".")[1]))
    txt = f"{cur:,.{dec}f}"
    return txt.replace(",", "X").replace(".", ",").replace("X", ".")
