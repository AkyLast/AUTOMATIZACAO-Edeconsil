import pandas as pd
from numpy import ndarray

class Validation():
    def __init__(self, columns):
        self.columns = columns

    def search_columns(self, column: str = None, set = False, should_print = False):
        columns = {
            "Coluna1": 0,
            "Coluna2": 0,
            "Coluna3": 0,
            "VEÍCULO": 0, 
        }

        if should_print:
            return columns
        if isinstance(column, list) or isinstance(column, ndarray):  
            for column_idx in column:
                print(column_idx, "id")
                self.search_columns(column_idx, set = True)
        else:  
            if not set:  
                print(column, "atualizar")  
                return columns.get(column, 0)  
            else:  
                if columns.get(column, 0) == 1:
                    columns[column] = 0
                else:
                    columns[column] = 1
            
teste = Validation(["teste1", "teste2", "teste3"])
df = pd.DataFrame({
    "Coluna1": [],
    "Coluna2": [],
    "Coluna3": []
})
print(df.columns.values)
teste.search_columns(df.columns.values)