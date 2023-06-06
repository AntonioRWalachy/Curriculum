import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk # NEEDS PIP INSTALL
import json

from scoreboard_widget import Scoreboard_Widget
from pdf_reader import Pdf_Reader
from api import AnalysisAi

class Main:
    all_files_dir = []
    all_params = []
    final_scoreboard = []
    params_list = None
    files_list = None
    param_window = None

    pdfr = Pdf_Reader()
    analysis_ai = AnalysisAi()

    results_toplevel = None

    def __init__(self):
        self.main_window()

    def display_file(self, file_dirs):
        # VERIFICA SE O ARQUIVO É REPETIDO
        for file_dir in file_dirs:
            repeated = False
            for file in self.all_files_dir:
                if file == file_dir:
                    repeated = True
                    break
            
            if repeated == False:
                self.all_files_dir.append(file_dir)
                self.files_list.insert("end",file_dir)
    
    def open_files(self):
        # PESQUISA ARQUIVOS NO EXPLORER
        file = filedialog.askopenfilename(
            title='Selecionar arquivo PDF',
            filetypes=(
                ('Arquivo PDF', '*.pdf'),
            ),
            multiple=True
        )

        if len(file) > 0:
            self.display_file(file)
    
    def add_param_window(self):
        # NOVA JANELA
        if self.param_window:
            self.param_window.destroy()
        self.param_window = tk.Toplevel()
        self.param_window.title("Adicionar regra")

        # WIDGETS
        container = tk.Frame(self.param_window,padx=10,pady=10)
        container_title = tk.Label(container,text="Novo parâmetro de avaliação", font="Arial 15 bold")
        frame_weigth = tk.Frame(container)
        label_weight = tk.Label(frame_weigth, text="Peso: ", font="Arial 12 bold")
        entry_weight = tk.Entry(frame_weigth,width=10)
        frame_param = tk.Frame(container)
        label_param = tk.Label(frame_param,text="Descrição da regra", font="Arial 12 bold")
        entry_param = tk.Entry(frame_param)
        confirm_btn = tk.Button(container, text="Adicionar", bg="green",fg="white", font="Arial 12 bold", command=lambda : self.check_param(entry_weight.get(), entry_param.get()))

        # GRID
        container.grid(row=0,column=0)
        container_title.grid(row=0,column=0,pady=(0,15))
        frame_weigth.grid(row=1,column=0,sticky="we")
        label_weight.grid(row=0,column=0, sticky="w")
        entry_weight.grid(row=1,column=0)
        frame_param.grid(row=2,column=0,sticky="we")
        label_param.grid(row=0,column=0,sticky="w")
        entry_param.grid(row=1,column=0, sticky="we")
        confirm_btn.grid(row=3,column=0,pady=(30,0))

        # RESPONSIVO
        frame_param.columnconfigure(0,weight=1)
    
    def check_param(self, weight, param):
        try:
            weight = int(weight)
            self.param_window.destroy()
            self.display_param(param,weight)
        except:
            messagebox.showerror(title="Erro", message="O peso deve ser um número inteiro")

    def display_param(self, param, weight):
        # POR PECULIARIEDADES DA API, USAMOS "SOME" PARA POSITIVOS E "SUBTRAIA" PARA NEGATIVOS
        if weight > 0:
            self.params_list.insert("end", f"some {weight} pontos {param}") # EXIBE NA LISTBOX
            self.all_params.append(f"some {weight} pontos {param}") # ADICIONA NA LISTA
        else:
            self.params_list.insert("end", f"subtraia {weight} pontos {param}") # EXIBE NA LISTBOX
            self.all_params.append(f"subtraia {weight} pontos {param}") # ADICIONA NA LISTA

    def remove_file(self):
        # JANELA DE CONFIRMAÇÃO
        resp = messagebox.askquestion(title="Deseja excluir?", message="Deseja mesmo excluir este registro?")
        if resp == "yes":
            if self.files_list.curselection():
                removed = 0
                for item in self.files_list.curselection():
                    index = item - removed # RECALCULA PARA CADA ITEM REMOVIDO
                    del self.all_files_dir[index]
                    self.files_list.delete(index,index)
                    removed +=1

    def remove_param(self):
        # JANELA DE CONFIRMAÇÃO
        resp = messagebox.askquestion(title="Deseja excluir?", message="Deseja mesmo excluir este registro?")
        if resp == "yes":
            if self.params_list.curselection():
                removed = 0
                for item in self.params_list.curselection():
                    index = item - removed # RECALCULA PARA CADA ITEM REMOVIDO
                    del self.all_params[index]
                    self.params_list.delete(index,index)
                    removed +=1   

    def generate_analysis(self,api_key):
        resp = messagebox.askquestion(title="Deseja executar?", message="Este é um programa em fase de desenvolvimento. Ao executar esta ação, esteja ciente de que muitos tokens serão usados e, portanto, um alto custo será aplicado na sua conta openai. Se seu intuito é testar, recomendo adicionar apenas um ou dois arquivos e não mais que 10 parâmetros.")

        if resp == "yes":
            errors_count = 0
            accepted_requests = 0

            if len(self.all_files_dir) > 0 and len(self.all_params) > 0:
                self.final_scoreboard.clear()

                for file_dir in self.all_files_dir:
                    curriculum_score = 0
                    wrong_key = False

                    curriculum_text = self.pdfr.read_pdf(file_dir) # RETORNA O TEXTO DO PDF

                    # LÊ CADA PARÂMETRO E ENVIA JUNTO AO TEXTO PARA ANÁLISE
                    for param in self.all_params:
                        points = self.analysis_ai.analyse(curriculum_text,param,api_key)

                        if points[0] != False: # RESULTADO RETORNADO CORRETAMENTE
                            accepted_requests+=1
                            curriculum_score += int(points[0])
                        else:
                            if points[1] != False: # ERRO, GERALMENTE NA CONEXÃO/COMUNICAÇÃO COM A API
                                errors_count+=1
                            else: # ERRO DE CHAVE INEXISTENTE
                                wrong_key = True
                                break
                    
                    # CHAVE INEXISTENTE
                    if wrong_key == True:
                        messagebox.showerror(title="Chave API inexistente", message="Parece que sua API key está incorreta!")
                        break

                    # SALVA A PONTUAÇÃO DESTE CURRÍCULO PARA SER CONSULTADA POSTERIORMENTE
                    self.final_scoreboard.append({"file_dir":file_dir, "curriculum_score":curriculum_score})
            
                if accepted_requests + errors_count > 0:
                    # MARGEM DE ERRO PERMITIDA
                    if (errors_count * 100 / (accepted_requests + errors_count)) < 15:
                        self.show_results()
                    else:
                        messagebox.showerror(title="Limite de erros excedido", message="O resultado não pôde ser computado devido a uma grande quantidade de erros. Favor verificar: sua conexão com a internet; estabilidade da API; alterar o código se necessário.")
            else:
                # NENHUM ARQUIVO OU PARÂMETRO ADICIONADO
                messagebox.showerror(title="Erro",message="Você deve adicionar ao menos um arquivo e um parâmetro") 

    def show_results(self):
        file_found = False

        # SALVA O RESULTADO MAIS RECENTE EM UM ARQUIVO
        if len(self.final_scoreboard) > 0:
            try:
                with open("scoreboard.json",'w') as f:
                    json.dump(self.final_scoreboard, f)
                    f.close()
                file_found = True
            except:
                messagebox.showerror(title="erro",message="Houve um erro ao carregar o arquivo")
        else: # RECUPERA O RESULTADO PARA CONSULTA
            try:
                with open("scoreboard.json","r") as f:
                    self.final_scoreboard = json.load(f)
                    f.close()
                file_found = True
            except FileNotFoundError:
                messagebox.showerror(title="erro",message="Nenhum dado salvo")
            except:
                messagebox.showerror(title="erro",message="Houve um erro ao carregar o arquivo")
        
        if file_found:
            # WINDOW
            if self.results_toplevel:
                self.results_toplevel.destroy()
            self.results_toplevel = tk.Toplevel()
            self.results_toplevel.columnconfigure(0,weight=1)
            self.results_toplevel.rowconfigure(0,weight=1)
            self.results_toplevel.title("Resultados finais")
            self.results_toplevel.maxsize(1920,390) # EXIBE APENAS 10 ITEMS POR VEZ NA TELA
            self.results_toplevel.minsize(500,390)

            # ORDENA PELA PONTUAÇÃO
            self.final_scoreboard = sorted(self.final_scoreboard, key=lambda x:x['curriculum_score'], reverse=True)

            # POSIÇÃO DA SCROLLBAR
            scroll_index = tk.IntVar()

            # SCROLLBAR IMPROVISADA. O WIDGET PRÓPRIO DA SCROLLBAR NÃO FUNCIONA COM FRAMES
            scrollbar = tk.Scale(
                self.results_toplevel,
                showvalue=0,
                from_=0,
                to=((len(self.final_scoreboard) - 10) if (len(self.final_scoreboard) - 10) >= 9 else 0),
                command=lambda value: scroll_index.set(value) # ATUALIZA POSIÇÃO DA SCROLLBAR
            )

            items_container = tk.Frame(
                self.results_toplevel,
            )

            # CHAMA A FUNÇÃO DE ATUALIZAR VISUALIZAÇÃO SEMPRE QUE O BOTÃO DO MOUSE É SOLTO
            # CHAMAR ESTA FUNÇÃO NO CALLBACK DO SCALE CAUSARIA LAG
            scrollbar.bind("<ButtonRelease>", lambda event: self.load_items(scroll_index.get(), items_container))
            
            # GRID E RESPONSIVO
            scrollbar.grid(row=0,column=1, sticky="ns")
            items_container.grid(row=0,column=0,sticky="wens")
            items_container.columnconfigure(0,weight=1)

            # CARREGA OS ITEMS INICIAIS NA TELA
            self.load_items(scroll_index.get(), items_container)
    
    def load_items(self, scroll_index, parent_widget):
        scroll_index = int(scroll_index)
        
        for child in parent_widget.winfo_children():
            child.destroy()

        # CARREGA 10 WIDGETS POR VEZ
        # MAIS QUE ISSO PODE CAUSAR LAG AO REDIMENSIONAR A JANELA
        for i in range(scroll_index, (scroll_index+10)):
            if i < len(self.final_scoreboard):
                score = self.final_scoreboard[i]
                line = Scoreboard_Widget(
                    parent_widget,
                    score,
                    i+1
                )
                line.grid(row=i,column=0, sticky="we")
            else:
                break
        
    def main_window(self):
        root = tk.Tk()

        '''UI ELEMENTS'''

        add_conf = Image.open("images/add.png")
        add_conf = add_conf.resize((24,24), Image.Resampling.LANCZOS)
        add_img = ImageTk.PhotoImage(add_conf)

        remove_conf = Image.open("images/remove.png")
        remove_conf = remove_conf.resize((24,24), Image.Resampling.LANCZOS)
        remove_img = ImageTk.PhotoImage(remove_conf)

        play_conf = Image.open("images/play.png")
        play_conf = play_conf.resize((24,24), Image.Resampling.LANCZOS)
        play_img = ImageTk.PhotoImage(play_conf)

        podium_conf = Image.open("images/podium.png")
        podium_conf = podium_conf.resize((24,24), Image.Resampling.LANCZOS)
        podium_img = ImageTk.PhotoImage(podium_conf)

        '''WINDOW'''

        root.title("Análise de Currículos")
        width, height = 500,500
        offset_x = int(root.winfo_screenwidth() / 2 - width / 2) # POSIÇÃO HORIZONTAL CENTRALIZADA DA JANELA
        offset_y = int(root.winfo_screenheight() / 2 - height / 2) # POSIÇÃO VERTICAL CENTRALIZADA DA JANELA
        root.geometry(f"{width}x{height}+{offset_x}+{offset_y}")
        root.minsize(width,height)

        '''WIDGETS'''

        # SUA API KEY
        frame_api = tk.Frame(root, padx=15,pady=15, bg="#424242")
        label_api = tk.Label(frame_api, text="Sua API key da openai:", bg=frame_api['bg'], font="Arial 12 bold", fg="white")
        entry_api = tk.Entry(frame_api, font="Arial 12")

        # BOTÕES DE CIMA
        frame_options = tk.Frame(root, padx=10,pady=10,bd=4,relief="raised",bg="lightgrey")
        add_file_btn = tk.Button(
            frame_options,
            text="arquivo",
            image=add_img,
            compound="left",
            font="Arial 12 bold",
            padx=5,
            bg="grey",
            command = self.open_files
        )
        remove_file_btn = tk.Button(
            frame_options,
            text="arquivo",
            image=remove_img,
            compound="left",
            font="Arial 12 bold",
            padx=5,
            bg="grey",
            command=self.remove_file
        )
        run_analysis_btn = tk.Button(
            frame_options,
            text="run",
            image=play_img,
            compound="left",
            font="Arial 12 bold",
            padx=5,
            bg="grey",
            command=lambda : self.generate_analysis(entry_api.get())
        )

        main = tk.Frame(root)

        # LISTA DE REGRAS
        params_container = tk.Frame(main,bd=4,relief="raised",bg="lightgrey")
        self.params_list = tk.Listbox(params_container,selectmode="multiple")

        # LISTA DE ARQUIVOS
        files_container = tk.Frame(main)
        self.files_list = tk.Listbox(files_container, selectmode="multiple")

        # BOTÕES DE BAIXO
        frame_bottom_options = tk.Frame(root, padx=10,pady=10,bd=4,relief="raised",bg="lightgrey")
        add_param_btn = tk.Button(
            frame_bottom_options,
            text="regra",
            image=add_img,
            compound="left",
            font="Arial 12 bold",
            padx=5,
            bg="grey",
            command=self.add_param_window
        )
        remove_param_btn = tk.Button(
            frame_bottom_options,
            text="regra",
            image=remove_img,
            compound="left",
            font="Arial 12 bold",
            padx=5,
            bg="grey",
            command=self.remove_param
        )
        show_scoreboard = tk.Button(
            frame_bottom_options,
            text="rank",
            image=podium_img,
            compound="left",
            font="Arial 12 bold",
            padx=5,
            bg="grey",
            command=self.show_results
        )

        '''GRID'''

        frame_api.grid(row=0,column=0,sticky="we")
        label_api.grid(row=0,column=0, sticky="w")
        entry_api.grid(row=1,column=0, sticky="we")
        frame_options.grid(row=1,column=0, sticky="we")
        add_file_btn.grid(row=0,column=1, sticky="e", padx=(0,5))
        remove_file_btn.grid(row=0,column=2, sticky="e")
        run_analysis_btn.grid(row=0,column=0, sticky="w")
        main.grid(row=2,column=0,sticky="wens")
        frame_bottom_options.grid(row=3,column=0, sticky="wes")
        add_param_btn.grid(row=0,column=0, sticky="w", padx=(0,5))
        remove_param_btn.grid(row=0,column=1, sticky="w")
        show_scoreboard.grid(row=0,column=2, sticky="e")
        params_container.grid(row=0,column=0,sticky="wens")
        files_container.grid(row=0,column=1,sticky="wens")
        self.params_list.grid(row=0,column=0,sticky="wens")
        self.files_list.grid(row=0,column=0,sticky="wens")

        '''RESPONSIVO'''

        root.columnconfigure(0,weight=1)
        frame_api.columnconfigure(0,weight=1)
        root.rowconfigure(2,weight=1)
        main.columnconfigure(0,weight=35)
        main.columnconfigure(1,weight=65)
        main.rowconfigure(0,weight=1)
        frame_options.columnconfigure(0,weight=1)
        params_container.columnconfigure(0,weight=1)
        params_container.rowconfigure(0,weight=1)
        files_container.columnconfigure(0,weight=1)
        files_container.rowconfigure(0,weight=1)
        frame_bottom_options.columnconfigure(2,weight=1)


        root.mainloop()

if __name__ == "__main__":
    main = Main()
