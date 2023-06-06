import tkinter as tk
import subprocess, os, platform

class Scoreboard_Widget(tk.Frame):
    def open_file(self, file_dir):
        # ABRE O ARQUIVO NO APLICATIVO PADRÃO DO SISTEMA
        if platform.system() == 'Darwin': # macOS
            subprocess.call(('open', file_dir))
        elif platform.system() == 'Windows': # Windows
            os.startfile(file_dir)
        else: # linux variants
            subprocess.call(('xdg-open', file_dir))

    def __init__(self,parent, score, position):
        super().__init__(parent)

        open_file_img = tk.PhotoImage(file='images/redirect24x24.png')
        self['bd'] = 4
        self['relief'] = "raised"
        self['bg'] = "black"

        # WIDGETS
        label_position = tk.Label(
            self,
            text=position,
            font="Arial 12 bold",
            bd=1,
            relief="solid",
            padx=15,
            pady=5
        )
        label_filedir = tk.Label(
            self,
            text=score['file_dir'],
        )
        label_score = tk.Label(
            self,
            text=score['curriculum_score'],
            font="Arial 12 bold",
            width=5
        )
        btn_open_file = tk.Button(
            self,
            image=open_file_img,
            command=lambda : self.open_file(score['file_dir'])
        )
        btn_open_file.image = open_file_img

        # GRID
        btn_open_file.grid(row=0,column=3,sticky="ens", padx=(1,0))
        label_position.grid(row=0,column=0,sticky="wns")
        label_filedir.grid(row=0,column=1,sticky="wens", padx=(1,0))
        label_score.grid(row=0,column=2,sticky="ens", padx=(1,0))
        
        # DESTACA OS PRIMEIROS COLOCADOS
        if position == 1:
            label_position['bg'] = "#ffe600"
        elif position == 2:
            label_position['bg'] = "#b7c1c7"
        elif position == 3:
            label_position['bg'] = "#ba6300"

        # RESPONSIVO
        self.columnconfigure(1,weight=1)
        self.rowconfigure(0,weight=1)