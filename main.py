# number_network_tutor_final.py
"""
Number Systems Converter + Subnetting Visual Tutor (final, UX improved)
 - Responsive grid layout so bottom controls are always visible
 - Uses ttkbootstrap ("superhero") + customtkinter for toggles
 - IPv4 animated visual tutor, Simple English mode, PDF export
Dependencies:
    pip install ttkbootstrap customtkinter reportlab pillow
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as tb
import customtkinter as ctk
import ipaddress
import math
import io

# optional pillow for image embedding in PDF
try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

# reportlab for PDF
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

# ---------- Utility functions ----------
def dotted_bin_8(x):
    return format(x, '08b')

def dotted_bin_32(x):
    return '.'.join(format(x & 0xFFFFFFFF, '032b')[i:i+8] for i in range(0,32,8))

# ---------- Converters (step-by-step) ----------
def decimal_to_binary_steps(n):
    n = int(n)
    if n == 0:
        return "Step 1: 0 is 0 in binary\n✅ Binary Result: 0"
    steps = []
    bits = []
    step = 1
    t = n
    while t > 0:
        r = t % 2
        steps.append(f"Step {step}: {t} ÷ 2 = {t//2}, remainder {r}")
        bits.append(str(r))
        t //= 2
        step += 1
    bits.reverse()
    steps.append(f"✅ Binary Result: {''.join(bits)}")
    return "\n".join(steps)

def decimal_to_octal_steps(n):
    n = int(n)
    if n == 0:
        return "Step 1: 0 is 0 in octal\n✅ Octal Result: 0"
    steps, digits = [], []
    step, t = 1, n
    while t > 0:
        r = t % 8
        steps.append(f"Step {step}: {t} ÷ 8 = {t//8}, remainder {r}")
        digits.append(str(r))
        t //= 8
        step += 1
    digits.reverse()
    steps.append(f"✅ Octal Result: {''.join(digits)}")
    return "\n".join(steps)

def decimal_to_hex_steps(n):
    n = int(n)
    if n == 0:
        return "Step 1: 0 is 0 in hex\n✅ Hexadecimal Result: 0"
    hex_map = "0123456789ABCDEF"
    steps, digits = [], []
    step, t = 1, n
    while t > 0:
        r = t % 16
        steps.append(f"Step {step}: {t} ÷ 16 = {t//16}, remainder {r} ({hex_map[r]})")
        digits.append(hex_map[r])
        t //= 16
        step += 1
    digits.reverse()
    steps.append(f"✅ Hexadecimal Result: {''.join(digits)}")
    return "\n".join(steps)

def binary_to_decimal_steps(s):
    s = s.strip()
    if not s:
        raise ValueError("Empty input")
    if any(ch not in "01" for ch in s):
        raise ValueError("Binary must contain only 0 and 1")
    steps = []
    total = 0
    p = len(s)-1
    for ch in s:
        val = int(ch) * (2**p)
        steps.append(f"{ch} × 2^{p} = {val}")
        total += val
        p -= 1
    steps.append(f"✅ Decimal Result: {total}")
    return "\n".join(steps)

def octal_to_decimal_steps(s):
    s = s.strip()
    if not s:
        raise ValueError("Empty input")
    if any(ch not in "01234567" for ch in s):
        raise ValueError("Octal digits must be 0-7")
    steps = []
    total = 0
    p = len(s)-1
    for ch in s:
        val = int(ch) * (8**p)
        steps.append(f"{ch} × 8^{p} = {val}")
        total += val
        p -= 1
    steps.append(f"✅ Decimal Result: {total}")
    return "\n".join(steps)

def hex_to_decimal_steps(s):
    s = s.strip().upper()
    if not s:
        raise ValueError("Empty input")
    map16 = "0123456789ABCDEF"
    if any(ch not in map16 for ch in s):
        raise ValueError("Hex digits must be 0-9, A-F")
    steps = []
    total = 0
    p = len(s)-1
    for ch in s:
        val = map16.index(ch)
        steps.append(f"{ch} ({val}) × 16^{p} = {val * (16**p)}")
        total += val * (16**p)
        p -= 1
    steps.append(f"✅ Decimal Result: {total}")
    return "\n".join(steps)

# ---------- Network verbose helpers ----------
def ipv4_steps_verbose(subnet_str, simple_mode=False):
    try:
        net = ipaddress.IPv4Network(subnet_str, strict=False)
    except Exception:
        raise ValueError("Invalid IPv4 network. Use e.g. 172.54.1.0/26")
    prefix = net.prefixlen
    mask = net.netmask
    mask_int = int(mask)
    network_addr = net.network_address
    broadcast = net.broadcast_address
    total = net.num_addresses
    host_bits = 32 - prefix
    input_ip_text = subnet_str.split('/')[0]
    try:
        input_ip = ipaddress.IPv4Address(input_ip_text)
    except Exception:
        input_ip = network_addr
    ip_int = int(input_ip)
    net_int = int(network_addr)
    host_mask = (~mask_int) & 0xFFFFFFFF
    lines = []
    if simple_mode:
        lines.append(f"Input: {subnet_str}")
        lines.append("")
        lines.append("Simple English Summary:")
        lines.append(f"  • Think: network bits = building address; host bits = room numbers")
        lines.append(f"  • /{prefix} → {prefix} building bits, {host_bits} room bits")
        lines.append(f"  • Rooms (addresses) = 2^{host_bits} = {total}")
        if prefix not in (31,32):
            lines.append(f"  • Usable rooms = {total-2} (usually)")
        lines.append("")
        lines.append(f"Network (start): {network_addr}")
        lines.append(f"Broadcast (announce to all): {broadcast}")
    else:
        lines.append(f"Input: {subnet_str}\n")
        lines.append("STEP 1 — Prefix")
        lines.append(f"  • /{prefix} → network bits = {prefix}, host bits = {host_bits}\n")
        lines.append("STEP 2 — Netmask")
        bin_mask = dotted_bin_32(mask_int)
        lines.append(f"  • Mask (binary): {bin_mask}")
        lines.append(f"  • Mask (decimal): {mask}")
        lines.append("STEP 3 — IP to binary")
        ip_bins = [dotted_bin_8(int(p)) for p in str(input_ip).split('.')]
        lines.append(f"  • IP: {input_ip} → {'.'.join(ip_bins)}")
        lines.append("STEP 4 — Network (IP AND Mask)")
        and_result = ip_int & mask_int
        lines.append(f"  • AND result (binary): {dotted_bin_32(and_result)}")
        lines.append(f"  • Network address: {ipaddress.IPv4Address(and_result)}")
        lines.append("STEP 5 — Broadcast")
        lines.append(f"  • Host mask (inverse): {dotted_bin_32(host_mask)}")
        broadcast_calc = net_int | host_mask
        lines.append(f"  • Broadcast: {ipaddress.IPv4Address(broadcast_calc)}")
        lines.append("STEP 6 — Counts")
        lines.append(f"  • 2^{host_bits} = {total} total addresses")
        if prefix == 32:
            usable = 1
        elif prefix == 31:
            usable = 2
        else:
            usable = total - 2
        lines.append(f"  • Usable hosts (typical): {usable}")
        lines.append("\nSTEP 7 — Summary")
        lines.append(f"  Network: {ipaddress.IPv4Address(and_result)}/{prefix}")
        lines.append(f"  Netmask: {mask}")
        lines.append(f"  Broadcast: {ipaddress.IPv4Address(broadcast_calc)}")
        lines.append(f"  Total addresses: {total}")
        lines.append(f"  Usable hosts: {usable}")
        if prefix not in (31,32):
            lines.append(f"  First usable: {ipaddress.IPv4Address(and_result+1)}")
            lines.append(f"  Last usable: {ipaddress.IPv4Address(broadcast_calc-1)}")
    and_result = ip_int & mask_int
    broadcast_calc = net_int | host_mask
    viz = {
        "prefix": prefix,
        "mask_dec": str(mask),
        "mask_bins": [dotted_bin_8(int(o)) for o in str(mask).split('.')],
        "ip_dec": str(input_ip),
        "ip_bins": [dotted_bin_8(int(o)) for o in str(input_ip).split('.')],
        "network": str(ipaddress.IPv4Address(and_result)),
        "network_bin": dotted_bin_32(and_result),
        "broadcast": str(ipaddress.IPv4Address(broadcast_calc)),
        "broadcast_bin": dotted_bin_32(broadcast_calc),
        "total": total,
        "usable": (1 if prefix==32 else (2 if prefix==31 else total-2)),
        "first": str(ipaddress.IPv4Address(and_result + (0 if prefix in (31,32) else 1))),
        "last": str(ipaddress.IPv4Address(broadcast_calc - (0 if prefix in (31,32) else 1))),
        "host_bits": host_bits,
        "mask_int": mask_int,
        "host_mask_int": host_mask
    }
    return "\n".join(lines), viz

def hosts_to_ipv4_steps(hosts_required, simple_mode=False):
    hosts_required = int(hosts_required)
    lines = []
    if simple_mode:
        lines.append(f"Need {hosts_required} hosts. Find smallest block.")
    else:
        lines.append(f"Input: needed hosts = {hosts_required}")
    for s in range(0,33):
        total = 2**s
        if s == 0:
            usable = 1
        elif s == 1:
            usable = 2
        else:
            usable = total - 2
        lines.append(f"Test s={s}: total={total}, usable={usable}")
        if usable >= hosts_required:
            prefix = 32 - s
            lines.append(f"Found: /{prefix} (total {total}, usable {usable})")
            return "\n".join(lines), {"prefix": prefix, "total": total, "usable": usable}
    lines.append("No suitable prefix found.")
    return "\n".join(lines), None

def ipv6_steps_verbose(subnet_str, simple_mode=False):
    try:
        net = ipaddress.IPv6Network(subnet_str, strict=False)
    except Exception:
        raise ValueError("Invalid IPv6 network. Use e.g. 2001:db8::/64")
    prefix = net.prefixlen
    total = net.num_addresses
    host_bits = 128 - prefix
    lines = []
    if simple_mode:
        lines.append(f"Input: {subnet_str}")
        lines.append(f"/{prefix} → host bits = {host_bits}, total = 2^{host_bits} = {total}")
    else:
        lines.append(f"Input: {subnet_str}")
        lines.append(f"/{prefix} → host bits = {host_bits}")
        mask_int = ((1<<128)-1) ^ ((1<<(128-prefix))-1) if prefix != 0 else 0
        groups = [format((mask_int >> (112 - i*16)) & 0xFFFF, '016b') for i in range(8)]
        lines.append("Mask grouped (16-bit):")
        lines.append("  " + " ".join(groups))
        lines.append(f"Network: {net.network_address}/{prefix}")
        lines.append(f"Total addresses: {total}")
    mask_int = ((1<<128)-1) ^ ((1<<(128-prefix))-1) if prefix != 0 else 0
    groups = [format((mask_int >> (112 - i*16)) & 0xFFFF, '016b') for i in range(8)]
    hextets = [format((int(net.network_address) >> (112 - i*16)) & 0xFFFF, '04x') for i in range(8)]
    viz = {"prefix": prefix, "groups": groups, "hextets": hextets, "total": total, "host_bits": host_bits, "network": str(net.network_address)}
    return "\n".join(lines), viz

def hosts_to_ipv6_steps(hosts_required, simple_mode=False):
    hosts_required = int(hosts_required)
    for s in range(0,129):
        total = 1 << s
        if total >= hosts_required:
            prefix = 128 - s
            return f"Found s={s} → prefix /{prefix}, total {total}", {"prefix": prefix, "total": total}
    return "No suitable IPv6 prefix found.", None

# ---------- Visual helpers ----------
def draw_octet_bits(canvas, x, y, bits8, outline_net=False, tag=None):
    box_w, box_h, gap = 24, 24, 5
    for i, b in enumerate(bits8):
        bx = x + i*(box_w+gap)
        color = "#2ecc71" if b == '1' else "#e74c3c"
        outline = "#145A32" if outline_net and b == '1' else "#222"
        tags = ()
        if tag:
            tags = (tag + f"_{i}",)
        canvas.create_rectangle(bx, y, bx+box_w, y+box_h, fill=color, outline=outline, width=2, tags=tags)
        canvas.create_text(bx+box_w/2, y+box_h/2, text=b, fill="white", font=("Consolas",9,"bold"), tags=tags)

def draw_hextet_groups(canvas, x, y, groups):
    box_w, box_h, gap = 100, 26, 6
    for i, g in enumerate(groups):
        bx = x + i*(box_w+gap)
        canvas.create_rectangle(bx, y, bx+box_w, y+box_h, fill="#34495e", outline="#222")
        canvas.create_text(bx+box_w/2, y+box_h/2, text=g, fill="white", font=("Consolas",9))

def draw_host_bar(canvas, x, y, total, reserved_top=2):
    max_draw = 256
    box_w, box_h, gap = 10, 10, 2
    cols = 16
    for i in range(min(total, max_draw)):
        row = i // cols
        col = i % cols
        bx = x + col*(box_w+gap)
        by = y + row*(box_h+gap)
        color = "#95a5a6" if i < reserved_top else "#3498db"
        canvas.create_rectangle(bx, by, bx+box_w, by+box_h, fill=color, outline="#222")
    if total > max_draw:
        canvas.create_text(x, y + ((min(total,max_draw)//cols)+1)*(box_h+gap) + 12, anchor="w",
                           text=f"(Showing first {max_draw}; total = {total})", fill="#eee", font=("Segoe UI",9))

# ---------- Animator (IPv4) ----------
class IPv4Animator:
    def __init__(self, canvas, viz, text_widget, speed_ms=700):
        self.canvas = canvas
        self.viz = viz
        self.text = text_widget
        self.speed_ms = speed_ms
        self.running = False

    def reset(self):
        self.canvas.delete("anim")
        self.running = False

    def run(self):
        self.reset()
        self.running = True
        self._step_mask()

    def _step_mask(self):
        pad_x = 20; y = 40
        self.canvas.create_text(pad_x, y-20, anchor="nw", text="Mask (binary):", fill="#ecf0f1", font=("Segoe UI",10,"bold"), tags=("anim",))
        per = (24+5)*8 + 12
        box_x = pad_x
        for oct_bin in self.viz['mask_bins']:
            draw_octet_bits(self.canvas, box_x, y, oct_bin, outline_net=True, tag="mask")
            box_x += per
        prefix = self.viz['prefix']
        # highlight prefix by overlaying thin outlines incrementally
        total_bits = 32
        def highlight(n):
            # draw highlight rectangles for first n bits
            # compute coordinates for these n boxes
            box_x2 = pad_x
            drawn = 0
            per_octet = per
            for oct_bin in self.viz['mask_bins']:
                for i, _ in enumerate(oct_bin):
                    bx = box_x2 + i*(24+5)
                    if drawn < n:
                        self.canvas.create_rectangle(bx, y, bx+24, y+24, outline="#f1c40f", width=3, tags=("anim","hl"))
                    drawn += 1
                box_x2 += per_octet
            if n < prefix:
                self.canvas.after(max(60, self.speed_ms//8), lambda: highlight(n + max(1, prefix//8)))
            else:
                self.canvas.after(self.speed_ms//2, self._step_ip)
        highlight(1)

    def _step_ip(self):
        pad_x = 20; y = 140
        self.canvas.create_text(pad_x, y-20, anchor="nw", text=f"IP: {self.viz['ip_dec']}", fill="#ecf0f1", font=("Segoe UI",10,"bold"), tags=("anim",))
        per = (24+5)*8 + 12
        box_x = pad_x
        for oct_bin in self.viz['ip_bins']:
            draw_octet_bits(self.canvas, box_x, y, oct_bin, tag="ip")
            box_x += per
        # highlight octet by octet
        def highlight(k):
            if k > 3:
                self.canvas.after(self.speed_ms//3, self._step_and)
                return
            bx = pad_x + k*per
            self.canvas.create_rectangle(bx-4, y-4, bx + (24+5)*8 - 4, y+24+4, outline="#f1c40f", width=3, tags=("anim","hl_oct"))
            self.canvas.after(self.speed_ms//3, lambda: highlight(k+1))
        highlight(0)

    def _step_and(self):
        pad_x = 20; y = 260
        self.canvas.create_text(pad_x, y, anchor="nw", text="Network Address (IP AND Mask):", fill="#ecf0f1", font=("Segoe UI",10,"bold"), tags=("anim",))
        y += 18
        self.canvas.create_text(pad_x, y, anchor="nw", text=f"IP bits : {self.viz['ip_bins'][0]}.{self.viz['ip_bins'][1]}.{self.viz['ip_bins'][2]}.{self.viz['ip_bins'][3]}", fill="#ecf0f1", font=("Consolas",10), tags=("anim",))
        y += 18
        self.canvas.create_text(pad_x, y, anchor="nw", text=f"Mask bits: {self.viz['mask_bins'][0]}.{self.viz['mask_bins'][1]}.{self.viz['mask_bins'][2]}.{self.viz['mask_bins'][3]}", fill="#ecf0f1", font=("Consolas",10), tags=("anim",))
        y += 18
        self.canvas.create_text(pad_x, y, anchor="nw", text=f"AND =>    {self.viz['network_bin']}", fill="#2ecc71", font=("Consolas",10,"bold"), tags=("anim",))
        self.canvas.after(self.speed_ms//2, self._step_broadcast)

    def _step_broadcast(self):
        pad_x = 20; y = 340
        self.canvas.create_text(pad_x, y, anchor="nw", text="Broadcast (host bits → 1):", fill="#ecf0f1", font=("Segoe UI",10,"bold"), tags=("anim",))
        y += 18
        host_mask_bin = dotted_bin_32(self.viz['host_mask_int'])
        self.canvas.create_text(pad_x, y, anchor="nw", text=f"Host mask (inverse): {host_mask_bin}", fill="#f39c12", font=("Consolas",10), tags=("anim",))
        y += 18
        self.canvas.create_text(pad_x, y, anchor="nw", text=f"OR => {self.viz['broadcast_bin']}", fill="#e67e22", font=("Consolas",10), tags=("anim",))
        y += 18
        self.canvas.create_text(pad_x, y, anchor="nw", text=f"Broadcast address: {self.viz['broadcast']}", fill="#ecf0f1", font=("Segoe UI",10,"bold"), tags=("anim",))
        self.canvas.after(self.speed_ms//2, self._step_summary)

    def _step_summary(self):
        pad_x = 20; y = 420
        self.canvas.create_rectangle(pad_x, y, pad_x+640, y+120, fill="#2c3e50", outline="#111", tags=("anim","summary"))
        sy = y+8
        lines = [
            f"Summary:",
            f"  Network: {self.viz['network']}/{self.viz['prefix']}",
            f"  Netmask: {self.viz['mask_dec']}",
            f"  Broadcast: {self.viz['broadcast']}",
            f"  Total addresses: {self.viz['total']}",
            f"  Usable hosts: {self.viz['usable']}",
            f"  First usable: {self.viz['first']}",
            f"  Last usable: {self.viz['last']}",
        ]
        for l in lines:
            self.canvas.create_text(pad_x+8, sy, anchor="nw", text=l, fill="#ecf0f1", font=("Segoe UI",10), tags=("anim",))
            sy += 14

# ---------- PDF export ----------
def export_to_pdf(filename, title, explanation_text, canvas_image_bytes=None):
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError("Install reportlab to export PDFs: pip install reportlab")
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1,12))
    # Explanation: split by double newline
    blocks = explanation_text.split('\n\n')
    for b in blocks:
        b_html = b.replace('\n', '<br/>')
        story.append(Paragraph(b_html, styles['BodyText']))
        story.append(Spacer(1,8))
    if canvas_image_bytes and PIL_AVAILABLE:
        try:
            img = Image.open(io.BytesIO(canvas_image_bytes))
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            rl_img = RLImage(buf, width=6.5*inch, preserveAspectRatio=True)
            story.insert(1, rl_img)
            story.insert(2, Spacer(1,12))
        except Exception:
            pass
    doc.build(story)

# ---------- Tutor window (grid-based responsive layout) ----------
def open_tutor_window(parent, simple_mode_var):
    win = tb.Toplevel()
    win.title("Subnetting Visual Tutor — UX")
    win.minsize(1100, 780)
    win.geometry("1200x820")
    try:
        win.eval('tk::PlaceWindow %s center' % win.winfo_toplevel())
    except Exception:
        pass

    # Configure grid: row0 = input (fixed), row1 = content (expands), row2 = bottom controls (fixed)
    win.grid_rowconfigure(0, weight=0)
    win.grid_rowconfigure(1, weight=1)
    win.grid_rowconfigure(2, weight=0)
    win.grid_columnconfigure(0, weight=1)

    # Input frame (row 0)
    input_frame = ttk.Frame(win, padding=8)
    input_frame.grid(row=0, column=0, sticky="ew")
    for c in range(4):
        input_frame.grid_columnconfigure(c, weight=1)
    ttk.Label(input_frame, text="Mode:").grid(row=0, column=0, sticky="w")
    mode_var = tk.StringVar(value="subnet_to_hosts")
    rb1 = ttk.Radiobutton(input_frame, text="Subnet → Hosts", variable=mode_var, value="subnet_to_hosts")
    rb2 = ttk.Radiobutton(input_frame, text="Hosts → Subnet", variable=mode_var, value="hosts_to_subnet")
    rb1.grid(row=0, column=1, sticky="w")
    rb2.grid(row=0, column=2, sticky="w")
    version_var = tk.IntVar(value=4)
    ttk.Radiobutton(input_frame, text="IPv4", variable=version_var, value=4).grid(row=0, column=3, sticky="e")
    ttk.Radiobutton(input_frame, text="IPv6", variable=version_var, value=6).grid(row=0, column=4, sticky="e")
    # inputs
    lbl_subnet = ttk.Label(input_frame, text="Subnet (e.g. 172.54.1.0/26):")
    entry_subnet = ttk.Entry(input_frame)
    lbl_hosts = ttk.Label(input_frame, text="Hosts (e.g. 50):")
    entry_hosts = ttk.Entry(input_frame)
    lbl_base = ttk.Label(input_frame, text="Optional base network:")
    entry_base = ttk.Entry(input_frame)

    def place_inputs(*_):
        # clear
        for w in (lbl_subnet, entry_subnet, lbl_hosts, entry_hosts, lbl_base, entry_base):
            try:
                w.grid_forget()
            except Exception:
                pass
        if mode_var.get() == "subnet_to_hosts":
            lbl_subnet.grid(row=1, column=0, sticky="w", pady=(6,0))
            entry_subnet.grid(row=1, column=1, columnspan=3, sticky="ew", pady=(6,0))
        else:
            lbl_hosts.grid(row=1, column=0, sticky="w", pady=(6,0))
            entry_hosts.grid(row=1, column=1, sticky="w", pady=(6,0))
            lbl_base.grid(row=1, column=2, sticky="w", pady=(6,0))
            entry_base.grid(row=1, column=3, sticky="ew", pady=(6,0))
    mode_var.trace_add("write", place_inputs)
    place_inputs()

    # Content (row 1) : Paned window (left canvas, right text)
    paned = ttk.PanedWindow(win, orient=tk.HORIZONTAL)
    paned.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
    left = ttk.Frame(paned)
    right = ttk.Frame(paned, width=420)
    paned.add(left, weight=3)
    paned.add(right, weight=1)

    # Canvas in left, with vertical scrollbar
    left.grid_rowconfigure(0, weight=1)
    left.grid_columnconfigure(0, weight=1)
    canvas_frame = ttk.Frame(left)
    canvas_frame.grid(row=0, column=0, sticky="nsew")
    canvas = tk.Canvas(canvas_frame, bg="#1e1e1e")
    canvas.grid(row=0, column=0, sticky="nsew")
    vscroll = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    vscroll.grid(row=0, column=1, sticky="ns")
    canvas.configure(yscrollcommand=vscroll.set)

    # text explanation in right with scrollbar
    right.grid_rowconfigure(0, weight=1)
    right.grid_columnconfigure(0, weight=1)
    explanation = tk.Text(right, wrap="word", font=("Segoe UI",10))
    explanation.grid(row=0, column=0, sticky="nsew", padx=(6,0))
    expl_scroll = ttk.Scrollbar(right, orient="vertical", command=explanation.yview)
    expl_scroll.grid(row=0, column=1, sticky="ns")
    explanation.configure(yscrollcommand=expl_scroll.set)

    # Bottom controls (row 2) anchored and always visible
    bottom = ttk.Frame(win, padding=8)
    bottom.grid(row=2, column=0, sticky="ew")
    bottom.grid_columnconfigure(0, weight=1)
    # left aligned buttons
    left_controls = ttk.Frame(bottom)
    left_controls.grid(row=0, column=0, sticky="w")
    run_btn = ttk.Button(left_controls, text="Show Steps (Visualize)")
    run_btn.grid(row=0, column=0, padx=6)
    static_btn = ttk.Button(left_controls, text="Show Static (No Animation)")
    static_btn.grid(row=0, column=1, padx=6)
    replay_btn = ttk.Button(left_controls, text="Replay")
    replay_btn.grid(row=0, column=2, padx=6)
    # right aligned controls
    right_controls = ttk.Frame(bottom)
    right_controls.grid(row=0, column=1, sticky="e")
    speed_label = ttk.Label(right_controls, text="Speed:")
    speed_label.grid(row=0, column=0, padx=(0,6))
    speed_combo = ttk.Combobox(right_controls, values=["slow","normal","fast"], state="readonly", width=8)
    speed_combo.set("normal")
    speed_combo.grid(row=0, column=1, padx=(0,10))
    # Simple English toggle (customtkinter switch)
    try:
        simple_switch = ctk.CTkSwitch(master=right_controls, text="Simple English", command=lambda: simple_mode_var.set(0 if simple_mode_var.get() else 1))
        if simple_mode_var.get():
            simple_switch.select()
        else:
            simple_switch.deselect()
        simple_switch.grid(row=0, column=2, padx=(0,12))
    except Exception:
        ttk.Checkbutton(right_controls, text="Simple English", variable=simple_mode_var).grid(row=0, column=2, padx=(0,12))
    export_btn = ttk.Button(right_controls, text="Export PDF")
    export_btn.grid(row=0, column=3, padx=(0,6))

    # animator holder
    animator = {"obj": None}

    # helper: clear canvas & explanation
    def clear_all():
        canvas.delete("all")
        explanation.delete("1.0", tk.END)
        canvas.configure(scrollregion=(0,0,0,0))

    # function to adjust canvas scroll region after drawings
    def update_canvas_region():
        canvas.update_idletasks()
        bbox = canvas.bbox("all")
        if bbox:
            canvas.configure(scrollregion=bbox)

    # function to show subnet steps (animated or static)
    def show_steps(animated=True):
        clear_all()
        simple = bool(simple_mode_var.get())
        spd = {'slow':1200,'normal':700,'fast':300}[speed_combo.get()]
        if mode_var.get() == "subnet_to_hosts":
            subnet = entry_subnet.get().strip()
            if not subnet:
                messagebox.showerror("Input required", "Please enter a subnet (e.g. 172.54.1.0/26).")
                return
            if version_var.get() == 4:
                try:
                    text, viz = ipv4_steps_verbose(subnet, simple_mode=simple)
                    explanation.insert("1.0", text)
                    update_canvas_region()
                    if animated:
                        anim = IPv4Animator(canvas, viz, explanation, speed_ms=spd)
                        animator['obj'] = anim
                        anim.run()
                    else:
                        # static draw
                        canvas.create_text(18,12, anchor="nw", text=f"Subnet: {subnet}", fill="#ecf0f1", font=("Segoe UI",12,"bold"))
                        # mask
                        draw_mask_x = 18; draw_mask_y = 40
                        per = (24+5)*8 + 12
                        box_x = draw_mask_x
                        for oct_bin in viz['mask_bins']:
                            draw_octet_bits(canvas, box_x, draw_mask_y, oct_bin, outline_net=True)
                            box_x += per
                        # IP
                        ip_y = draw_mask_y + 90
                        box_x = draw_mask_x
                        canvas.create_text(draw_mask_x, ip_y-20, anchor="nw", text=f"IP: {viz['ip_dec']}", fill="#ecf0f1")
                        for oct_bin in viz['ip_bins']:
                            draw_octet_bits(canvas, box_x, ip_y, oct_bin)
                            box_x += per
                        # summary
                        sum_y = ip_y + 160
                        canvas.create_rectangle(draw_mask_x, sum_y, draw_mask_x+640, sum_y+110, fill="#2c3e50", outline="#111")
                        sy = sum_y + 8
                        sum_lines = [
                            f"Network: {viz['network']}/{viz['prefix']}",
                            f"Netmask: {viz['mask_dec']}",
                            f"Broadcast: {viz['broadcast']}",
                            f"Total addresses: {viz['total']}",
                            f"Usable hosts: {viz['usable']}",
                            f"First usable: {viz['first']}",
                            f"Last usable: {viz['last']}",
                        ]
                        for l in sum_lines:
                            canvas.create_text(draw_mask_x+8, sy, anchor="nw", text=l, fill="#ecf0f1", font=("Segoe UI",10))
                            sy += 14
                        update_canvas_region()
                except Exception as e:
                    messagebox.showerror("Error", str(e))
            else:
                # IPv6 static
                try:
                    text, viz = ipv6_steps_verbose(subnet, simple_mode=simple)
                    explanation.insert("1.0", text)
                    canvas.create_text(18,12, anchor="nw", text=f"IPv6: {subnet}", fill="#ecf0f1", font=("Segoe UI",12,"bold"))
                    draw_hextet_groups(canvas, 18, 48, viz['groups'])
                    canvas.create_text(18, 220, anchor="nw", text="Hextets: " + " ".join(viz['hextets']), fill="#ecf0f1", font=("Consolas",10))
                    update_canvas_region()
                except Exception as e:
                    messagebox.showerror("Error", str(e))
        else:
            # Hosts -> Subnet
            hosts = entry_hosts.get().strip()
            if not hosts:
                messagebox.showerror("Input required", "Please enter number of hosts.")
                return
            if version_var.get() == 4:
                try:
                    out, res = hosts_to_ipv4_steps(hosts, simple_mode=bool(simple_mode_var.get()))
                    explanation.insert("1.0", out)
                    canvas.create_text(18,12, anchor="nw", text=f"Hosts -> Subnet (IPv4)", fill="#ecf0f1", font=("Segoe UI",12,"bold"))
                    if res:
                        canvas.create_text(18,40, anchor="nw", text=f"Result: /{res['prefix']}  Total: {res['total']}  Usable: {res['usable']}", fill="#2ecc71")
                        base = entry_base.get().strip()
                        if base:
                            try:
                                base_net = ipaddress.IPv4Network(base, strict=False)
                                subnets = list(base_net.subnets(new_prefix=res['prefix']))
                                if subnets:
                                    first = subnets[0]
                                    canvas.create_text(18,64, anchor="nw", text=f"Example inside {base}: {first.network_address}/{first.prefixlen}")
                            except Exception as e:
                                canvas.create_text(18,64, anchor="nw", text=f"Base parse error: {e}", fill="#e74c3c")
                    update_canvas_region()
                except Exception as e:
                    messagebox.showerror("Error", str(e))
            else:
                out, res = hosts_to_ipv6_steps(hosts, simple_mode=bool(simple_mode_var.get()))
                explanation.insert("1.0", out)
                if res:
                    canvas.create_text(18,12, anchor="nw", text=f"Result: /{res['prefix']}  Total: {res['total']}", fill="#2ecc71")
                update_canvas_region()

    # bind operations
    run_btn.config(command=lambda: show_steps(animated=True))
    static_btn.config(command=lambda: show_steps(animated=False))

    def replay():
        anim_obj = animator.get("obj")
        # our animator variable stored per show_steps; try to retrieve by scanning created anim object if present
        # For simplicity, if show_steps animated just stored in function scope, we recreate via running again
        show_steps(animated=True)

    replay_btn.config(command=replay)

    def export_pdf_action():
        txt = explanation.get("1.0", tk.END).strip()
        if not txt:
            messagebox.showinfo("Export", "Nothing to export. Generate steps first.")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF","*.pdf")])
        if not filename:
            return
        # attempt canvas snapshot via postscript + PIL if available
        img_bytes = None
        if PIL_AVAILABLE:
            try:
                ps = canvas.postscript(colormode='color')
                img = Image.open(io.BytesIO(ps.encode('utf-8')))
                buf = io.BytesIO()
                img.save(buf, format='PNG')
                img_bytes = buf.getvalue()
            except Exception:
                img_bytes = None
        try:
            export_to_pdf(filename, "Subnetting Steps", txt, canvas_image_bytes=img_bytes)
            messagebox.showinfo("Export", f"PDF saved to {filename}")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))

    export_btn.config(command=export_pdf_action)

# ---------- Main window (grid layout with anchored bottom controls) ----------
def main_app():
    style = tb.Style(theme="superhero")
    root = style.master
    root.title("Number Systems & Network Tutor (Final UX)")
    root.minsize(1000,700)
    root.geometry("1100x760")
    try:
        root.eval('tk::PlaceWindow %s center' % root.winfo_toplevel())
    except Exception:
        pass

    # configure root grid: row0 content (expand), row1 bottom controls (fixed)
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=0)
    root.grid_columnconfigure(0, weight=1)

    # notebook area (row 0)
    notebook = ttk.Notebook(root)
    notebook.grid(row=0, column=0, sticky="nsew", padx=12, pady=8)

    # bottom control bar (row 1) anchored
    bottom = ttk.Frame(root, padding=8)
    bottom.grid(row=1, column=0, sticky="ew")
    bottom.grid_columnconfigure(0, weight=1)
    left_btns = ttk.Frame(bottom)
    left_btns.grid(row=0, column=0, sticky="w")
    right_btns = ttk.Frame(bottom)
    right_btns.grid(row=0, column=1, sticky="e")

    # simple english toggle variable
    simple_mode_var = tk.IntVar(value=0)
    try:
        switch = ctk.CTkSwitch(master=left_btns, text="Simple English Mode", command=lambda: simple_mode_var.set(0 if simple_mode_var.get() else 1))
        switch.grid(row=0, column=0, padx=6)
    except Exception:
        ttk.Checkbutton(left_btns, text="Simple English Mode", variable=simple_mode_var).grid(row=0, column=0, padx=6)

    ttk.Button(right_btns, text="Open Subnet Tutor", bootstyle="info", command=lambda: open_tutor_window(root, simple_mode_var)).grid(row=0, column=0, padx=6)
    ttk.Button(right_btns, text="Apply Theme", command=lambda: tb.Style(theme="superhero")).grid(row=0, column=1, padx=6)

    # helper to create converter tabs with grid inside
    def make_tab(title, placeholder, convert_fn):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=title)
        # grid top (controls) and center (output)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        top = ttk.Frame(frame, padding=(8,8))
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(1, weight=1)
        ttk.Label(top, text=placeholder).grid(row=0, column=0, sticky="w")
        entry = ttk.Entry(top)
        entry.grid(row=0, column=1, sticky="ew", padx=6)
        convert_btn = ttk.Button(top, text="Convert")
        convert_btn.grid(row=0, column=2, padx=6)
        copy_btn = ttk.Button(top, text="Copy Result")
        copy_btn.grid(row=0, column=3, padx=6)
        output_frame = ttk.Frame(frame)
        output_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)
        txt = tk.Text(output_frame, wrap="word", font=("Consolas",11))
        txt.grid(row=0, column=0, sticky="nsew")
        vs = ttk.Scrollbar(output_frame, orient="vertical", command=txt.yview)
        vs.grid(row=0, column=1, sticky="ns")
        txt.configure(yscrollcommand=vs.set)

        def do_convert():
            v = entry.get().strip()
            txt.delete("1.0", tk.END)
            try:
                if title.startswith("Decimal"):
                    out = convert_fn(int(v))
                else:
                    out = convert_fn(v)
                txt.insert("1.0", out)
            except Exception as e:
                txt.insert("1.0", f"Error: {e}")

        def do_copy():
            s = txt.get("1.0", tk.END).strip()
            if s:
                root.clipboard_clear()
                root.clipboard_append(s)
                messagebox.showinfo("Copied", "Result copied to clipboard.")

        convert_btn.config(command=do_convert)
        copy_btn.config(command=do_copy)

    make_tab("Decimal → Binary", "Enter decimal:", decimal_to_binary_steps)
    make_tab("Decimal → Octal", "Enter decimal:", decimal_to_octal_steps)
    make_tab("Decimal → Hexadecimal", "Enter decimal:", decimal_to_hex_steps)
    make_tab("Binary → Decimal", "Enter binary:", binary_to_decimal_steps)
    make_tab("Octal → Decimal", "Enter octal:", octal_to_decimal_steps)
    make_tab("Hexadecimal → Decimal", "Enter hex:", hex_to_decimal_steps)

    root.mainloop()

if __name__ == "__main__":
    main_app()
