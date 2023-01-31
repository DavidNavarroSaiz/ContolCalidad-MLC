from fpdf import FPDF
import pandas as pd
import math
import numpy as np
import datetime
class PDF2(FPDF):

    def header(self):
        self.image('./resources/reporte_resultados.jpeg', x = 0, y = 0, w = 210, h = 297)
        

    def estimate_lines_needed(self, iter, col_width: float) -> int:
        """_summary_

        Args:
            iter (iterable): a row in your table
            col_width (float): cell width

        Returns:
            _type_: _description_
        """
        font_width_in_mm = (
            self.font_size_pt * 0.5 * 0.6
        )  # assumption: a letter is half his height in width, the 0.5 is the value you want to play with
        max_cell_text_len_header = max([len(str(col)) for col in iter])  # how long is the longest string?
        return math.ceil(max_cell_text_len_header * font_width_in_mm / col_width)

    def table(self, table: pd.DataFrame):
        """Add table to pdf

        Args:
            table (pd.DataFrame): a table to be added to the document
        """

        # one pt is ~0.35mm
        # font size is in pt

        index_width = 8
        col_width = (self.epw - index_width) / (table.shape[1])  # distribute content evenly across pdf

        lines_needed = self.estimate_lines_needed(table.columns, col_width)

        # empty cell to start
        self.multi_cell(
            w=index_width,
            h=self.font_size * lines_needed,
            txt="",
            border=0,
            ln=3,
            max_line_height=self.font_size,
        )
        
        # header
        self.set_font('arial', 'B', 10)
        for col in table.columns:
            self.multi_cell(
                col_width,
                self.font_size * lines_needed,
                col,
                border="BL",
                ln=1
                if col == table.columns[-1]
                else 3,   # if it is the last col, go to beginning of next line, otherwise continue
                max_line_height=self.font_size,
            )
            
        # table
        self.set_font('arial', '', 8)
        for index, row in table.iterrows():

            lines_needed = self.estimate_lines_needed(iter=row.to_list(), col_width=col_width)
            self.multi_cell(
                index_width, self.font_size * lines_needed, str(index), border="TBR", ln=3, max_line_height=self.font_size
            )
            for col in table.columns:
                self.multi_cell(
                    col_width,
                    self.font_size * lines_needed,
                    str(row[col]),
                    border="TBL",
                    ln=1 if col == table.columns[-1] else 3,
                    max_line_height=self.font_size,
                )
        self.ln(5)  # add a small gap after the table

    def lista_terapia_objetivos(self,x_init,y_init,df):
        self.set_xy(x_init, y_init)
        contador_obj = 1
        contador_ter  = 0
        terapias_lista = df.terapia.to_numpy()
        terapias_lista = np.unique(terapias_lista)

        for terapia in terapias_lista: 
            # if contador_ter > 1:
            #     self.add_page()
            self.set_font('arial', 'B', 11)
            self.cell(40, 20, 'Terapia '+str(contador_ter+1)+':'+str(terapia), 0, 2, 'L')
            dataframe_objetivos = df[df['terapia'] == terapias_lista[contador_ter]]
            lista_objetivos = dataframe_objetivos.values.tolist()
            for objetivos in lista_objetivos:
                self.set_font('arial', 'B', 10)
                self.cell(40, 10, 'Objetivo '+str(contador_obj)+':'+str(objetivos[1]), 0, 2, 'L')
                self.set_font('arial', '', 8)
                self.cell(40, 10, 'Objetivo General: '+str(objetivos[2]), 0, 2, 'L')
                self.cell(40, 10, 'Objetivo + 2: '+str(objetivos[3]), 0, 2, 'L')
                self.cell(40, 10, 'Objetivo + 1: '+str(objetivos[4]), 0, 2, 'L')
                self.cell(40, 10, 'Objetivo 0: '+str(objetivos[5]), 0, 2, 'L')
                self.cell(40, 10, 'Objetivo - 1: '+str(objetivos[6]), 0, 2, 'L')
                self.cell(40, 10, 'Objetivo - 2: '+str(objetivos[7]), 0, 2, 'L')
                contador_obj = contador_obj+ 1
            contador_ter = contador_ter + 1 
    
            
    

    


    