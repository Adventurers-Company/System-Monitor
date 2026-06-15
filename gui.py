# gui.py
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from datetime import datetime
from monitor import SystemMonitor
from logs import log_info

class MonitorGUI:
    def __init__(self):
        self.monitor = SystemMonitor()
        self.root = tk.Tk()
        self.root.title("System Monitor Pro - Gerenciador de Tarefas")
        self.root.geometry("1250x820")
        self.root.configure(bg="#1e1e1e")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Dark Theme
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(".", background="#1e1e1e", foreground="#e0e0e0", fieldbackground="#2d2d2d")
        style.configure("TNotebook", background="#1e1e1e")
        style.configure("TNotebook.Tab", background="#2d2d2d", foreground="#e0e0e0", padding=[10, 4])
        style.map("TNotebook.Tab", background=[("selected", "#1e1e1e")])
        
        style.configure("Treeview", background="#2d2d2d", foreground="#e0e0e0", fieldbackground="#2d2d2d", rowheight=24)
        style.configure("Treeview.Heading", background="#383838", foreground="#ffffff", relief="flat", padding=5)
        style.map("Treeview.Heading", background=[('active', '#4a4a4a')])
        
        style.configure("TButton", background="#383838", foreground="#e0e0e0", padding=6)
        style.map("TButton", background=[('active', '#505050')])
        
        # Menu (sem opções que causam erro)
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Sair", command=self.on_close)
        menubar.add_cascade(label="Arquivo", menu=filemenu)
        self.root.config(menu=menubar)
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Visão Geral
        self.tab_overview = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_overview, text="Visão Geral")
        
        info_frame = tk.Frame(self.tab_overview, bg="#1e1e1e")
        info_frame.pack(fill=tk.X, pady=12, padx=15)
        self.lbl_time = tk.Label(info_frame, text="", bg="#1e1e1e", fg="#aaaaaa", font=("Segoe UI", 10))
        self.lbl_time.pack(side=tk.LEFT, padx=10)
        
        self.lbl_cpu = tk.Label(info_frame, text="CPU: --%", font=("Segoe UI", 17, "bold"), fg="#ff5555", bg="#1e1e1e")
        self.lbl_cpu.pack(side=tk.LEFT, padx=30)
        self.lbl_ram = tk.Label(info_frame, text="RAM: --%", font=("Segoe UI", 17, "bold"), fg="#4dabf7", bg="#1e1e1e")
        self.lbl_ram.pack(side=tk.LEFT, padx=30)
        self.lbl_disk = tk.Label(info_frame, text="Disco: --%", font=("Segoe UI", 17, "bold"), fg="#51cf66", bg="#1e1e1e")
        self.lbl_disk.pack(side=tk.LEFT, padx=30)
        self.lbl_net = tk.Label(info_frame, text="Rede: ↓0 ↑0 KB/s", font=("Segoe UI", 12), fg="#ffd43b", bg="#1e1e1e")
        self.lbl_net.pack(side=tk.LEFT, padx=30)
        
        # Gráficos
        self.fig, (self.ax_cpu, self.ax_ram) = plt.subplots(2, 1, figsize=(10.8, 5.6), facecolor="#1e1e1e")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab_overview)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        self.cpu_hist = [0] * 60
        self.ram_hist = [0] * 60
        self.ani = animation.FuncAnimation(self.fig, self.update_graphs, interval=1000, cache_frame_data=False)
        
        # Processos
        self.tab_proc = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_proc, text="Processos")
        
        ctrl_frame = tk.Frame(self.tab_proc, bg="#1e1e1e")
        ctrl_frame.pack(fill=tk.X, padx=15, pady=8)
        tk.Label(ctrl_frame, text="Filtrar:", bg="#1e1e1e", fg="#e0e0e0").pack(side=tk.LEFT)
        self.filter_var = tk.StringVar()
        self.filter_entry = tk.Entry(ctrl_frame, textvariable=self.filter_var, width=45, bg="#2d2d2d", fg="#e0e0e0", insertbackground="white")
        self.filter_entry.pack(side=tk.LEFT, padx=8)
        self.filter_entry.bind("<KeyRelease>", lambda e: self.refresh_processes())
        
        tk.Button(ctrl_frame, text="Atualizar", command=self.refresh_processes, bg="#383838", fg="white", relief="flat").pack(side=tk.RIGHT, padx=4)
        tk.Button(ctrl_frame, text="Finalizar Processo", command=self.kill_selected, bg="#e03131", fg="white", relief="flat").pack(side=tk.RIGHT, padx=4)
        
        cols = ("PID", "Nome", "CPU %", "MEM %", "Threads", "Status")
        self.tree = ttk.Treeview(self.tab_proc, columns=cols, show="headings", height=23)
        widths = [75, 390, 95, 95, 85, 110]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c))
            self.tree.column(col, width=w, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        self.sort_reverse = {}
        self.update_info()
        self.refresh_processes()
        log_info("System Monitor Pro iniciado")
        self.root.mainloop()
    
    def update_info(self):
        cpu = self.monitor.get_cpu()
        ram = self.monitor.get_ram()
        disk = self.monitor.get_disk()
        net = self.monitor.get_network()
        self.lbl_time.config(text=f"Atualizado: {datetime.now().strftime('%H:%M:%S')}")
        self.lbl_cpu.config(text=f"CPU: {cpu:.1f}%")
        self.lbl_ram.config(text=f"RAM: {ram['percent']}% ({ram['used']}/{ram['total']} MB)")
        self.lbl_disk.config(text=f"Disco: {disk['percent']}% ({disk['used']}/{disk['total']} GB)")
        self.lbl_net.config(text=f"Rede: ↓{net['recv']} ↑{net['sent']} KB/s")
        self.root.after(900, self.update_info)
    
    def update_graphs(self, frame):
        cpu = self.monitor.get_cpu()
        ram = self.monitor.get_ram()['percent']
        self.cpu_hist.pop(0); self.cpu_hist.append(cpu)
        self.ram_hist.pop(0); self.ram_hist.append(ram)
        
        self.ax_cpu.clear()
        self.ax_cpu.plot(self.cpu_hist, color="#ff5555", lw=2.5)
        self.ax_cpu.set_ylim(0, 100)
        self.ax_cpu.set_title("CPU (%)", color="#e0e0e0")
        self.ax_cpu.grid(True, alpha=0.3)
        self.ax_cpu.set_facecolor("#252525")
        
        self.ax_ram.clear()
        self.ax_ram.plot(self.ram_hist, color="#4dabf7", lw=2.5)
        self.ax_ram.set_ylim(0, 100)
        self.ax_ram.set_title("RAM (%)", color="#e0e0e0")
        self.ax_ram.grid(True, alpha=0.3)
        self.ax_ram.set_facecolor("#252525")
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def refresh_processes(self, *args):
        filter_text = self.filter_var.get().lower().strip()
        for i in self.tree.get_children():
            self.tree.delete(i)
        procs = self.monitor.get_all_processes(300)
        for p in procs:
            if filter_text and filter_text not in p['name'].lower():
                continue
            self.tree.insert("", "end", values=(p['pid'], p['name'], p['cpu'], p['mem'], p['threads'], p['status']))
    
    def sort_column(self, col):
        self.sort_reverse[col] = not self.sort_reverse.get(col, False)
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        reverse = self.sort_reverse[col]
        try:
            data.sort(reverse=reverse, key=lambda x: float(x[0]) if col in ["CPU %", "MEM %"] else x[0].lower())
        except:
            data.sort(reverse=reverse, key=lambda x: x[0].lower())
        for index, (_, child) in enumerate(data):
            self.tree.move(child, '', index)
    
    def kill_selected(self):
        sel = self.tree.selection()
        if not sel: return
        pid = int(self.tree.item(sel[0])['values'][0])
        if messagebox.askyesno("Confirmar", f"Finalizar PID {pid}?", icon="warning"):
            if self.monitor.kill_process(pid):
                self.refresh_processes()
    
    def on_close(self):
        if messagebox.askokcancel("Sair", "Fechar System Monitor Pro?"):
            log_info("System Monitor Pro finalizado")
            self.root.destroy()