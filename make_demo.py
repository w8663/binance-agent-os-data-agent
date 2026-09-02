#!/usr/bin/env python3
import re, html, os
def inline(t):
    t = html.escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return t
def md_to_html(md):
    lines, out, in_tbl = md.split("\n"), [], False
    for ln in lines:
        s = ln.rstrip()
        if s.startswith("|") and s.endswith("|"):
            cells = [inline(c.strip()) for c in s.strip("|").split("|")]
            if not in_tbl: out.append("<table>"); in_tbl = True
            if all(re.fullmatch(r":?-{2,}:?", html.unescape(c)) for c in cells): continue
            out.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>"); continue
        if in_tbl: out.append("</table>"); in_tbl = False
        if s.startswith("### "): out.append(f"<h3>{inline(s[4:])}</h3>")
        elif s.startswith("## "): out.append(f"<h2>{inline(s[3:])}</h2>")
        elif s.startswith("# "): out.append(f"<h1>{inline(s[2:])}</h1>")
        elif s.startswith("> "): out.append(f"<blockquote>{inline(s[2:])}</blockquote>")
        elif s == "": out.append("")
        else: out.append(f"<p>{inline(s)}</p>")
    if in_tbl: out.append("</table>")
    return "\n".join(out)
md = open("output/report.md").read()
css = "*{box-sizing:border-box}body{margin:0;font-family:-apple-system,'SF Mono',Menlo,monospace;background:#0e1117;color:#cfe3e6;padding:24px}.wrap{max-width:980px;margin:auto;background:#161b22;border:1px solid #23302f;border-radius:14px;padding:28px}h1{color:#3bd89b;font-size:22px;border-bottom:1px solid #23302f;padding-bottom:10px}h2{color:#39c4ff;font-size:16px;margin-top:22px}h3{color:#f0b429}table{width:100%;border-collapse:collapse;font-size:12.5px;margin:12px 0}td,th{border:1px solid #23302f;padding:6px 9px;text-align:left}tr:nth-child(even){background:#0d1117}li{margin:4px 0;font-size:13px}blockquote{border-left:3px solid #f0b429;margin:14px 0;padding:8px 14px;background:#1b2329;color:#9fb1b8;font-size:12px}p{font-size:13.5px}"
open("output/demo.html","w").write(f"<!doctype html><html><head><meta charset=utf-8><style>{css}</style></head><body><div class='wrap'>{md_to_html(md)}</div></body></html>")
print("demo.html size:", os.path.getsize("output/demo.html"))
